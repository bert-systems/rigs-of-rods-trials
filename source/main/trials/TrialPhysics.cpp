// SPDX-License-Identifier: GPL-3.0-or-later
#include "TrialRuntime.h"
#include "Actor.h"
#include "ActorManager.h"
#include "Engine.h"
#include "SimConstants.h"
#include <algorithm>
#include <cmath>

namespace RoR { namespace Trials {
namespace {
Vec V(Ogre::Vector3 v) {return Vec(v.x,v.y,v.z);}
double LinearStorage(double k,double length,double rest) {const double x=length-rest;return 0.5*k*x*x;}
bool Linear(const beam_t& b) {return b.bm_type==BEAM_NORMAL && b.bounded==NOSHOCK && !b.bm_inter_actor;}
double Length(const beam_t& b)
{
    return (V(b.p1->RelPosition)-V(b.p2->RelPosition)).Norm();
}
}
bool Runtime::Matches(const Actor& a) const
{
    return a.ar_filename==(IsFixture()?"ror-"+m_scenario+".truck":"b6b0UID-semi.truck");
}
void Runtime::PrepareActor(Actor& actor)
{
    if(!m_enabled || !Matches(actor))return;
    if(actor.ar_num_nodes<=0 || actor.ar_num_nodes>65536 || actor.ar_num_beams>65536){m_scope_violation=true;return;}
    int expected=-1;
    m_ready_actor.compare_exchange_strong(expected,actor.ar_instance_id);
    if(m_ready_actor.load()!=actor.ar_instance_id){m_scope_violation=true;return;} // sticky unsupported second pilot
    if(!m_observe)return;
    auto& l=actor.ar_trial_ledger;
    if(l.nodes.size()==static_cast<std::size_t>(actor.ar_num_nodes))return;
    // Poll is called on the render/main thread after joining the physics task.
    if(actor.ar_num_nodes<=0 || actor.ar_num_nodes>65536 || actor.ar_num_beams>65536){m_scope_violation=true;return;}
    l.Prepare(actor.ar_num_nodes,actor.ar_num_beams);
    l.attribution_enabled=m_accounting;
    if(m_scenario=="barrier-v1"&&!m_detail)PrepareBarrier(actor);
    l.detail_transitions=m_detail!=nullptr;
    for(int i=0;i<actor.ar_num_nodes;++i)
        {l.nodes[i].force[Unattributed]=V(actor.ar_nodes[i].Forces);l.nodes[i].active=1u<<Unattributed;} // honest warm-up provenance
}
void Runtime::Snapshot(Actor& actor)
{
    auto& l=actor.ar_trial_ledger;
    if(!l.enabled || !l.attribution_enabled)return;
    for(int i=0;i<actor.ar_num_nodes;++i)l.nodes[i].snapshot=V(actor.ar_nodes[i].Forces);
}
void Runtime::Delta(Actor& actor,Channel channel)
{
    auto& l=actor.ar_trial_ledger;
    if(!l.enabled || !l.attribution_enabled)return;
    for(int i=0;i<actor.ar_num_nodes;++i){
        const Vec actual=V(actor.ar_nodes[i].Forces);
        l.Add(i,channel,actual-l.nodes[i].snapshot,!actor.ar_nodes[i].nd_immovable);
        l.nodes[i].snapshot=actual; // next phase starts from this same boundary
    }
}
void Runtime::InitializeFixture(Actor& actor)
{
    if(actor.ar_num_nodes!=4 || actor.ar_num_beams<1){m_scope_violation=true;return;}
    actor.ar_origin=Ogre::Vector3(500,20,500); // preserve local-coordinate precision in the controlled fixture
    const Ogre::Vector3 offsets[]={Ogre::Vector3(1.05f,0,0),Ogre::Vector3(0,0,0),Ogre::Vector3(0,0,1),Ogre::Vector3(0,1,0)};
    for(int i=0;i<actor.ar_num_nodes;++i)
    {
        node_t& n=actor.ar_nodes[i];
        n.nd_immovable=i!=0;n.nd_no_ground_contact=true;
        n.mass=i==0?100.f:1.f;n.Velocity=Ogre::Vector3::ZERO;
        n.RelPosition=offsets[i];
        n.AbsPosition=actor.ar_origin+n.RelPosition;
        n.Forces=Ogre::Vector3(0,n.mass*static_cast<float>(m_gravity),0);
        if(actor.ar_trial_ledger.enabled)actor.ar_trial_ledger.Reset(i,V(n.Forces),!n.nd_immovable);
    }
    actor.ar_total_mass=103.f;actor.ar_initial_total_mass=103.f;
    actor.ar_disable_aerodyn_turbulent_drag=true;
    for(int i=0;i<actor.ar_num_beams;++i)
    {
        beam_t& b=actor.ar_beams[i];b.bm_disabled=i!=0;b.bm_broken=false;
        b.k=m_scenario=="freefall-v1"?0.f:10000.f;
        b.d=m_scenario=="damper-v1"?200.f:0.f;
        b.L=1.f;b.refL=1.f;b.strength=1e9f;b.maxposstress=1e9f;b.maxnegstress=-1e9f;b.minmaxposnegstress=1e9f;
    }
    if(actor.ar_engine){actor.ar_engine->stopEngine();actor.ar_engine->setGear(0);}
}
void Runtime::Energy(Actor& actor,bool before)
{
    auto& l=actor.ar_trial_ledger;
    double ug=0,us=0;
    for(int i=0;i<actor.ar_num_nodes;++i)
    {
        const node_t& n=actor.ar_nodes[i];
        if(!n.nd_immovable)
            ug-=m_gravity*n.mass*(static_cast<double>(actor.ar_origin.y)+n.RelPosition.y);
    }
    for(int i=0;i<actor.ar_num_beams;++i)
    {
        const beam_t& b=actor.ar_beams[i];
        const bool active=!b.bm_disabled&&!b.bm_broken;
        const bool eligible=Linear(b);
        double length=0;
        if(active && eligible){length=Length(b);us+=LinearStorage(b.k,length,b.L);}
        if(before)
        {
            l.beam_rest[i]=b.L;l.beam_k[i]=b.k;l.beam_strength[i]=b.strength;l.beam_active[i]=active?1:0;
        }
        else
        {
            if(active&&!eligible)++l.record.unclosed_beams;
            l.record.peak_beam_stress=std::max(l.record.peak_beam_stress,std::abs(static_cast<double>(b.stress)));
            const bool changed=b.L!=l.beam_rest[i]||b.k!=l.beam_k[i];
            const bool removed=l.beam_active[i]&&!active;
            if(changed||removed)
            {
                if(!(active && eligible))length=Length(b);
                BeamTransition event;
                event.beam=i;event.kind=(changed?(eligible?1:8):0)|(removed?2:0);
                event.length=length;event.oldRest=l.beam_rest[i];event.newRest=b.L;
                event.oldK=l.beam_k[i];event.newK=b.k;event.oldStrength=l.beam_strength[i];event.newStrength=b.strength;
                event.oldStorage=eligible?LinearStorage(event.oldK,length,event.oldRest):0;
                event.newStorage=eligible?LinearStorage(event.newK,length,event.newRest):0;
                event.stress=b.stress;l.Transition(event);
                if(!eligible)l.record.flags|=4;
            }
        }
    }
    if(before){l.record.gravity_before=ug;l.record.elastic_before=us;}
    else {l.record.gravity_after=ug;l.record.elastic_after=us;}
}
}} // namespace
