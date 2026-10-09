// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace RoR { namespace Trials {
struct Vec
{
    double x=0,y=0,z=0;
    Vec()=default;
    Vec(double a,double b,double c):x(a),y(b),z(c) {}
    Vec operator+(Vec v) const { return Vec(x+v.x,y+v.y,z+v.z); }
    Vec operator-(Vec v) const { return Vec(x-v.x,y-v.y,z-v.z); }
    Vec operator*(double s) const { return Vec(x*s,y*s,z*s); }
    Vec& operator+=(Vec v) { x+=v.x; y+=v.y; z+=v.z; return *this; }
    double Dot(Vec v) const { return x*v.x+y*v.y+z*v.z; }
    double Norm() const { return std::sqrt(Dot(*this)); }
    bool Finite() const { return std::isfinite(x)&&std::isfinite(y)&&std::isfinite(z); }
};
enum Channel
{
    Gravity,GenericDrag,GroundObject,BeamElastic,BeamDamping,BeamCorrection,
    Wheels,Aero,Buoyancy,Commands,Mouse,CabContact,Slide,InterActor,FreeForce,Unattributed,ChannelCount
};
inline const char* ChannelName(int c)
{
    const char* names[]={"gravity","genericDrag","groundObject","beamElastic","beamDamping","beamCorrection",
        "wheels","aero","buoyancy","commands","mouse","cabContact","slide","interActor","freeForce","unattributed"};
    return names[c];
}
struct ChannelRecord { Vec force; double work=0; Vec generated; };
struct BeamTransition
{
    std::uint32_t beam=0,kind=0;
    double length=0,oldRest=0,newRest=0,oldK=0,newK=0,oldStrength=0,newStrength=0,oldStorage=0,newStorage=0,stress=0;
};
// Schema 2: base v1 prefix (240 bytes), 16*56 channel bytes, 16 doubles,
// 3 vectors, 4 counters, 2 epochs, 2 event counters, 8*88 transitions = 2080 bytes.
static const std::uint32_t RecordBytes=2080;
struct Record
{
    std::uint64_t tick=0;
    std::uint32_t actor=0,nodes=0,phase=0,flags=0;
    double dt=0,mass=0;
    Vec center,momentum,force,contact_force;
    double kinetic_before=0,kinetic=0,work=0;
    Vec momentum_residual;
    double work_residual=0,peak_node_force=0,gravity=0,density=0;
    Vec wind;
    std::array<ChannelRecord,ChannelCount> channels;
    double gravity_before=0,gravity_after=0,elastic_before=0,elastic_after=0;
    double mechanical_residual=0,nonconservative_work=0,injection_kinetic=0,mutation_kinetic=0;
    double wind_work=0,relative_drag_work=0,unattributed_l1=0,attribution_residual_l1=0;
    // physics_cpu_us is elapsed steady-clock time around the complete native physics step, not process CPU time.
    double rest_storage_port=0,removed_storage_port=0,peak_beam_stress=0,physics_cpu_us=0;
    Vec injection_impulse,fixed_force,mutation_impulse;
    std::uint32_t plastic_events=0,break_events=0,unclosed_beams=0,prepared_nodes=0;
    std::uint64_t consumed_from_tick=0,generated_tick=0;
    std::uint32_t event_count=0,event_dropped=0;
    std::array<BeamTransition,8> events;
};
struct NodeChannels
{
    std::array<Vec,ChannelCount> force;
    Vec snapshot,last_velocity;
    std::uint32_t active=0; // sparse cache; iteration remains in channel order
    double last_mass=0;
    bool has_previous=false,last_fixed=false;
};
class Ledger
{
public:
    bool enabled=false,attribution_enabled=true,detail_transitions=false;
    Record record;
    std::vector<NodeChannels> nodes; // allocated only by render/main-thread preparation
    std::vector<double> beam_rest,beam_k,beam_strength;
    std::vector<unsigned char> beam_active;
    void Prepare(std::size_t count,std::size_t beams)
    {
        nodes.resize(count); beam_rest.resize(beams); beam_k.resize(beams);
        beam_strength.resize(beams); beam_active.resize(beams);
    }
    void Begin(std::uint64_t tick,std::uint32_t actor,std::uint32_t phase,double dt)
    {
        record=Record(); record.tick=tick;record.actor=actor;record.phase=phase;record.dt=dt;
        record.consumed_from_tick=tick?tick-1:0;record.generated_tick=tick;
        record.prepared_nodes=static_cast<std::uint32_t>(nodes.size());
    }
    void Observe(double mass,Vec position,Vec before,Vec after,Vec force,Vec contact)
    {
        if(!(mass>0)||!std::isfinite(mass)||!position.Finite()||!before.Finite()||!after.Finite()||!force.Finite()||!contact.Finite())
        {record.flags|=1;return;}
        ++record.nodes;record.mass+=mass;record.center+=position*mass;record.momentum+=after*mass;
        record.force+=force;record.contact_force+=contact;
        double kb=0.5*mass*before.Dot(before),ka=0.5*mass*after.Dot(after);
        double w=((before+after)*0.5).Dot(force*record.dt);
        record.kinetic_before+=kb;record.kinetic+=ka;record.work+=w;
        record.momentum_residual+=(after-before)*mass-force*record.dt;
        record.work_residual+=ka-kb-w;
        record.peak_node_force=std::max(record.peak_node_force,force.Norm());
        if(!std::isfinite(ka)||!std::isfinite(w))record.flags|=1;
    }
    void Add(std::size_t node,Channel channel,Vec delta,bool moving)
    {
        if(!attribution_enabled)return;
        if(delta.x==0 && delta.y==0 && delta.z==0)return;
        nodes[node].active|=1u<<channel;
        nodes[node].force[channel]+=delta;
        if(moving)record.channels[channel].generated+=delta;
    }
    void Reset(std::size_t node,Vec gravity,bool moving)
    {
        if(!attribution_enabled)return;
        auto& slot=nodes[node];
        for(int c=0;c<ChannelCount;++c)if(slot.active&(1u<<c))slot.force[c]=Vec();
        slot.active=1u<<Gravity;
        slot.force[Gravity]=gravity;
        if(moving)record.channels[Gravity].generated+=gravity;
    }
    void Consume(std::size_t node,double mass,Vec before,Vec after,Vec actual,Vec wind,bool fixed)
    {
        if(!attribution_enabled)return;
        auto& slot=nodes[node];
        Vec expected;
        for(int c=0;c<ChannelCount;++c)if(slot.active&(1u<<c))expected+=slot.force[c];
        Vec correction=actual-expected;
        if(correction.x!=0 || correction.y!=0 || correction.z!=0)slot.active|=1u<<Unattributed;
        slot.force[Unattributed]+=correction;
        if(slot.has_previous && slot.last_fixed!=fixed)record.flags|=4; // unsupported cohort exchange
        if(fixed) {
            record.fixed_force+=actual;slot.last_mass=mass;slot.last_velocity=after;
            slot.has_previous=true;slot.last_fixed=true;return;
        }
        record.unattributed_l1+=slot.force[Unattributed].Norm();
        Vec reconstructed;
        const Vec mid=(before+after)*0.5;
        for(int c=0;c<ChannelCount;++c)
        {
            if(!(slot.active&(1u<<c)))continue;
            auto& out=record.channels[c];
            out.force+=slot.force[c];
            out.work+=mid.Dot(slot.force[c]*record.dt);
            reconstructed+=slot.force[c];
        }
        record.attribution_residual_l1+=(actual-reconstructed).Norm();
        record.wind_work+=wind.Dot(slot.force[GenericDrag]*record.dt);
        record.relative_drag_work+=(mid-wind).Dot(slot.force[GenericDrag]*record.dt);
        if(slot.has_previous && !(record.flags&2))
        {
            record.mutation_kinetic+=0.5*(mass*before.Dot(before)-slot.last_mass*slot.last_velocity.Dot(slot.last_velocity));
            record.mutation_impulse+=before*mass-slot.last_velocity*slot.last_mass;
            if(mass!=slot.last_mass)record.flags|=4; // mass/cohort flux unqualified
        }
        slot.last_mass=mass;slot.last_velocity=after;slot.has_previous=true;slot.last_fixed=false;
    }
    void Transition(const BeamTransition& value)
    {
        if(value.kind&9){if(value.kind&1)++record.plastic_events;record.rest_storage_port+=value.newStorage-value.oldStorage;}
        if(value.kind&2){++record.break_events;record.removed_storage_port-=value.newStorage;}
        if(record.event_count<record.events.size())record.events[record.event_count++]=value;
        else {++record.event_dropped;record.flags|=detail_transitions?16:1;} // flag16: dense detail carries all transitions; projection omitted
    }
    Record Finish()
    {
        if(record.mass>0)record.center=record.center*(1.0/record.mass);
        for(int c=0;c<ChannelCount;++c)
            if(c!=Gravity&&c!=BeamElastic)record.nonconservative_work+=record.channels[c].work;
        record.mechanical_residual=record.kinetic-record.kinetic_before+
            record.gravity_after-record.gravity_before+record.elastic_after-record.elastic_before-
            record.nonconservative_work-record.rest_storage_port-record.removed_storage_port;
        return record;
    }
};
inline std::uint32_t Crc32(const unsigned char* bytes,std::size_t size)
{
    // Recorder threads use a byte table rather than eight bit iterations per byte.
    // Same IEEE CRC-32 polynomial and archive bytes as schemas 1/2.
    static const auto table=[](){
        std::array<std::uint32_t,256> t{};
        for(unsigned i=0;i<256;++i){
            std::uint32_t v=i;
            for(int b=0;b<8;++b)v=(v>>1)^(0xedb88320u&(0u-(v&1u)));
            t[i]=v;
        }
        return t;
    }();
    std::uint32_t crc=0xffffffffu;
    for(std::size_t i=0;i<size;++i)crc=(crc>>8)^table[(crc^bytes[i])&255];
    return ~crc;
}
}} // namespace
