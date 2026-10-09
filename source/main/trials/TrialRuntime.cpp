// SPDX-License-Identifier: GPL-3.0-or-later
#include "TrialRuntime.h"
#include "Actor.h"
#include "ActorManager.h"
#include <cassert>
#include "GameContext.h"
#include "Terrain.h"
#include "Application.h"
#include "SimConstants.h"
#include <rapidjson/document.h>
#include <cstdio>
#include <cstdlib>
#include <algorithm>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <sstream>
#ifdef _WIN32
#include <io.h>
#include <share.h>
#else
#include <unistd.h>
#endif

namespace RoR { namespace Trials {
namespace {
void U32(std::vector<unsigned char>& out, std::uint32_t n) { for(int i=0;i<4;++i) out.push_back(static_cast<unsigned char>(n>>(8*i))); }
void U64(std::vector<unsigned char>& out, std::uint64_t n) { for(int i=0;i<8;++i) out.push_back(static_cast<unsigned char>(n>>(8*i))); }
void Double(std::vector<unsigned char>& out, double n) { std::uint64_t bits; std::memcpy(&bits,&n,8); U64(out,bits); }
void Vector(std::vector<unsigned char>& out, Vec v) { Double(out,v.x); Double(out,v.y); Double(out,v.z); }
void Encode(std::vector<unsigned char>& out, const Record& r)
{
    const auto initial=out.size();
    U64(out,r.tick); U32(out,r.actor); U32(out,r.nodes); U32(out,r.phase); U32(out,r.flags);
    Double(out,r.dt); Double(out,r.mass); Vector(out,r.center); Vector(out,r.momentum);
    Vector(out,r.force); Vector(out,r.contact_force);
    Double(out,r.kinetic_before); Double(out,r.kinetic); Double(out,r.work);
    Vector(out,r.momentum_residual); Double(out,r.work_residual);
    Double(out,r.peak_node_force); Double(out,r.gravity); Double(out,r.density); Vector(out,r.wind);
    for(const auto& c:r.channels){Vector(out,c.force);Double(out,c.work);Vector(out,c.generated);}
    for(double v:{r.gravity_before,r.gravity_after,r.elastic_before,r.elastic_after,r.mechanical_residual,r.nonconservative_work,
        r.injection_kinetic,r.mutation_kinetic,r.wind_work,r.relative_drag_work,r.unattributed_l1,r.attribution_residual_l1,
        r.rest_storage_port,r.removed_storage_port,r.peak_beam_stress,r.physics_cpu_us})Double(out,v);
    Vector(out,r.injection_impulse);Vector(out,r.fixed_force);Vector(out,r.mutation_impulse);
    U32(out,r.plastic_events);U32(out,r.break_events);U32(out,r.unclosed_beams);U32(out,r.prepared_nodes);
    U64(out,r.consumed_from_tick);U64(out,r.generated_tick);U32(out,r.event_count);U32(out,r.event_dropped);
    for(const auto& e:r.events){
        U32(out,e.beam);U32(out,e.kind);
        for(double v:{e.length,e.oldRest,e.newRest,e.oldK,e.newK,e.oldStrength,e.newStrength,e.oldStorage,e.newStorage,e.stress})Double(out,v);
    }
    assert(out.size()-initial==RecordBytes);
}
std::string JsonVector(Vec v)
{
    std::ostringstream out; out<<std::setprecision(17)<<"["<<v.x<<","<<v.y<<","<<v.z<<"]"; return out.str();
}
bool Sync(FILE* file)
{
    if(std::fflush(file)!=0) return false;
#ifdef _WIN32
    return _commit(_fileno(file))==0;
#else
    return fsync(fileno(file))==0;
#endif
}
}

Runtime& Runtime::Get() { static Runtime runtime; return runtime; }
Runtime::Runtime()
{
    const char* dir=std::getenv("ROR_TRIAL_ARCHIVE");
    if(!dir || !*dir) return;
    m_root=dir;
    std::ifstream stream(m_root+"/native-config.json");
    const std::string text((std::istreambuf_iterator<char>(stream)),std::istreambuf_iterator<char>());
    rapidjson::Document doc; doc.Parse(text.c_str());
    if(doc.HasParseError() || !doc.IsObject()) return;
    auto number=[&](const char* key,double fallback) { return doc.HasMember(key)&&doc[key].IsNumber()?doc[key].GetDouble():fallback; };
    if(number("schema",0)!=1) return;
    if(doc.HasMember("scenario")&&doc["scenario"].IsString())m_scenario=doc["scenario"].GetString();
    if(m_scenario!="coast-v1"&&m_scenario!="freefall-v1"&&m_scenario!="spring-v1"&&m_scenario!="damper-v1")return;
    m_accounting=!doc.HasMember("accounting")||!doc["accounting"].IsBool()||doc["accounting"].GetBool();
    if(doc.HasMember("observation")&&doc["observation"].IsString()){
        const std::string mode=doc["observation"].GetString();
        if(mode!="full"&&mode!="off")return;
        m_observe=mode!="off";
    }
    m_probe=doc.HasMember("performanceProbe")&&doc["performanceProbe"].IsBool()&&doc["performanceProbe"].GetBool();
    if(!m_observe&&!m_probe)return; // off runs require the explicitly declared control probe
    m_speed=number("launchSpeedMps",0); m_duration=number("durationSeconds",12);
    m_settle=number("settleSeconds",3); m_gravity=number("gravity",-9.81); m_density=number("density",1.225);
    m_wind=Vec(number("windX",0),number("windY",0),number("windZ",0));
    if(!std::isfinite(m_speed) || m_speed<0 || m_speed>20 || !std::isfinite(m_duration) || m_duration<0.1 || m_duration>(IsFixture()?5:120) ||
       !std::isfinite(m_settle) || m_settle<(IsFixture()?0:2) || m_settle>30 || !std::isfinite(m_gravity) || m_gravity>0 || (m_gravity==0&&m_scenario=="coast-v1") || m_gravity < -30 ||
       !std::isfinite(m_density) || m_density<=0 || m_density>3 || !std::isfinite(m_wind.Norm()) || m_wind.Norm()>30) return;
    if(m_observe)m_queue.resize(32768); // bounded 65 MiB of records, one physics producer
    if(m_probe)m_probe_queue.resize(65536); // 8 MiB bounded probe, shared by both modes
    m_enabled=true;
    std::ofstream hello(m_root+"/handshake.json");
    hello<<"{\"schema\":1,\"observer\":\"accounting-v2\",\"capture\":\"crc32-binary-v2\","
          "\"coverage\":\"phase/node channels; linear storage subset; explicit unclosed terms\","
          "\"observation\":\""<<(m_observe?"full":"off")<<"\",\"performanceProbe\":"<<(m_probe?"true":"false")<<",\"cohort\":\"movable nodes\",\"dt\":"<<std::setprecision(17)<<static_cast<double>(PHYSICS_DT)<<"}\n";
    hello.close();
    if(m_observe)m_writer=std::thread(&Runtime::Writer,this);
    if(m_probe)m_probe_writer=std::thread(&Runtime::ProbeWriter,this);
    Event("worker-ready");
}
Runtime::~Runtime() { Stop(); }
void Runtime::Stop()
{
    if(m_closed) return;
    m_closed=true; m_stop.store(true,std::memory_order_release);
    if(m_writer.joinable()) m_writer.join();
    if(m_probe_writer.joinable())m_probe_writer.join();
    if(!m_observe){
        std::ofstream health(m_root+"/capture-health.json");
        health<<std::setprecision(17)<<"{\"tick\":"<<m_tick<<",\"timeSeconds\":"<<m_tick*static_cast<double>(PHYSICS_DT)
            <<",\"released\":"<<(m_released?"true":"false")<<",\"produced\":"<<m_probe_head.load()+m_probe_dropped.load()
            <<",\"enqueued\":"<<m_probe_head.load()<<",\"durable\":"<<m_probe_written.load()<<",\"dropped\":"<<m_probe_dropped.load()
            <<",\"ioError\":"<<(m_probe_error.load()?"true":"false")<<",\"closed\":true}\n";
    }
}
void Runtime::Event(const std::string& name,std::uint64_t sequence)
{
    std::ofstream out(m_root+"/native-events.jsonl",std::ios::app);
    out<<"{\"event\":\""<<name<<"\",\"tick\":"<<m_tick<<",\"sequence\":"<<sequence<<"}\n";
}
void Runtime::Poll(ActorManager& manager)
{
    if(!m_enabled || m_closed) return;
    for(ActorPtr& actor:manager.GetActors())PrepareActor(*actor.GetRef());
    const auto now=std::chrono::steady_clock::now();
    if(now-m_poll<std::chrono::milliseconds(100)) return;
    m_poll=now;
    manager.SetTrucksForcedAwake(true);
    std::ifstream input(m_root+"/command.json");
    std::string text((std::istreambuf_iterator<char>(input)),std::istreambuf_iterator<char>());
    rapidjson::Document doc; doc.Parse(text.c_str());
    if(!doc.HasParseError() && doc.IsObject() && doc.HasMember("sequence") && doc["sequence"].IsUint64() &&
       doc.HasMember("operation") && doc["operation"].IsString() && doc["sequence"].GetUint64()>m_last_command)
    {
        m_last_command=doc["sequence"].GetUint64();
        const std::string op=doc["operation"].GetString();
        bool valid=true;
        if(op=="pause") manager.SetSimulationPaused(true);
        else if(op=="resume") manager.SetSimulationPaused(false);
        else if(op=="cancel") App::GetGameContext()->PushMessage(Message(MSG_APP_SHUTDOWN_REQUESTED));
        else valid=false;
        Event(valid?op:"command-rejected",m_last_command);
        std::ofstream ack(m_root+"/ack.json");
        ack<<"{\"sequence\":"<<m_last_command<<",\"appliedTick\":"<<m_tick<<",\"applied\":"<<(valid?"true":"false")<<"}\n";
    }
    std::ofstream health(m_root+"/worker-status.json");
    health<<std::setprecision(17)<<"{\"tick\":"<<m_tick<<",\"timeSeconds\":"<<m_tick*static_cast<double>(PHYSICS_DT)
        <<",\"paused\":"<<(manager.IsSimulationPaused()?"true":"false")<<",\"released\":"<<(m_released?"true":"false")
        <<",\"produced\":"<<(m_observe?m_head.load()+m_dropped.load():m_probe_head.load()+m_probe_dropped.load())<<",\"enqueued\":"<<(m_observe?m_head.load():m_probe_head.load())
        <<",\"durable\":"<<(m_observe?m_written.load():m_probe_written.load())<<",\"dropped\":"<<(m_observe?m_dropped.load():m_probe_dropped.load())
        <<",\"ioError\":"<<((m_io_error.load()||m_probe_error.load())?"true":"false")<<"}\n";
    // Wall time is owned by the coordinator. This native completion uses physics ticks.
    if(m_released && m_tick*static_cast<double>(PHYSICS_DT)>=m_settle+m_duration)
        App::GetGameContext()->PushMessage(Message(MSG_APP_SHUTDOWN_REQUESTED));
}
void Runtime::BeginStep(Actor& actor)
{
    auto& ledger=actor.ar_trial_ledger;
    ledger.enabled=m_enabled && m_observe && !m_closed && Matches(actor) && ledger.nodes.size()==static_cast<std::size_t>(actor.ar_num_nodes);
    if(!m_enabled || m_closed || !Matches(actor) || m_ready_actor.load()!=actor.ar_instance_id || actor.ar_num_nodes<=0 || (m_observe&&!ledger.enabled)){ledger.enabled=false;return;}
    int expected=-1;
    m_pilot_actor.compare_exchange_strong(expected,actor.ar_instance_id);
    if(m_pilot_actor.load()!=actor.ar_instance_id)
    {
        ledger.enabled=false; m_scope_violation=true; return;
    }
    m_step_started=std::chrono::steady_clock::now();
    ++m_tick; // supported measurement cohort: exactly one pilot actor
    if(App::GetGameContext()->GetTerrain())
        App::GetGameContext()->GetTerrain()->setGravity(static_cast<float>(m_gravity));
    const bool was_released = m_released;
    m_initializing=false;
    double injection=0;Vec injected_p;
    if(!m_released && m_tick*static_cast<double>(PHYSICS_DT)>=m_settle)
    {
        for(int n=0;n<actor.ar_num_nodes;++n)if(!actor.ar_nodes[n].nd_immovable)
        {
            const auto& v=actor.ar_nodes[n].Velocity;const double mass=actor.ar_nodes[n].mass;
            injection-=0.5*mass*v.squaredLength();injected_p+=Vec(v.x,v.y,v.z)*(-mass);
        }
        if(IsFixture())InitializeFixture(actor);
        else
        {
        Ogre::Vector3 direction=actor.getDirection(); direction.y=0;
        if(direction.squaredLength()>1e-8f) direction.normalise(); else direction=Ogre::Vector3::UNIT_X;
        const Ogre::Vector3 velocity=direction*static_cast<float>(m_speed);
        for(int i=0;i<actor.ar_num_nodes;++i)
            if(!actor.ar_nodes[i].nd_immovable) actor.ar_nodes[i].Velocity=velocity;
        for(int w=0;w<actor.ar_num_wheels;++w)
        {
            wheel_t& wheel=actor.ar_wheels[w];
            if(wheel.wh_radius<=0 || !wheel.wh_axis_node_0 || !wheel.wh_axis_node_1) continue;
            const Ogre::Vector3 center=(wheel.wh_axis_node_0->AbsPosition+wheel.wh_axis_node_1->AbsPosition)*0.5f;
            Ogre::Vector3 axis=wheel.wh_axis_node_1->AbsPosition-wheel.wh_axis_node_0->AbsPosition;
            if(axis.squaredLength()<1e-8f) continue;
            axis.normalise();
            const Ogre::Vector3 ideal=Ogre::Vector3::UNIT_Y.crossProduct(velocity)/wheel.wh_radius;
            const Ogre::Vector3 omega=axis*axis.dotProduct(ideal);
            for(int n=0;n<wheel.wh_num_nodes;++n)
                wheel.wh_nodes[n]->Velocity=velocity+omega.crossProduct(wheel.wh_nodes[n]->AbsPosition-center);
            for(int n=0;n<wheel.wh_num_rim_nodes;++n)
                wheel.wh_rim_nodes[n]->Velocity=velocity+omega.crossProduct(wheel.wh_rim_nodes[n]->AbsPosition-center);
            wheel.wh_speed=static_cast<float>(m_speed); wheel.wh_avg_speed=static_cast<float>(m_speed);
        }
        }
        for(int n=0;n<actor.ar_num_nodes;++n)if(!actor.ar_nodes[n].nd_immovable)
        {
            const auto& v=actor.ar_nodes[n].Velocity;const double mass=actor.ar_nodes[n].mass;
            injection+=0.5*mass*v.squaredLength();injected_p+=Vec(v.x,v.y,v.z)*mass;
        }
        if(actor.ar_engine) { actor.ar_engine->stopEngine(); actor.ar_engine->setGear(0); }
        if(actor.getParkingBrake()) actor.parkingbrakeToggle();
        actor.ar_brake=0;
        m_released=true;
    }
    m_initializing=!was_released&&m_released;
    if(!m_observe)return;
    ledger.Begin(m_tick,static_cast<std::uint32_t>(actor.ar_instance_id),m_released?1:0,PHYSICS_DT);
    ledger.record.injection_kinetic=injection;ledger.record.injection_impulse=injected_p;
    Energy(actor,true);
    if(!m_accounting)ledger.record.flags|=4;
    if(m_scope_violation.load()) ledger.record.flags |= 1; // unsupported additional pilot actor
    if(!was_released && m_released) {
        ledger.record.flags |= 2; // initialization port boundary

    }
}
void Runtime::FinishStep(Actor& actor)
{
    if(!m_enabled || m_closed || !Matches(actor) || m_pilot_actor.load()!=actor.ar_instance_id)return;
    if(actor.ar_trial_ledger.enabled){
    Energy(actor,false);
    actor.ar_trial_ledger.record.physics_cpu_us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-m_step_started).count();
    Record record=actor.ar_trial_ledger.Finish();
    record.gravity=m_gravity; record.density=m_density; record.wind=m_wind;
    const auto head=m_head.load(std::memory_order_relaxed);
    if(head-m_tail.load(std::memory_order_acquire)>=m_queue.size()) { ++m_dropped; }
    else {m_queue[head % m_queue.size()]=record;m_head.store(head+1,std::memory_order_release);}
    }
    if(m_probe)Probe(actor);
}
void Runtime::Writer()
{
#ifdef _WIN32
    FILE* file=_fsopen((m_root+"/steps.rort").c_str(),"wb",_SH_DENYNO);
#else
    FILE* file=std::fopen((m_root+"/steps.rort").c_str(),"wb");
#endif
    if(!file) { m_io_error=true; return; }
    std::vector<unsigned char> header; U32(header,2); U32(header,RecordBytes);
    std::fwrite("RORTRIAL",1,8,file); std::fwrite(header.data(),1,header.size(),file);
    if(!Sync(file)) m_io_error=true;
    std::ofstream summaries(m_root+"/summaries.jsonl");
    std::ofstream transitions(m_root+"/beam-transitions.jsonl");
    std::vector<unsigned char> bytes; bytes.reserve(128*RecordBytes);
    std::uint64_t pending_durable=0;
    auto last_sync=std::chrono::steady_clock::now();
    double window_peak=0;
    while(!m_stop.load(std::memory_order_acquire) || m_tail.load()<m_head.load())
    {
        bytes.clear();
        auto tail=m_tail.load(std::memory_order_relaxed);
        auto head=m_head.load(std::memory_order_acquire);
        const auto count=std::min<std::uint64_t>(128,head-tail);
        if(count<128 && !m_stop.load()) { std::this_thread::sleep_for(std::chrono::milliseconds(5)); continue; }
        for(std::uint64_t i=0;i<count;++i)
        {
            const Record& r=m_queue[(tail+i)%m_queue.size()];
            Encode(bytes,r);
            window_peak=std::max(window_peak,r.peak_node_force);
            for(unsigned j=0;j<r.event_count;++j){
                const auto& e=r.events[j];
                transitions<<std::setprecision(17)<<"{\"tick\":"<<r.tick<<",\"beam\":"<<e.beam<<",\"kind\":"<<e.kind
                    <<",\"lengthM\":"<<e.length<<",\"oldRestM\":"<<e.oldRest<<",\"newRestM\":"<<e.newRest
                    <<",\"oldK\":"<<e.oldK<<",\"newK\":"<<e.newK<<",\"oldStrengthN\":"<<e.oldStrength
                    <<",\"newStrengthN\":"<<e.newStrength<<",\"oldStorageJ\":"<<e.oldStorage<<",\"newStorageJ\":"<<e.newStorage
                    <<",\"stressN\":"<<e.stress<<"}\n";
            }
            if(r.tick%10==0)
            {
                summaries<<std::setprecision(17)<<"{\"tick\":"<<r.tick<<",\"timeSeconds\":"<<r.tick*r.dt
                    <<",\"phase\":\""<<(r.phase?"coast":"settle")<<"\",\"nodes\":"<<r.nodes<<",\"massKg\":"<<r.mass
                    <<",\"centerM\":"<<JsonVector(r.center)<<",\"momentumKgMps\":"<<JsonVector(r.momentum)
                    <<",\"forceN\":"<<JsonVector(r.force)<<",\"contactForceN\":"<<JsonVector(r.contact_force)
                    <<",\"kineticJ\":"<<r.kinetic<<",\"workJ\":"<<r.work<<",\"workResidualJ\":"<<r.work_residual
                    <<",\"momentumResidualKgMps\":"<<JsonVector(r.momentum_residual)<<",\"peakNodeForceN\":"<<window_peak
                    <<",\"gravityMps2\":"<<r.gravity<<",\"densityKgM3\":"<<r.density<<",\"windMps\":"<<JsonVector(r.wind)
                    <<",\"flags\":"<<r.flags<<",\"dropped\":"<<m_dropped.load()
                    <<",\"scenario\":\""<<m_scenario<<"\",\"gravityPotentialJ\":"<<r.gravity_after<<",\"linearElasticJ\":"<<r.elastic_after
                    <<",\"mechanicalResidualJ\":"<<r.mechanical_residual<<",\"nonconservativeWorkJ\":"<<r.nonconservative_work
                    <<",\"injectionKineticJ\":"<<r.injection_kinetic<<",\"mutationKineticJ\":"<<r.mutation_kinetic
                    <<",\"windWorkJ\":"<<r.wind_work<<",\"relativeDragWorkJ\":"<<r.relative_drag_work
                    <<",\"unattributedNodeForceL1N\":"<<r.unattributed_l1<<",\"attributionResidualL1N\":"<<r.attribution_residual_l1
                    <<",\"restStoragePortJ\":"<<r.rest_storage_port<<",\"removedStoragePortJ\":"<<r.removed_storage_port
                    <<",\"peakBeamStressN\":"<<r.peak_beam_stress<<",\"physicsStepElapsedUs\":"<<r.physics_cpu_us
                    <<",\"unclosedBeams\":"<<r.unclosed_beams<<",\"linearBeamParameterEvents\":"<<r.plastic_events<<",\"breakEvents\":"<<r.break_events
                    <<",\"consumedFromTick\":"<<r.consumed_from_tick<<",\"generatedTick\":"<<r.generated_tick<<",\"channels\":{";
                for(int c=0;c<ChannelCount;++c){
                    if(c)summaries<<",";
                    const auto& v=r.channels[c];
                    summaries<<"\""<<ChannelName(c)<<"\":{\"forceN\":"<<JsonVector(v.force)<<",\"workJ\":"<<v.work
                        <<",\"generatedN\":"<<JsonVector(v.generated)<<"}";
                }
                summaries<<"}}\n";
                window_peak=0;
            }
        }
        if(count)
        {
            std::vector<unsigned char> block; U32(block,static_cast<std::uint32_t>(count));
            U32(block,static_cast<std::uint32_t>(bytes.size())); U32(block,Crc32(bytes.data(),bytes.size()));
            bool ok=std::fwrite("DATA",1,4,file)==4 && std::fwrite(block.data(),1,block.size(),file)==block.size()
                && std::fwrite(bytes.data(),1,bytes.size(),file)==bytes.size() && std::fwrite("DONE",1,4,file)==4;
            if(!ok) m_io_error=true; else pending_durable+=count;
            const auto now=std::chrono::steady_clock::now();
            if(now-last_sync>=std::chrono::milliseconds(250) || m_stop.load())
            {
                if(Sync(file)) { m_written+=pending_durable; pending_durable=0; }
                else m_io_error=true;
                last_sync=now;
            }
            summaries.flush(); transitions.flush(); if(!summaries||!transitions) m_io_error=true;
            m_tail.store(tail+count,std::memory_order_release);
        }
        else std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    if(Sync(file)) m_written+=pending_durable; else m_io_error=true;
    std::vector<unsigned char> footer;
    U64(footer,m_written.load()); U64(footer,m_dropped.load()); U32(footer,m_io_error.load()?1:0);
    if(std::fwrite("END!",1,4,file)!=4 || std::fwrite(footer.data(),1,footer.size(),file)!=footer.size()) m_io_error=true;
    if(!Sync(file)) m_io_error=true;
    if(std::fclose(file)!=0) m_io_error=true;
    std::ofstream health(m_root+"/capture-health.json");
    health<<std::setprecision(17)<<"{\"tick\":"<<m_tick<<",\"timeSeconds\":"<<m_tick*static_cast<double>(PHYSICS_DT)<<",\"released\":"<<(m_released?"true":"false")<<",\"produced\":"<<(m_head.load()+m_dropped.load())<<",\"enqueued\":"<<m_head.load()
          <<",\"durable\":"<<m_written.load()<<",\"dropped\":"<<m_dropped.load()
          <<",\"ioError\":"<<(m_io_error.load()?"true":"false")<<",\"closed\":true}\n";
}
}} // namespace
