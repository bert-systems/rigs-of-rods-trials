// SPDX-License-Identifier: GPL-3.0-or-later
#include "TrialRuntime.h"
#include "Actor.h"
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <algorithm>
#ifdef _WIN32
#include <io.h>
#include <share.h>
#else
#include <unistd.h>
#endif
namespace RoR { namespace Trials {
namespace {
void U32(std::vector<unsigned char>& out,std::uint32_t n){for(int i=0;i<4;++i)out.push_back(static_cast<unsigned char>(n>>(8*i)));}
void U64(std::vector<unsigned char>& out,std::uint64_t n){for(int i=0;i<8;++i)out.push_back(static_cast<unsigned char>(n>>(8*i)));}
void D(std::vector<unsigned char>& out,double n){std::uint64_t b;std::memcpy(&b,&n,8);U64(out,b);}
void V(std::vector<unsigned char>& out,Vec v){D(out,v.x);D(out,v.y);D(out,v.z);}
bool Sync(FILE* f){
    if(std::fflush(f)!=0)return false;
#ifdef _WIN32
    return _commit(_fileno(f))==0;
#else
    return fsync(fileno(f))==0;
#endif
}
void Hash(std::uint64_t& h,float v){
    std::uint32_t b;std::memcpy(&b,&v,4);
    for(int i=0;i<4;++i){h^=static_cast<unsigned char>(b>>(8*i));h*=1099511628211ULL;}
}
void Hash(std::uint64_t& h,Ogre::Vector3 v){Hash(h,v.x);Hash(h,v.y);Hash(h,v.z);}
Vec Vector(Ogre::Vector3 v){return Vec(v.x,v.y,v.z);}
}
void Runtime::Probe(Actor& actor)
{
    // End the common timer before sampling or queueing the common probe. Includes
    // control, native job/barrier phases and (when enabled) all ledger reduction/copy.
    ProbeRecord p;
    p.elapsed=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-m_step_started).count();
    p.tick=m_tick;p.phase=m_released?1:0;p.nodes=actor.ar_num_nodes;p.beams=actor.ar_num_beams;
    p.flags=m_scope_violation.load()?1:0;p.dt=PHYSICS_DT;
    p.position=Vector(actor.ar_nodes[0].AbsPosition);p.velocity=Vector(actor.ar_nodes[0].Velocity);
    p.origin=Vector(actor.ar_origin);p.initialized=m_initializing?1:0;
    // FNV-1a diagnostic fingerprint, NOT a cryptographic identity or exhaustive
    // engine state checkpoint. All node world position/velocity/force/mass/cohort
    // and local beam L/k/d/strength/active state sampled every 200 ticks (10 Hz).
    if(m_tick%200==0){
        p.sampled=1;p.fingerprint=14695981039346656037ULL;
        for(int i=0;i<actor.ar_num_nodes;++i){
            const auto& n=actor.ar_nodes[i];
            Hash(p.fingerprint,n.AbsPosition);Hash(p.fingerprint,n.Velocity);
            Hash(p.fingerprint,n.Forces);Hash(p.fingerprint,n.mass);Hash(p.fingerprint,n.nd_immovable?1.f:0.f);
        }
        for(int i=0;i<actor.ar_num_beams;++i){
            const auto& b=actor.ar_beams[i];
            Hash(p.fingerprint,b.L);Hash(p.fingerprint,b.k);Hash(p.fingerprint,b.d);Hash(p.fingerprint,b.strength);
            Hash(p.fingerprint,b.bm_disabled?1.f:0.f);Hash(p.fingerprint,b.bm_broken?1.f:0.f);
        }
    }
    const auto head=m_probe_head.load(std::memory_order_relaxed);
    if(head-m_probe_tail.load(std::memory_order_acquire)>=m_probe_queue.size()){++m_probe_dropped;return;}
    m_probe_queue[head%m_probe_queue.size()]=p;
    m_probe_health.Admit(head+1-m_probe_tail.load(std::memory_order_acquire),128);
    m_probe_head.store(head+1,std::memory_order_release);
}
void Runtime::ProbeWriter()
{
#ifdef _WIN32
    FILE* f=_fsopen((m_root+"/probe.rort").c_str(),"wb",_SH_DENYNO);
#else
    FILE* f=std::fopen((m_root+"/probe.rort").c_str(),"wb");
#endif
    if(!f){m_probe_error=true;m_probe_health.closed=true;return;}
    auto sync=[&](){const auto start=std::chrono::steady_clock::now();const bool ok=Sync(f);
        m_probe_health.Synced(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-start).count());return ok;};
    auto progress=[&](){const auto tail=m_probe_tail.load(),head=m_probe_head.load();std::ofstream out(m_root+"/probe-progress.json");
        out<<m_probe_health.Json(head,tail,m_probe_written.load(),m_probe_queue.size(),128,m_probe_dropped.load(),m_probe_error.load())<<"\n";};
    std::vector<unsigned char> header;U32(header,1);U32(header,128);
    bool ok=std::fwrite("RORPROBE",1,8,f)==8 && std::fwrite(header.data(),1,header.size(),f)==header.size() && sync();
    if(!ok)m_probe_error=true;
    std::ofstream summaries(m_root+"/probe-summaries.jsonl");
    std::vector<unsigned char> bytes;bytes.reserve(128*128);
    std::uint64_t pending=0;SyncSchedule syncSchedule;
    while(!m_stop.load(std::memory_order_acquire)||m_probe_tail.load()<m_probe_head.load()){
        auto tail=m_probe_tail.load(std::memory_order_relaxed);
        const auto count=std::min<std::uint64_t>(128,m_probe_head.load(std::memory_order_acquire)-tail);
        if(count<128&&!m_stop.load()){std::this_thread::sleep_for(std::chrono::milliseconds(5));continue;}
        bytes.clear();
        const auto encodeStart=std::chrono::steady_clock::now();
        for(std::uint64_t i=0;i<count;++i){
            const auto& p=m_probe_queue[(tail+i)%m_probe_queue.size()];
            U64(bytes,p.tick);for(auto n:{p.phase,p.nodes,p.beams,p.flags})U32(bytes,n);
            D(bytes,p.dt);D(bytes,p.elapsed);V(bytes,p.position);V(bytes,p.velocity);
            U64(bytes,p.fingerprint);U32(bytes,p.sampled);U32(bytes,p.initialized);V(bytes,p.origin);
            if(p.tick%10==0)summaries<<std::setprecision(17)<<"{\"tick\":"<<p.tick<<",\"timeSeconds\":"<<p.tick*p.dt
                <<",\"probeOnly\":true,\"positionXM\":"<<p.position.x<<",\"positionYM\":"<<p.position.y
                <<",\"sentinelSpeedMps\":"<<p.velocity.Norm()<<",\"physicsStepElapsedUs\":"<<p.elapsed
                <<",\"flags\":"<<p.flags<<",\"dropped\":"<<m_probe_dropped.load()<<"}\n";
        }
        if(count){
            std::vector<unsigned char> block;U32(block,static_cast<std::uint32_t>(count));
            U32(block,static_cast<std::uint32_t>(bytes.size()));U32(block,Crc32(bytes.data(),bytes.size()));
            m_probe_health.encode_ns+=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-encodeStart).count();
            const auto writeStart=std::chrono::steady_clock::now();
            ok=std::fwrite("DATA",1,4,f)==4&&std::fwrite(block.data(),1,block.size(),f)==block.size()&&
                std::fwrite(bytes.data(),1,bytes.size(),f)==bytes.size()&&std::fwrite("DONE",1,4,f)==4;
            m_probe_health.write_ns+=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-writeStart).count();
            if(!ok)m_probe_error=true;else {pending+=count;m_probe_health.written+=count;m_probe_health.bytes+=bytes.size()+20;}
            const auto now=std::chrono::steady_clock::now();
            if(syncSchedule.Due(now)||m_stop.load()){
                if(sync()){m_probe_written+=pending;pending=0;}else m_probe_error=true;syncSchedule.Completed(std::chrono::steady_clock::now());
                progress();
            }
            summaries.flush();if(!summaries)m_probe_error=true;
            m_probe_tail.store(tail+count,std::memory_order_release);
        }else std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
    if(sync())m_probe_written+=pending;else m_probe_error=true;
    std::vector<unsigned char> footer;U64(footer,m_probe_written.load());U64(footer,m_probe_dropped.load());U32(footer,m_probe_error.load()?1:0);
    if(std::fwrite("END!",1,4,f)!=4||std::fwrite(footer.data(),1,footer.size(),f)!=footer.size()||!sync())m_probe_error=true;
    if(std::fclose(f)!=0)m_probe_error=true;
    m_probe_health.closed=true;
    progress();
    std::ofstream health(m_root+"/probe-health.json");
    health<<"{\"records\":"<<m_probe_written.load()<<",\"dropped\":"<<m_probe_dropped.load()<<",\"ioError\":"<<(m_probe_error.load()?"true":"false")<<"}\n";
}
}} // namespace
