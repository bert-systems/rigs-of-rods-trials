// SPDX-License-Identifier: GPL-3.0-or-later
#include "../../source/main/trials/TrialDetail.h"
#include <iostream>
#include <chrono>
#include <cstdlib>
using namespace RoR::Trials;
void Check(bool b,const char* message){if(!b){std::cerr<<message<<"\n";std::exit(1);}}
std::uint32_t Bitwise(const unsigned char* p,std::size_t n){
    std::uint32_t crc=0xffffffffu;
    for(std::size_t i=0;i<n;++i){crc^=p[i];for(int k=0;k<8;++k)crc=(crc>>1)^(0xedb88320u&(0u-(crc&1u)));}
    return ~crc;
}
std::uint32_t ByteTable(const unsigned char* p,std::size_t n){
    static const auto t=[](){std::array<std::uint32_t,256> t{};for(unsigned i=0;i<256;++i){auto v=i;for(int k=0;k<8;++k)v=(v>>1)^(0xedb88320u&(0u-(v&1u)));t[i]=v;}return t;}();
    auto crc=0xffffffffu;for(std::size_t i=0;i<n;++i)crc=(crc>>8)^t[(crc^p[i])&255];return ~crc;
}
int main(int argc,char**){
    std::vector<unsigned char> payload(131080);
    for(std::size_t i=0;i<payload.size();++i)payload[i]=static_cast<unsigned char>((i*197+i/17)&255);
    for(unsigned offset=0;offset<8;++offset)for(unsigned n=0;n<1025;++n)
        Check(Crc32(payload.data()+offset,n)==Bitwise(payload.data()+offset,n),"unaligned CRC/tail differs from independent bitwise reference");
    Check(Crc32(payload.data(),131072)==Bitwise(payload.data(),131072),"dense frame CRC reference");
    const auto stride=128+176*256+744*112+736*104;
    std::vector<unsigned char> src(stride),dst(stride,0xa5);
    for(std::size_t i=128;i<src.size();++i)src[i]=static_cast<unsigned char>(i*31);
    auto& h=*reinterpret_cast<DetailHeader*>(src.data());h=DetailHeader{};h.nodes=176;h.beams=744;
    for(unsigned contacts:{736u,0u,1u,32u,735u,0u}){
        h.contacts=contacts;const auto used=DetailFrameBytes(h);
        std::fill(dst.begin(),dst.end(),0xa5);CopyDetailFrame(dst.data(),src.data());
        Check(std::memcmp(src.data(),dst.data(),used)==0,"populated detail prefix changed");
        for(std::size_t i=used;i<dst.size();++i)Check(dst[i]==0xa5,"copy touched reserved contact tail");
        Check(Crc32(dst.data(),used)==Bitwise(src.data(),used),"stale unused tails contaminated frame CRC");
    }
    RecorderHealth health;health.Admit(3,100);health.Admit(1,200);health.written=9;health.Synced(11000);health.Synced(2000);
    const std::chrono::steady_clock::time_point zero{};SyncSchedule schedule(zero);
    Check(!schedule.Due(zero+std::chrono::milliseconds(249))&&schedule.Due(zero+std::chrono::milliseconds(250)),"nominal sync interval boundary");
    // A flush starts at 250 ms and blocks until 1250 ms. The following frame
    // must get a full new interval rather than immediately forcing another flush.
    schedule.Completed(zero+std::chrono::milliseconds(1250));
    Check(!schedule.Due(zero+std::chrono::milliseconds(1251))&&!schedule.Due(zero+std::chrono::milliseconds(1499))&&schedule.Due(zero+std::chrono::milliseconds(1500)),"slow synchronization cannot cascade into every-frame flushes");
    Check(health.high_water==3&&health.copied_bytes==300&&health.sync_calls==2&&health.max_sync_ns==11000,"queue maxima/byte/sync diagnostics");
    const auto json=health.Json(10,8,7,20,100,1,true);
    Check(json.find("\"pendingSync\":2")!=std::string::npos&&json.find("\"queued\":2")!=std::string::npos,"write-sync and queue counters kept distinct");
    std::cout<<"PASS: unaligned CRC, all tails, populated detail/ring prefixes and separate queue/durability diagnostics\n";
    if(argc>1){
        volatile std::uint32_t guard=0;std::array<double,3> old{},now{};
        for(unsigned repeat=0;repeat<3;++repeat){
            auto start=std::chrono::steady_clock::now();for(int i=0;i<500;++i)guard=ByteTable(payload.data(),131072);
            old[repeat]=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
            start=std::chrono::steady_clock::now();for(int i=0;i<500;++i)guard=Crc32(payload.data(),131072);
            now[repeat]=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
        }
        std::cout<<"{\"bytesPerRepeat\":65536000,\"byteTableMs\":["<<old[0]<<","<<old[1]<<","<<old[2]<<"],\"slicing8Ms\":["<<now[0]<<","<<now[1]<<","<<now[2]<<"],\"guard\":"<<guard<<"}\n";
    }
}
