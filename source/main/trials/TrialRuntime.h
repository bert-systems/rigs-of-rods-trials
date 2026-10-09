// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "TrialLedger.h"
#include <atomic>
#include <chrono>
#include <string>
#include <thread>
#include <vector>
namespace RoR {
class Actor;
class ActorManager;
namespace Trials {
class Runtime
{
public:
    static Runtime& Get();
    bool Enabled() const { return m_enabled; }
    bool Released() const { return m_released; }
    std::uint64_t Tick() const { return m_tick; }
    void BeginStep(Actor& actor);
    void FinishStep(Actor& actor);
    void Poll(ActorManager& manager);
    void Stop();
    bool HasEnvironment() const { return m_enabled; }
    double Density() const { return m_density; }
    Vec Wind() const { return m_wind; }
private:
    Runtime();
    ~Runtime();
    void Writer();
    void Event(const std::string& name, std::uint64_t sequence=0);
    bool m_enabled = false, m_released = false, m_closed = false;
    std::string m_root;
    double m_speed = 0, m_gravity = -9.81, m_density = 1.225, m_duration = 12, m_settle = 3;
    Vec m_wind;
    std::uint64_t m_tick = 0, m_last_command = 0;
    std::vector<Record> m_queue;
    std::atomic<std::uint64_t> m_head{0}, m_tail{0}, m_dropped{0}, m_written{0};
    std::atomic<int> m_pilot_actor{-1};
    std::atomic<bool> m_scope_violation{false};
    std::atomic<bool> m_stop{false}, m_io_error{false};
    std::thread m_writer;
    std::chrono::steady_clock::time_point m_poll;
};
}}
