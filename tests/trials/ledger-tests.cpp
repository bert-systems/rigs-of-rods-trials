// SPDX-License-Identifier: GPL-3.0-or-later
#include "../../source/main/trials/TrialLedger.h"
#include <cstdlib>
#include <iostream>
#include <limits>
using namespace RoR::Trials;
void Check(bool ok, const char* message) { if (!ok) { std::cerr << message << "\n"; std::exit(1); } }
bool Near(double a, double b, double abs=1e-9) { return std::abs(a-b) <= abs; }
int main()
{
    Ledger ledger;
    ledger.Begin(17, 3, 1, 0.5);
    // Independent impulse/energy example: 2 kg, +4 N for 0.5 s, v: 3 -> 4.
    ledger.Observe(2, Vec(5,0,0), Vec(3,0,0), Vec(4,0,0), Vec(4,0,0), Vec(1,0,0));
    Record r=ledger.Finish();
    Check(r.tick==17 && r.actor==3 && r.nodes==1, "identity");
    Check(Near(r.momentum.x,8) && Near(r.kinetic_before,9) && Near(r.kinetic,16), "mass weighted momentum/energy");
    Check(Near(r.work,7) && Near(r.work_residual,0) && Near(r.momentum_residual.Norm(),0), "independent work/impulse closure");
    Check(Near(r.center.x,5) && Near(r.contact_force.x,1), "center/contact");
    ledger.Begin(18,3,1,0.5);
    ledger.Observe(2,Vec(0,0,0),Vec(3,0,0),Vec(4.1,0,0),Vec(4,0,0),Vec());
    r=ledger.Finish();
    Check(r.momentum_residual.x>0.19 && r.work_residual>0.6, "state mutation must remain a residual");
    ledger.Begin(19,3,1,0.5);
    ledger.Observe(0,Vec(),Vec(),Vec(),Vec(),Vec());
    Check(ledger.Finish().flags==1, "invalid mass must flag quality");
    ledger.Begin(20,3,1,0.5);
    ledger.Observe(1,Vec(0,0,0),Vec(),Vec(),Vec(),Vec());
    ledger.Observe(3,Vec(4,0,0),Vec(),Vec(),Vec(),Vec());
    Check(Near(ledger.Finish().center.x,3), "center must be mass weighted");
    ledger.Begin(21,3,1,0.5);
    ledger.Observe(2,Vec(std::numeric_limits<double>::quiet_NaN(),0,0),Vec(),Vec(),Vec(),Vec());
    Check((ledger.Finish().flags&1)!=0,"nonfinite position must invalidate observation");
    const unsigned char crc[]={'1','2','3','4','5','6','7','8','9'};
    Check(Crc32(crc,9)==0xcbf43926u,"standard CRC-32 check vector");
    std::cout << "PASS: independent ledger identities, detectable mutation, invalid mass, weighted COM, CRC32\n";
}
