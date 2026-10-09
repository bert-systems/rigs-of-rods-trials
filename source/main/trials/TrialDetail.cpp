// SPDX-License-Identifier: GPL-3.0-or-later
#include "TrialDetail.h"
#include "Actor.h"
#include "SimConstants.h"
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <stdexcept>
#include <limits>
#ifdef _WIN32
#include <io.h>
#include <share.h>
#else
#include <unistd.h>
#endif
namespace RoR { namespace Trials {
namespace {
Vec V(Ogre::Vector3 v){return Vec(v.x,v.y,v.z);}
void Put(float* dst,Vec v){dst[0]=static_cast<float>(v.x);dst[1]=static_cast<float>(v.y);dst[2]=static_cast<float>(v.z);}
Vec Get(const float* f){return Vec(f[0],f[1],f[2]);}
bool Sync(FILE* f){if(std::fflush(f))return false;
#ifdef _WIN32
    return _commit(_fileno(f))==0;
#else
    return fsync(fileno(f))==0;
#endif
}
void U32(std::vector<unsigned char>& v,std::uint32_t x){for(int i=0;i<4;++i)v.push_back(static_cast<unsigned char>(x>>(8*i)));}
void U64(std::vector<unsigned char>& v,std::uint64_t x){for(int i=0;i<8;++i)v.push_back(static_cast<unsigned char>(x>>(8*i)));}
void Float(std::vector<unsigned char>& v,float x){std::uint32_t b;std::memcpy(&b,&x,4);U32(v,b);}
void Double(std::vector<unsigned char>& v,double x){std::uint64_t b;std::memcpy(&b,&x,8);U64(v,b);}
std::int64_t Position(FILE* f){
#ifdef _WIN32
    return _ftelli64(f);
#else
    return ftello(f);
#endif
}
bool Rollback(FILE* f,std::int64_t offset){
    std::clearerr(f);std::fflush(f);std::clearerr(f);
#ifdef _WIN32
    return _chsize_s(_fileno(f),offset)==0&&_fseeki64(f,offset,SEEK_SET)==0;
#else
    return ftruncate(fileno(f),offset)==0&&fseeko(f,offset,SEEK_SET)==0;
#endif
}
void Encode(std::vector<unsigned char>& v,const unsigned char* frame){
    // This profile explicitly supports little-endian IEEE Windows x64 only.
    // Layout assertions fix every record, with initialized reserved fields and no implicit padding.
    // Copy the defined wire representation in bulk instead of 4 byte pushes per float.
    const auto& h=*reinterpret_cast<const DetailHeader*>(frame);
    v.resize(128+h.nodes*256+h.beams*112+h.contacts*104);
    std::memcpy(v.data(),frame,v.size());
}
}
Detail::Detail(const std::string& root,const std::string& fault,int nodes,int beams,int barrier,Vec origin,Vec direction):
    m_root(root),m_fault(fault),m_nodes(nodes),m_beams(beams),m_barrier(barrier),m_origin(origin),m_direction(direction)
{
    const std::uint32_t endian=1;
    if(*reinterpret_cast<const unsigned char*>(&endian)!=1||!std::numeric_limits<float>::is_iec559||!std::numeric_limits<double>::is_iec559)
        throw std::runtime_error("Detail profile requires little-endian IEEE floating point");
    // Realized pinned Daf: 176 nodes / 744 beams, 820,429,056 history bytes.
    // Resource profile v2: 1 GiB maximum prehistory, separate 3 GiB queue.
    // This full-window burst buffer accommodates measured archive-volume drain latency.
    m_stride=128+nodes*256+beams*112+(nodes*4+32)*104;
    if(m_stride*m_history_capacity>1024ull*1024*1024)throw std::runtime_error("Required detail prehistory exceeds profile budget");
    m_capacity=std::max<std::size_t>(2,3072ull*1024*1024/m_stride);
    m_scratch.resize(m_stride);m_queue.resize(m_capacity*m_stride);m_history.resize(m_history_capacity*m_stride);
    m_sink.owner=this;
    std::ofstream budget(m_root+"/detail-profile.json");
    budget<<"{\"schema\":1,\"profile\":\"whole-pilot-f32-v1\",\"nodes\":"<<nodes<<",\"beams\":"<<beams
        <<",\"contactCapacityPerTick\":"<<nodes*4+32<<",\"strideBytes\":"<<m_stride<<",\"preTicks\":4000,\"postTicks\":8000"
        <<",\"historyBytes\":"<<m_history.size()<<",\"queueBytes\":"<<m_queue.size()<<",\"queueFrames\":"<<m_capacity
        <<",\"fault\":\""<<fault<<"\",\"floatPrecision\":\"native float32; double cohort reduction/clock\"}\n";
    m_writer=std::thread(&Detail::Writer,this);
}
Detail::~Detail(){Stop();}
void Detail::Stop(){m_stop.store(true,std::memory_order_release);if(m_writer.joinable())m_writer.join();}
void Detail::Begin(Actor& a,std::uint64_t tick,bool released){
    auto& h=Header();h=DetailHeader{};h.tick=tick;h.dt=PHYSICS_DT;h.actor=a.ar_instance_id;h.nodes=m_nodes;h.beams=m_beams;h.phase=released?1:0;
    for(int i=0;i<m_beams;++i){const auto& b=a.ar_beams[i];auto& x=Beams()[i];x.beforeRest=b.L;x.beforeK=b.k;x.beforeStrength=b.strength;x.beforeActive=!b.bm_disabled&&!b.bm_broken;
        Put(x.generated1,Vec());Put(x.generated2,Vec());Put(x.elastic,Vec());Put(x.damping,Vec());}
}
ContactSink* Detail::Sink(int node){m_sink.node=node;return &m_sink;}
void ContactSink::Observe(std::uint32_t kind,std::uint32_t feature,Vec p,Vec n,Vec v,Vec b,Vec a,Vec raw,float mass,float depth,std::uint32_t material){
    owner->Contact(node,kind,feature,p,n,v,b,a,raw,mass,depth,material);
}
void Detail::Contact(std::uint32_t node,std::uint32_t kind,std::uint32_t feature,Vec p,Vec n,Vec v,Vec before,Vec after,Vec raw,float mass,float depth,std::uint32_t material){
    auto& h=Header();bool barrier=kind==2&&static_cast<int>(feature)==m_barrier;
    if(barrier&&(after-before).Norm()>0){++h.barrierContacts;if(!m_trigger.load())m_trigger=h.tick;}
    if(h.contacts>=static_cast<unsigned>(m_nodes*4+32)){++h.lost;++m_contact_lost;h.flags|=1;return;}
    auto& c=Contacts()[h.contacts++];c.node=node;c.kind=kind;c.feature=feature;c.barrier=barrier?1:0;
    Put(c.position,p);Put(c.normal,n);Put(c.velocity,v);Put(c.beforeForce,before);Put(c.applied,after-before);Put(c.rawForce,raw);c.mass=mass;c.penetration=depth;c.material=material;
}
void Detail::Node(Actor& a,int i,Vec beforeVelocity,Vec force){
    auto& x=Nodes()[i];const auto& n=a.ar_nodes[i];x.id=i;x.flags=n.nd_immovable?1:0;x.mass=n.mass;
    Put(x.position,V(n.AbsPosition));Put(x.beforeVelocity,beforeVelocity);Put(x.velocity,V(n.Velocity));Put(x.force,force);
    const auto& cache=a.ar_trial_ledger.nodes[i];
    for(int c=0;c<ChannelCount;++c)Put(x.channels[c],cache.force[c]);
}
void Detail::Beam(int i,Vec first,Vec second,Vec elastic,Vec damping){
    auto& b=Beams()[i];Put(b.generated1,first);Put(b.generated2,second);Put(b.elastic,elastic);Put(b.damping,damping);
}
void Detail::Finish(Actor& a){
    auto& h=Header();Vec center,velocity;double mass=0,front=-1e30;
    for(int i=0;i<m_nodes;++i){const auto& n=a.ar_nodes[i];front=std::max(front,(V(n.AbsPosition)-m_origin).Dot(m_direction));
        if(!n.nd_immovable){mass+=n.mass;center+=V(n.AbsPosition)*n.mass;velocity+=V(n.Velocity)*n.mass;h.kinetic+=.5*n.mass*V(n.Velocity).Dot(V(n.Velocity));}}
    if(mass>0){center=center*(1/mass);velocity=velocity*(1/mass);}
    h.center[0]=center.x;h.center[1]=center.y;h.center[2]=center.z;h.velocity[0]=velocity.x;h.velocity[1]=velocity.y;h.velocity[2]=velocity.z;
    Vec direction=V(a.getDirection());direction.y=0;double norm=direction.Norm();
    h.headingDegrees=norm>0?std::acos(std::max(-1.,std::min(1.,direction.Dot(m_direction)/norm)))*180/3.141592653589793:180;
    h.frontDistance=-front-.5;h.lateral=(center-m_origin).Dot(Vec(-m_direction.z,0,m_direction.x));
    for(int i=0;i<m_beams;++i){const auto& b=a.ar_beams[i];auto& x=Beams()[i];x.id=i;x.node1=b.p1-a.ar_nodes;x.node2=b.p2-a.ar_nodes;
        x.flags=(b.bm_disabled?1:0)|(b.bm_broken?2:0);x.length=static_cast<float>((V(b.p1->RelPosition)-V(b.p2->RelPosition)).Norm());
        x.rest=b.L;x.k=b.k;x.d=b.d;x.stress=b.stress;x.strength=b.strength;x.type=b.bm_type;x.bounded=b.bounded;}
    ++m_produced;auto head=m_head.load(std::memory_order_relaxed);
    const bool injectedFull=m_fault=="queue-overflow"&&m_trigger.load()&&h.tick==m_trigger.load()+500;
    if(injectedFull||head-m_tail.load(std::memory_order_acquire)>=m_capacity)++m_dropped;
    else{std::memcpy(m_queue.data()+(head%m_capacity)*m_stride,m_scratch.data(),m_stride);m_head.store(head+1,std::memory_order_release);}
}
void Detail::Writer(){
#ifdef _WIN32
    FILE* file=_fsopen((m_root+"/detail.rort").c_str(),"wb",_SH_DENYNO);
#else
    FILE* file=std::fopen((m_root+"/detail.rort").c_str(),"wb");
#endif
    if(!file){m_error=true;return;}
    std::vector<unsigned char> bytes,meta;bytes.reserve(m_stride);
    for(auto x:{1u,static_cast<unsigned>(m_nodes),static_cast<unsigned>(m_beams),static_cast<unsigned>(m_nodes*4+32),4000u,8000u})U32(meta,x);
    if(std::fwrite("RORDTAIL",1,8,file)!=8||std::fwrite(meta.data(),1,meta.size(),file)!=meta.size()||!Sync(file))m_error=true;
    std::ofstream events(m_root+"/impact-events.jsonl"),summaries(m_root+"/impact-summaries.jsonl"),gaps(m_root+"/detail-gaps.jsonl");
    std::uint64_t historyHead=0,historyCount=0,first=0,last=0,end=0,firstTrigger=0,lastContact=0,approachTick=0,written=0,pending=0,missing=0,episodes=0;
    Vec impulse;double contactWork=0,peakApplication=0,peakNet=0,windowPeak=0;bool faultApplied=false;
    auto lastSync=std::chrono::steady_clock::now();
    auto write=[&](const unsigned char* frame){
        const auto& h=*reinterpret_cast<const DetailHeader*>(frame);
        if(last&&h.tick!=last+1){auto lost=h.tick-last-1;missing+=lost;gaps<<"{\"afterTick\":"<<last<<",\"beforeTick\":"<<h.tick<<",\"missingTicks\":"<<lost<<"}\n";}
        Encode(bytes,frame);meta.clear();U32(meta,1);U32(meta,static_cast<unsigned>(bytes.size()));U32(meta,Crc32(bytes.data(),bytes.size()));
        bool inject=m_fault=="storage-error"&&!faultApplied&&h.tick>=firstTrigger&&firstTrigger;
        const auto offset=Position(file);
        bool ok=false;
        if(inject){faultApplied=true;std::fwrite("DATA",1,4,file);std::fwrite(meta.data(),1,meta.size(),file);std::fwrite(bytes.data(),1,64,file);}
        else ok=std::fwrite("DATA",1,4,file)==4&&std::fwrite(meta.data(),1,meta.size(),file)==meta.size()&&std::fwrite(bytes.data(),1,bytes.size(),file)==bytes.size()&&std::fwrite("DONE",1,4,file)==4;
        if(!ok){m_error=true;++missing;bool recovered=offset>=0&&Rollback(file,offset);
            gaps<<"{\"tick\":"<<h.tick<<",\"reason\":\"writer failure\",\"injected\":"<<(inject?"true":"false")<<",\"partialFrameRolledBack\":"<<(recovered?"true":"false")<<"}\n";}
        else{++written;++pending;}
        if(!first)first=h.tick;last=h.tick;
        auto now=std::chrono::steady_clock::now();
        if(now-lastSync>std::chrono::milliseconds(250)){
            if(Sync(file)){m_durable+=pending;pending=0;}else m_error=true;lastSync=now;
            std::ofstream progress(m_root+"/detail-progress.json");
            progress<<"{\"durable\":"<<m_durable.load()<<",\"written\":"<<written<<",\"lastWrittenTick\":"<<h.tick
                <<",\"triggerTick\":"<<firstTrigger<<",\"requiredEndTick\":"<<end<<",\"dropped\":"<<Dropped()<<",\"ioError\":"<<(m_error.load()?"true":"false")<<"}\n";
        }
    };
    while(!m_stop.load(std::memory_order_acquire)||m_tail.load()<m_head.load()){
        auto tail=m_tail.load(std::memory_order_relaxed),head=m_head.load(std::memory_order_acquire);
        if(tail==head){std::this_thread::sleep_for(std::chrono::milliseconds(2));continue;}
        const unsigned char* frame=m_queue.data()+(tail%m_capacity)*m_stride;
        const auto& h=*reinterpret_cast<const DetailHeader*>(frame);
        const auto* contacts=reinterpret_cast<const DetailContact*>(frame+128+m_nodes*256+m_beams*112);
        if(h.phase&&!approachTick&&h.frontDistance<=.25){
            approachTick=h.tick;std::ofstream approach(m_root+"/approach.json");
            double speed=h.velocity[0]*m_direction.x+h.velocity[2]*m_direction.z;
            approach<<std::setprecision(17)<<"{\"schema\":1,\"profile\":\"barrier-approach-v1\",\"tick\":"<<h.tick
                <<",\"speedMps\":"<<speed<<",\"horizontalSpeedMps\":"<<std::hypot(h.velocity[0],h.velocity[2])
                <<",\"headingDegrees\":"<<h.headingDegrees<<",\"lateralM\":"<<h.lateral<<",\"frontDistanceM\":"<<h.frontDistance
                <<",\"kineticJ\":"<<h.kinetic<<",\"definition\":\"first released tick frontmost node is <=0.25m before front face; signed mass-weighted COM velocity projected on frozen direction\"}\n";
        }
        bool closing=false;Vec net;
        for(unsigned i=0;i<h.contacts;++i)if(contacts[i].barrier){const auto& c=contacts[i];Vec applied=Get(c.applied),normal=Get(c.normal);
            if(applied.Norm()==0)continue;
            closing=closing||Get(c.velocity).Dot(normal)<-.1;
            net+=applied;impulse+=applied*h.dt;
            // Actual contact's contribution to midpoint integration work uses the recorded total node kick.
            const auto& node=reinterpret_cast<const DetailNode*>(frame+128)[c.node];
            contactWork+=applied.Dot((Get(node.beforeVelocity)+Get(node.velocity))*.5)*h.dt;
            peakApplication=std::max(peakApplication,applied.Norm());
        }
        bool trigger=h.barrierContacts&&(!firstTrigger||(closing&&h.tick>lastContact+1000));
        if(h.barrierContacts)lastContact=h.tick;
        if(trigger){
            ++episodes;end=std::max(end,h.tick+8000);
            events<<"{\"event\":\"consumed-barrier-impact\",\"tick\":"<<h.tick<<",\"windowEndTick\":"<<end<<",\"episode\":"<<episodes<<",\"applications\":"<<h.barrierContacts<<"}\n";events.flush();
            if(!firstTrigger){
                firstTrigger=h.tick;const auto start=h.tick>4000?h.tick-4000:1;
                std::uint64_t found=0;
                for(std::uint64_t i=0;i<historyCount;++i){auto index=(historyHead-historyCount+i)%m_history_capacity;const auto* old=m_history.data()+index*m_stride;
                    auto tick=reinterpret_cast<const DetailHeader*>(old)->tick;
                    if(tick>=start&&(m_fault!="short-history"||tick+1000>=h.tick)){write(old);++found;}}
                if(found<4000){missing+=4000-found;gaps<<"{\"beforeTriggerTick\":"<<h.tick<<",\"requiredPreTicks\":4000,\"observedPreTicks\":"<<found<<"}\n";}
            }
        }
        peakNet=std::max(peakNet,net.Norm());windowPeak=std::max(windowPeak,net.Norm());
        if(firstTrigger&&h.tick<=end)write(frame);
        if(!firstTrigger){std::memcpy(m_history.data()+(historyHead%m_history_capacity)*m_stride,frame,m_stride);++historyHead;historyCount=std::min<std::uint64_t>(historyCount+1,m_history_capacity);}
        if(h.tick%10==0){
            summaries<<std::setprecision(17)<<"{\"tick\":"<<h.tick<<",\"timeSeconds\":"<<h.tick*h.dt<<",\"triggerTick\":"<<firstTrigger<<",\"windowEndTick\":"<<end
                <<",\"contactApplications\":"<<h.barrierContacts<<",\"peakNetBarrierForceN\":"<<windowPeak<<",\"peakApplicationForceN\":"<<peakApplication
                <<",\"barrierImpulseNs\":["<<impulse.x<<","<<impulse.y<<","<<impulse.z<<"],\"barrierWorkJ\":"<<contactWork
                <<",\"frontDistanceM\":"<<h.frontDistance<<",\"headingDegrees\":"<<h.headingDegrees<<",\"detailDurable\":"<<m_durable.load()
                <<",\"detailDropped\":"<<Dropped()<<",\"detailIoError\":"<<(m_error.load()?"true":"false")<<"}\n";summaries.flush();windowPeak=0;
        }
        if(!events||!summaries||!gaps)m_error=true;
        m_tail.store(tail+1,std::memory_order_release);
    }
    if(firstTrigger&&last<end){missing+=end-last;gaps<<"{\"afterTick\":"<<last<<",\"requiredEndTick\":"<<end<<",\"reason\":\"posthistory unavailable\"}\n";}
    if(Sync(file)){m_durable+=pending;pending=0;}else m_error=true;
    meta.clear();U64(meta,written);U64(meta,Dropped());U64(meta,missing);U32(meta,m_error.load()?1:0);
    if(std::fwrite("END!",1,4,file)!=4||std::fwrite(meta.data(),1,meta.size(),file)!=meta.size()||!Sync(file))m_error=true;
    if(std::fclose(file))m_error=true;
    std::ofstream health(m_root+"/detail-health.json");
    health<<std::setprecision(17)<<"{\"schema\":1,\"produced\":"<<m_produced.load()<<",\"enqueued\":"<<m_head.load()<<",\"written\":"<<written
        <<",\"durable\":"<<m_durable.load()<<",\"dropped\":"<<Dropped()<<",\"missingRequiredTicks\":"<<missing<<",\"ioError\":"<<(m_error.load()?"true":"false")
        <<",\"closed\":true,\"triggerTick\":"<<firstTrigger<<",\"firstTick\":"<<first<<",\"lastTick\":"<<last<<",\"requiredEndTick\":"<<end
        <<",\"episodes\":"<<episodes<<",\"peakApplicationForceN\":"<<peakApplication<<",\"peakNetBarrierForceN\":"<<peakNet
        <<",\"barrierImpulseNs\":["<<impulse.x<<","<<impulse.y<<","<<impulse.z<<"],\"barrierWorkJ\":"<<contactWork<<"}\n";
}
}}
