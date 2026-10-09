// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace RoR { namespace Trials {

struct Vec
{
    double x = 0, y = 0, z = 0;
    Vec() = default;
    Vec(double a, double b, double c): x(a), y(b), z(c) {}
    Vec operator+(Vec v) const { return Vec(x+v.x, y+v.y, z+v.z); }
    Vec operator-(Vec v) const { return Vec(x-v.x, y-v.y, z-v.z); }
    Vec operator*(double s) const { return Vec(x*s, y*s, z*s); }
    Vec& operator+=(Vec v) { x+=v.x; y+=v.y; z+=v.z; return *this; }
    double Dot(Vec v) const { return x*v.x + y*v.y + z*v.z; }
    bool Finite() const { return std::isfinite(x) && std::isfinite(y) && std::isfinite(z); }
    double Norm() const { return std::sqrt(Dot(*this)); }
};

// Serialized field by field, little endian. No native struct padding in archives.
struct Record
{
    std::uint64_t tick = 0;
    std::uint32_t actor = 0, nodes = 0, phase = 0, flags = 0;
    double dt = 0, mass = 0;
    Vec center, momentum, force, contact_force;
    double kinetic_before = 0, kinetic = 0, work = 0;
    Vec momentum_residual;
    double work_residual = 0, peak_node_force = 0, gravity = 0, density = 0;
    Vec wind;
};

class Ledger
{
public:
    bool enabled = false;
    Record record;
    void Begin(std::uint64_t tick, std::uint32_t actor, std::uint32_t phase, double dt)
    {
        record = Record();
        record.tick = tick; record.actor = actor; record.phase = phase; record.dt = dt;
    }
    void Observe(double mass, Vec position, Vec before, Vec after, Vec force, Vec contact)
    {
        if (!(mass > 0) || !std::isfinite(mass) || !position.Finite() || !before.Finite() || !after.Finite() || !force.Finite() || !contact.Finite()) { record.flags |= 1; return; }
        ++record.nodes;
        record.mass += mass;
        record.center += position * mass;
        record.momentum += after * mass;
        record.force += force;
        record.contact_force += contact;
        const double kb = 0.5 * mass * before.Dot(before);
        const double ka = 0.5 * mass * after.Dot(after);
        const double w = ((before + after) * 0.5).Dot(force * record.dt);
        record.kinetic_before += kb; record.kinetic += ka; record.work += w;
        record.momentum_residual += (after - before) * mass - force * record.dt;
        record.work_residual += ka - kb - w;
        const double peak = force.Norm();
        if (peak > record.peak_node_force) record.peak_node_force = peak;
        if (!std::isfinite(ka) || !std::isfinite(w) || !std::isfinite(peak)) record.flags |= 1;
    }
    Record Finish()
    {
        if (record.mass > 0) record.center = record.center * (1.0 / record.mass);
        return record;
    }
};

inline std::uint32_t Crc32(const unsigned char* bytes, std::size_t size)
{
    std::uint32_t crc = 0xffffffffu;
    for (std::size_t i=0; i<size; ++i)
    {
        crc ^= bytes[i];
        for (int bit=0; bit<8; ++bit) crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}

}} // namespace RoR::Trials
