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
    ledger.Prepare(2,1);
    ledger.Begin(22,3,1,.5);
    ledger.Reset(0,Vec(),true);ledger.Reset(1,Vec(),true);
    ledger.Add(0,BeamElastic,Vec(4,0,0),true);
    ledger.Add(0,BeamDamping,Vec(-1,0,0),true);
    ledger.Consume(0,2,Vec(3,0,0),Vec(3.75,0,0),Vec(3,0,0),Vec(),false);
    Check(Near(ledger.record.channels[BeamElastic].work,6.75),"channel work uses integration midpoint");
    Check(Near(ledger.record.attribution_residual_l1,0),"channels reconstruct actual force");
    ledger.Begin(23,3,1,.5);
    ledger.Reset(0,Vec(),true);ledger.Reset(1,Vec(),true);
    ledger.Consume(0,2,Vec(),Vec(),Vec(7,0,0),Vec(),false);
    ledger.Consume(1,2,Vec(),Vec(),Vec(-7,0,0),Vec(),false);
    Check(Near(ledger.record.unattributed_l1,14),"opposing unattributed forces cannot cancel coverage gap");
    ledger.Begin(24,3,1,.5);
    BeamTransition transition;transition.kind=3;transition.oldStorage=9;transition.newStorage=4;
    ledger.Transition(transition);
    Check(Near(ledger.record.rest_storage_port,-5)&&Near(ledger.record.removed_storage_port,-4),"rest change plus break does not remove storage twice");
    for(int j=0;j<8;j++)ledger.Transition(transition);
    Check(ledger.record.event_count==8&&ledger.record.event_dropped==1&&(ledger.record.flags&1),"required event overflow sticky");
    ledger.Begin(25,3,1,.5);
    ledger.Consume(1,2,Vec(),Vec(),Vec(),Vec(),true);
    ledger.Begin(26,3,1,.5);
    ledger.Consume(1,2,Vec(),Vec(),Vec(),Vec(),false);
    Check((ledger.record.flags&4)!=0,"fixed/movable cohort exchange remains unqualified");
    const unsigned char crc[]={'1','2','3','4','5','6','7','8','9'};
    Check(Crc32(crc,9)==0xcbf43926u,"standard CRC-32 check vector");
    std::cout << "PASS: independent ledger identities, detectable mutation, invalid mass, weighted COM, CRC32\n";
}
