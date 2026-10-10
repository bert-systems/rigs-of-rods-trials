// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <atomic>
#include <algorithm>
#include <cstdint>
#include <sstream>
#include <iomanip>
#include <chrono>
namespace RoR { namespace Trials {
class SyncSchedule {
    using Clock=std::chrono::steady_clock;
    Clock::time_point m_completed;
public:
    explicit SyncSchedule(Clock::time_point now=Clock::now()):m_completed(now){}
    bool Due(Clock::time_point now) const {return now-m_completed>=std::chrono::milliseconds(250);}
    void Completed(Clock::time_point now){m_completed=now;}
};
// Queue counters have one producer. Recorder timings/counters have one writer.
// JSON is constructed only on the joined main thread or recorder thread.
// Atomic snapshots are independently sampled diagnostics, not integrity proof.
struct RecorderHealth {
    std::atomic<std::uint64_t> high_water{0},copied_bytes{0},written{0},bytes{0},sync_calls{0};
    std::atomic<std::uint64_t> encode_ns{0},write_ns{0},sync_ns{0},max_sync_ns{0};
    std::atomic<bool> closed{false};
    void Admit(std::uint64_t queued,std::uint64_t copied) {
        if(queued>high_water.load(std::memory_order_relaxed))high_water.store(queued,std::memory_order_relaxed);
        copied_bytes.store(copied_bytes.load(std::memory_order_relaxed)+copied,std::memory_order_relaxed);
    }
    void Synced(std::uint64_t ns) {
        ++sync_calls;sync_ns+=ns;
        if(ns>max_sync_ns.load())max_sync_ns=ns;
    }
    std::string Json(std::uint64_t head,std::uint64_t tail,std::uint64_t durable,std::uint64_t capacity,
        std::uint64_t stride,std::uint64_t dropped,bool error) const {
        const auto w=written.load(); // durable argument was sampled first
        std::ostringstream s;s<<std::setprecision(17)<<"{\"schema\":1,\"enqueued\":"<<head<<",\"processed\":"<<tail
            <<",\"queued\":"<<(head>=tail?head-tail:0)<<",\"capacity\":"<<capacity<<",\"highWater\":"<<high_water.load()
            <<",\"reservedQueueBytes\":"<<capacity*stride<<",\"copiedBytes\":"<<copied_bytes.load()
            <<",\"written\":"<<w<<",\"durable\":"<<durable<<",\"pendingSync\":"<<(w>=durable?w-durable:0)
            <<",\"archiveBytes\":"<<bytes.load()<<",\"dropped\":"<<dropped<<",\"ioError\":"<<(error?"true":"false")
            <<",\"closed\":"<<(closed.load()?"true":"false")<<",\"syncCalls\":"<<sync_calls.load()
            <<",\"encodeCrcWallUs\":"<<encode_ns.load()/1000.0<<",\"fileWriteWallUs\":"<<write_ns.load()/1000.0
            <<",\"syncWallUs\":"<<sync_ns.load()/1000.0<<",\"maxSyncWallUs\":"<<max_sync_ns.load()/1000.0<<"}";
        return s.str();
    }
};
}}
