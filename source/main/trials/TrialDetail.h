// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "TrialLedger.h"
#include "TrialRecorderHealth.h"
#include <atomic>
#include <thread>
#include <string>
#include <cstring>
namespace RoR { class Actor; namespace Trials {
// Native float32 solver values; double precision tick clock and cohort reduction.
// Explicit little-endian encoding occurs on the recorder thread.
struct DetailNode {
    std::uint32_t id=0,flags=0;
    float mass=0,reserved=0;
    float position[3]{},beforeVelocity[3]{},velocity[3]{},force[3]{};
    float channels[ChannelCount][3]{};
};
struct DetailBeam {
    std::uint32_t id=0,node1=0,node2=0,flags=0;
    float length=0,rest=0,k=0,d=0,stress=0,strength=0;
    float beforeRest=0,beforeK=0,beforeStrength=0;
    std::uint32_t beforeActive=0,type=0,bounded=0;
    float generated1[3]{},generated2[3]{},elastic[3]{},damping[3]{};
};
struct DetailContact {
    std::uint32_t node=0,kind=0,feature=0,barrier=0;
    float position[3]{},normal[3]{},velocity[3]{},rawForce[3]{},applied[3]{},beforeForce[3]{};
    float mass=0,penetration=0;
    std::uint32_t material=0,reserved=0;
};
struct DetailHeader {
    std::uint64_t tick=0;
    double dt=0;
    std::uint32_t actor=0,nodes=0,beams=0,contacts=0,phase=0,flags=0,lost=0,barrierContacts=0;
    double center[3]{},velocity[3]{};
    double kinetic=0,headingDegrees=0,frontDistance=0,lateral=0;
};
static_assert(sizeof(DetailNode)==256,"node layout");
static_assert(sizeof(DetailBeam)==112,"beam layout");
static_assert(sizeof(DetailContact)==104,"contact layout");
static_assert(sizeof(DetailHeader)==128,"header layout");
static_assert(offsetof(DetailNode,channels)==64,"channel wire offset");
static_assert(offsetof(DetailBeam,generated1)==64,"beam application wire offset");
static_assert(offsetof(DetailContact,material)==96,"material wire offset");
static_assert(offsetof(DetailHeader,center)==48,"cohort wire offset");
inline std::size_t DetailFrameBytes(const DetailHeader& h) {return 128+static_cast<std::size_t>(h.nodes)*256+static_cast<std::size_t>(h.beams)*112+static_cast<std::size_t>(h.contacts)*104;}
inline void CopyDetailFrame(unsigned char* dst,const unsigned char* src) {
    std::memcpy(dst,src,DetailFrameBytes(*reinterpret_cast<const DetailHeader*>(src)));
}
class Detail;
struct ContactSink {
    Detail* owner=nullptr;
    std::uint32_t node=0;
    void Observe(std::uint32_t kind,std::uint32_t feature,Vec position,Vec normal,Vec velocity,
        Vec before,Vec after,Vec raw,float mass,float penetration,std::uint32_t material);
};
class Detail {
public:
    Detail(const std::string& root,const std::string& fault,int nodes,int beams,int barrier,Vec origin,Vec direction);
    ~Detail();
    void Begin(Actor& actor,std::uint64_t tick,bool released);
    ContactSink* Sink(int node);
    void Node(Actor& actor,int node,Vec beforeVelocity,Vec force);
    void Finish(Actor& actor);
    void Beam(int beam,Vec first,Vec second,Vec elastic,Vec damping);
    void Stop();
    void Contact(std::uint32_t node,std::uint32_t kind,std::uint32_t feature,Vec position,Vec normal,Vec velocity,
        Vec before,Vec after,Vec raw,float mass,float penetration,std::uint32_t material);
    std::uint64_t Dropped() const {return m_dropped.load()+m_contact_lost.load();}
    bool Error() const {return m_error.load();}
    std::uint64_t Trigger() const {return m_trigger.load();}
    std::uint64_t Durable() const {return m_durable.load();}
    std::string Health() const {const auto tail=m_tail.load(),head=m_head.load();return m_health.Json(head,tail,m_durable.load(),m_capacity,m_stride,Dropped(),Error());}
private:
    void Writer();
    DetailHeader& Header() {return *reinterpret_cast<DetailHeader*>(m_scratch.data());}
    DetailNode* Nodes() {return reinterpret_cast<DetailNode*>(m_scratch.data()+128);}
    DetailBeam* Beams() {return reinterpret_cast<DetailBeam*>(m_scratch.data()+128+m_nodes*256);}
    DetailContact* Contacts() {return reinterpret_cast<DetailContact*>(m_scratch.data()+128+m_nodes*256+m_beams*112);}
    std::string m_root,m_fault;
    int m_nodes,m_beams,m_barrier;
    Vec m_origin,m_direction;
    std::size_t m_stride,m_capacity,m_history_capacity=4001;
    std::vector<unsigned char> m_scratch,m_queue,m_history;
    ContactSink m_sink;
    std::atomic<std::uint64_t> m_head{0},m_tail{0},m_dropped{0},m_contact_lost{0},m_trigger{0},m_durable{0},m_produced{0};
    std::atomic<bool> m_stop{false},m_error{false};
    std::thread m_writer;
    RecorderHealth m_health;
};
}}
