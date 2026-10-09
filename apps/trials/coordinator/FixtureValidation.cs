namespace RoR.Trials;

// Qualification is limited to a pinned, one-moving-node, dry analytical fixture.
// Reference math is double precision kick-drift, separate from native observer formulas.
public static class FixtureValidation
{
    public sealed record Item(string Name,double Observed,double Limit,bool Passed);
    public sealed record Result(string Status,string Scope,List<Item> Checks);
    public static Result Evaluate(string path,ExperimentDefinition d,ArchiveReader.Check capture,bool executionComplete)
    {
        const string scope="Pinned dry one-node native fixture with precise beam lengths only; excludes vehicle, contact, impact, nonlinear beams and flight";
        if(d.Observation=="off")return new("NotReady","Ledger disabled; control probe only, no force/energy qualification",[]);
        if(d.Scenario is "coast-v1" or "barrier-v1")return new("NotReady","Vehicle constitutive/storage and environment qualification pending",[]);
        if(!executionComplete||!capture.Complete||!d.Accounting)return new("NotReady",scope,[]);
        var checks=new List<Item>();
        void Max(string name,double value,double limit)=>checks.Add(new(name,value,limit,double.IsFinite(value)&&value<=limit));
        double time=0,refX=0,refV=0,x0=0,initialEnergy=0,energy0=0,workSum=0;
        double maxPosition=0,maxVelocity=0,maxMass=0,maxEnergyEnvelope=0,maxClosure=0,maxUnknown=0,maxUnclosed=0,maxMutation=0;
        double maxAttribution=0,maxImpulse=0,maxWork=0,maxForeignWork=0,maxFixedWork=0;long steps=0;
        bool initialized=false;double g=d.Environment!.Gravity,damper=d.Scenario=="damper-v1"?200:0;
        foreach(var r in ArchiveReader.VerifiedRecords(path)){
            double At(int offset)=>BitConverter.ToDouble(r,offset);
            uint flags=BitConverter.ToUInt32(r,20);
            if(BitConverter.ToUInt32(r,12)!=1 || BitConverter.ToUInt32(r,16)!=1 || (flags&4)!=0)
                return new("NotReady",scope,checks);
            double dt=At(24),mass=At(32);
            if(!initialized){
                if((flags&2)==0)return new("NotReady",scope,checks);
                x0=d.Scenario=="freefall-v1"?20:Math.Sqrt(2*At(1152)/10000);
                refX=x0;refV=0;initialEnergy=At(1152);energy0=At(136)+At(1136)+At(1152);
                Max("pinned initial kinetic energy / J",Math.Abs(At(136)),1e-6);
                Max("prepared four-node fixture",Math.Abs(BitConverter.ToUInt32(r,1348)-4.0),0);
                if(d.Scenario!="freefall-v1"){
                    Max("pinned initial extension error / m",Math.Abs(x0-.05),1e-5);
                    Max("pinned initial spring stiffness response / N",Math.Abs(At(408)+10000*x0),.1);
                }
                initialized=true;
            }else if((flags&2)!=0)return new("NotReady",scope,checks);
            time+=dt;++steps;
            double foreignWork=0;
            foreach(int channel in new[]{1,2,6,7,8,9,10,11,12,13,14,15})foreignWork+=Math.Abs(At(240+channel*56+24));
            maxForeignWork=Math.Max(maxForeignWork,foreignWork);
            if(d.Scenario=="freefall-v1")maxFixedWork=Math.Max(maxFixedWork,Math.Abs(At(1152))+Math.Abs(At(1160)));
            double acceleration=d.Scenario=="freefall-v1"?g:(-10000*refX-damper*refV)/100;
            refV+=acceleration*dt;refX+=refV*dt;
            double actualX=d.Scenario=="freefall-v1"?At(48):At(40)-501;
            double actualV=(d.Scenario=="freefall-v1"?At(72):At(64))/mass;
            maxPosition=Math.Max(maxPosition,Math.Abs(actualX-refX));
            maxVelocity=Math.Max(maxVelocity,Math.Abs(actualV-refV));
            maxMass=Math.Max(maxMass,Math.Abs(mass-100));
            double mechanical=At(144)+At(1144)+At(1160);
            workSum+=At(1176)+At(1232)+At(1240);
            double expectedDrift=d.Scenario=="freefall-v1"?-.5*100*g*g*dt*dt*steps:0;
            maxClosure=Math.Max(maxClosure,Math.Abs(mechanical-energy0-workSum-expectedDrift));
            if(d.Scenario=="spring-v1")maxEnergyEnvelope=Math.Max(maxEnergyEnvelope,Math.Abs(mechanical-initialEnergy));
            maxUnknown=Math.Max(maxUnknown,At(1216));maxAttribution=Math.Max(maxAttribution,At(1224));
            maxUnclosed=Math.Max(maxUnclosed,BitConverter.ToUInt32(r,1344));maxMutation=Math.Max(maxMutation,Math.Abs(At(1192)));
            maxImpulse=Math.Max(maxImpulse,Math.Sqrt(At(160)*At(160)+At(168)*At(168)+At(176)*At(176)));
            maxWork=Math.Max(maxWork,Math.Abs(At(184)));
        }
        if(!initialized)return new("NotReady",scope,checks);
        Max("extraneous force-channel work / J",maxForeignWork,1e-8);
        if(d.Scenario=="freefall-v1")Max("freefall elastic storage / J",maxFixedWork,0);
        Max("one moving node mass error / kg",maxMass,.001);
        Max("native versus independent kick-drift position / m",maxPosition,.003);
        Max("native versus independent kick-drift velocity / m/s",maxVelocity,.04);
        Max("core closure after known freefall discretization / J",maxClosure,.3);
        if(d.Scenario=="spring-v1")Max("undamped energy envelope / J",maxEnergyEnvelope,.3);
        Max("unattributed node force L1 / N",maxUnknown,1e-5);
        Max("force reconstruction L1 / N",maxAttribution,1e-5);
        Max("unqualified active storage elements",maxUnclosed,0);
        Max("uncommanded state-change energy / J",maxMutation,.001);
        Max("integration impulse discrepancy / kg m/s",maxImpulse,1e-3);
        Max("kinetic midpoint-work discrepancy / J",maxWork,1e-3);
        Max("simulated duration error / s",Math.Abs(time-d.DurationSeconds),.001);
        if(d.Scenario=="damper-v1")Max("damping work must be dissipative / J",capture.Accounting.GetValueOrDefault("work.beamDamping.J"),0);
        return new(checks.All(c=>c.Passed)?"Passed":"Failed",scope,checks);
    }
}
