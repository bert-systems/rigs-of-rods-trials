// SPDX-License-Identifier: GPL-3.0-or-later
#include "TrialRuntime.h"
#include "Actor.h"
#include "Application.h"
#include "GameContext.h"
#include "GfxScene.h"
#include "Terrain.h"
#include "Collisions.h"
#include <fstream>
#include <iomanip>
namespace RoR { namespace Trials {
namespace {Vec V(Ogre::Vector3 p){return Vec(p.x,p.y,p.z);}}
void Runtime::PrepareBarrier(Actor& a)
{
    // Main-thread setup after joining physics; geometry is fixed for the attempt.
    auto terrain=App::GetGameContext()->GetTerrain();
    Ogre::Vector3 forward=a.getDirection();forward.y=0;
    if(forward.squaredLength()<1e-8f){m_scope_violation=true;return;}
    forward.normalise();
    Ogre::Vector3 center=Ogre::Vector3::ZERO;double mass=0,front=-1e30;
    for(int i=0;i<a.ar_num_nodes;++i){center+=a.ar_nodes[i].AbsPosition*a.ar_nodes[i].mass;mass+=a.ar_nodes[i].mass;
        front=std::max(front,V(a.ar_nodes[i].AbsPosition).Dot(V(forward)));}
    center/=static_cast<float>(mass);
    center+=forward*static_cast<float>(front-V(center).Dot(V(forward))+m_barrier_distance+.5);
    center.y=terrain->getHeightAt(center.x,center.z);
    const float yaw=static_cast<float>(std::atan2(-forward.z,forward.x)*180/3.141592653589793);
    auto* collisions=terrain->GetCollisions();
    int feature=collisions->addCollisionBox(false,false,center,Ogre::Vector3(0,yaw,0),
        Ogre::Vector3(-.5f,-.2f,-8),Ogre::Vector3(.5f,6,8),Ogre::Vector3::ZERO,"","trial-barrier-v1","",false,Ogre::Vector3::ZERO);
    auto material=Ogre::MaterialManager::getSingleton().create("TrialBarrierMaterial",Ogre::ResourceGroupManager::DEFAULT_RESOURCE_GROUP_NAME);
    auto* pass=material->getTechnique(0)->getPass(0);pass->setLightingEnabled(false);pass->setVertexColourTracking(Ogre::TVC_DIFFUSE);
    auto* scene=App::GetGfxScene()->GetSceneManager();auto* object=scene->createManualObject("TrialBarrier-v1");
    object->begin("TrialBarrierMaterial",Ogre::RenderOperation::OT_TRIANGLE_LIST);
    Ogre::Quaternion rotation(Ogre::Degree(yaw),Ogre::Vector3::UNIT_Y);
    const Ogre::Vector3 corners[]={Ogre::Vector3(-.5f,0,-8),Ogre::Vector3(.5f,0,-8),Ogre::Vector3(.5f,6,-8),Ogre::Vector3(-.5f,6,-8),
        Ogre::Vector3(-.5f,0,8),Ogre::Vector3(.5f,0,8),Ogre::Vector3(.5f,6,8),Ogre::Vector3(-.5f,6,8)};
    const int indices[]={0,2,1,0,3,2,4,5,6,4,6,7,0,4,7,0,7,3,1,2,6,1,6,5,3,7,6,3,6,2,0,1,5,0,5,4};
    for(int i:indices){object->position(center+rotation*corners[i]);object->colour(Ogre::ColourValue(.95f,.35f,.08f));}
    object->end();scene->getRootSceneNode()->createChildSceneNode()->attachObject(object);
    auto* gm=collisions->defaultgm;
    std::ofstream resolved(m_root+"/barrier.json");
    resolved<<std::setprecision(17)<<"{\"schema\":1,\"asset\":\"controlled-concrete-box-v1\",\"logicalFeature\":1,\"nativeBoxIndex\":"<<feature
        <<",\"originM\":["<<center.x<<","<<center.y<<","<<center.z<<"],\"direction\":["<<forward.x<<","<<forward.y<<","<<forward.z
        <<"],\"yawDegrees\":"<<yaw<<",\"localBoundsM\":[[-0.5,-0.2,-8],[0.5,6,8]],\"distanceFromInitialFrontM\":"<<m_barrier_distance
        <<",\"material\":\""<<gm->name<<"\",\"frictionStatic\":"<<gm->ms<<",\"frictionSliding\":"<<gm->mc<<",\"strength\":"<<gm->strength
        <<",\"solidGroundLevelM\":"<<gm->solid_ground_level<<",\"collisionLaw\":\"native primitiveCollision; boxes supply zero penetration\"}\n";
    std::ofstream models(m_root+"/contact-materials.json");models<<"[";bool comma=false;
    for(const auto& item:*collisions->getGroundModels()){
        std::uint32_t hash=2166136261u;for(char c:item.first)hash=(hash^static_cast<unsigned char>(c))*16777619u;
        if(comma)models<<",";comma=true;const auto& model=item.second;
        models<<std::setprecision(17)<<"{\"id\":"<<hash<<",\"name\":\""<<item.first<<"\",\"staticFriction\":"<<model.ms<<",\"slidingFriction\":"<<model.mc<<",\"strength\":"<<model.strength<<"}";
    }models<<"]";
    m_detail=std::make_unique<Detail>(m_root,m_detail_fault,a.ar_num_nodes,a.ar_num_beams,feature,V(center),V(forward));
}
ContactSink* Runtime::ContactObserver(Actor& a,int node)
{
    return m_detail&&a.ar_trial_ledger.enabled&&m_pilot_actor.load()==a.ar_instance_id?m_detail->Sink(node):nullptr;
}
void Runtime::DetailBeamObserved(Actor& a,int beam,Vec first,Vec second,Vec elastic,Vec damping)
{
    if(m_detail&&m_pilot_actor.load()==a.ar_instance_id)m_detail->Beam(beam,first,second,elastic,damping);
}
void Runtime::DetailNodeObserved(Actor& a,int node,Vec beforeVelocity,Vec force)
{
    if(m_detail&&m_pilot_actor.load()==a.ar_instance_id)m_detail->Node(a,node,beforeVelocity,force);
}
}}
