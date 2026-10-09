namespace RoR.Trials;

// Independent, double-precision, one-dimensional reference to the existing native constitutive
// rules, including its initialization prime and kick-drift epochs. This validates capture and
// implementation agreement, not the calibration of physical material failure or dissipation.
public static class TransitionValidation
{
    public static FixtureValidation.Result Evaluate(string path,ExperimentDefinition d)
    {
        const string scope="beam-transition-reference-v1: pinned dry 100 kg/one-beam native law, storage ports and force epochs; material fracture dissipation and vehicles unqualified";
        var checks=new List<FixtureValidation.Item>();
        void Max(string name,double value,double limit)=>checks.Add(new(name,value,limit,double.IsFinite(value)&&value<=limit));
        bool yield=d.Scenario.StartsWith("yield-",StringComparison.Ordinal),compression=d.Scenario=="yield-compression-v1",
            protect=d.Scenario=="protected-beam-v1",active=true,first=true;
        double x=compression?.95:1.05,v=0,rest=1,strength=yield?2000:200,posYield=yield?200:1e9,negYield=-posYield,minStress=200;
        double force=0,time=0,maxPosition=0,maxVelocity=0,maxForce=0,maxStorage=0,maxPort=0,maxState=0,maxUnknown=0,
            maxAttribution=0,maxImpulse=0,maxWork=0,maxMutation=0,maxForeign=0,maxClosure=0,maxMass=0,maxConsumed=0,maxEventStorage=0,energy0=0,ports=0,work=0;
        long records=0,events=0,parameterEvents=0,strengthEvents=0,removals=0;int mismatches=0;
        double Law(){
            if(!active)return 0;
            double extension=x-rest,stress=-10000*extension,applied=stress,len=Math.Abs(stress);
            if(len>minStress){
                if(yield&&stress>posYield&&extension<0){
                    double old=rest;rest+=extension+posYield/10000*.75;applied=(stress+posYield)*.5;len=applied;
                    posYield*=old/rest;minStress=Math.Min(posYield,-negYield);minStress=Math.Min(minStress,strength);
                }else if(yield&&stress<negYield&&extension>0){
                    double old=rest,deform=extension+negYield/10000*.75;rest+=deform;
                    applied=(stress+negYield)*.5;len=-applied;negYield*=rest/old;
                    minStress=Math.Min(posYield,-negYield);minStress=Math.Min(minStress,strength);strength-=deform*10000;
                }
                if(len>strength){if(protect)strength=2*minStress;else{active=false;applied=0;}}
            }
            return applied;
        }
        foreach(var r in ArchiveReader.VerifiedRecords(path)){
            double At(int n)=>BitConverter.ToDouble(r,n);uint flags=BitConverter.ToUInt32(r,20);
            if(BitConverter.ToUInt32(r,12)!=1||BitConverter.ToUInt32(r,16)!=1||(flags&5)!=0||
                BitConverter.ToUInt32(r,1348)!=4||BitConverter.ToUInt32(r,1344)!=0||BitConverter.ToUInt32(r,1372)!=0)
                return new("NotReady",scope,checks);
            double dt=At(24),oldRest=rest,oldStrength=strength;bool oldActive=active;
            if(first){
                if((flags&2)==0)return new("NotReady",scope,checks);
                Max("pinned initial storage / J",Math.Abs(At(1152)-12.5),.0001);
                Max("pinned initial kinetic energy / J",Math.Abs(At(136)),1e-8);
                energy0=At(136)+At(1152);force=Law();
            }else if((flags&2)!=0)return new("NotReady",scope,checks);
            maxConsumed=Math.Max(maxConsumed,Math.Abs(At(88)-force));
            maxMass=Math.Max(maxMass,Math.Abs(At(32)-100));
            if(BitConverter.ToUInt64(r,1352)!=BitConverter.ToUInt64(r,0)-1||BitConverter.ToUInt64(r,1360)!=BitConverter.ToUInt64(r,0))++mismatches;
            v+=force/100*dt;x+=v*dt;force=Law();time+=dt;++records;
            maxPosition=Math.Max(maxPosition,Math.Abs(At(40)-500-x));maxVelocity=Math.Max(maxVelocity,Math.Abs(At(64)/100-v));
            maxForce=Math.Max(maxForce,Math.Abs(At(440)+At(496)+At(552)-force));
            maxStorage=Math.Max(maxStorage,Math.Abs(At(1160)-(active?5000*(x-rest)*(x-rest):0)));
            uint kind=(rest!=oldRest?1u:0)|(oldActive&&!active?2u:0)|(strength!=oldStrength?4u:0);
            uint count=BitConverter.ToUInt32(r,1368);if(count!=(kind==0?0:1))++mismatches;
            double expectedRest=kind%2==1?5000*((x-rest)*(x-rest)-(x-oldRest)*(x-oldRest)):0;
            double expectedRemoved=(kind&2)!=0?-5000*(x-rest)*(x-rest):0;
            maxPort=Math.Max(maxPort,Math.Abs(At(1232)-expectedRest)+Math.Abs(At(1240)-expectedRemoved));
            for(int i=0;i<count;i++){
                int at=1376+i*88;uint actualKind=BitConverter.ToUInt32(r,at+4);
                if(actualKind!=kind||BitConverter.ToUInt32(r,at)!=0)++mismatches;
                maxState=Math.Max(maxState,Math.Abs(At(at+16)-oldRest)+Math.Abs(At(at+24)-rest));
                maxState=Math.Max(maxState,Math.Abs(At(at+48)-oldStrength)+Math.Abs(At(at+56)-strength));
                maxEventStorage=Math.Max(maxEventStorage,Math.Abs(At(at+64)-5000*(x-oldRest)*(x-oldRest))+
                    Math.Abs(At(at+72)-5000*(x-rest)*(x-rest)));
                if(At(at+32)!=10000||At(at+40)!=10000)++mismatches;
                ++events;if((actualKind&1)!=0)++parameterEvents;if((actualKind&4)!=0)++strengthEvents;if((actualKind&2)!=0)++removals;
            }
            maxUnknown=Math.Max(maxUnknown,At(1216));maxAttribution=Math.Max(maxAttribution,At(1224));
            maxImpulse=Math.Max(maxImpulse,Math.Sqrt(At(160)*At(160)+At(168)*At(168)+At(176)*At(176)));
            maxWork=Math.Max(maxWork,Math.Abs(At(184)));maxMutation=Math.Max(maxMutation,Math.Abs(At(1192)));
            foreach(int c in new[]{0,1,2,4,6,7,8,9,10,11,12,13,14,15})maxForeign=Math.Max(maxForeign,Math.Abs(At(240+c*56+24)));
            ports+=At(1232)+At(1240);work+=At(1176);
            maxClosure=Math.Max(maxClosure,Math.Abs(At(144)+At(1160)-energy0-ports-work));first=false;
        }
        if(first)return new("NotReady",scope,checks);
        Max("expected one native transition",Math.Abs(events-1),0);
        Max("expected parameter transitions",Math.Abs(parameterEvents-(yield?1:0)),0);
        Max("expected strength transitions",Math.Abs(strengthEvents-(d.Scenario=="yield-tension-v1"||protect?1:0)),0);
        Max("expected removed beams",Math.Abs(removals-(d.Scenario=="fracture-v1"?1:0)),0);
        Max("transition tick/kind/beam mismatches",mismatches,0);
        // COM uses float32 world coordinates near x=500: half an ULP is ~1.53e-5 m.
        // The 5e-5 m envelope also admits accumulated local float32 integration roundoff.
        Max("reference world-coordinate position discrepancy / m",maxPosition,5e-5);
        Max("reference velocity discrepancy / m/s",maxVelocity,.001);
        Max("reference generated applied force discrepancy / N",maxForce,.05);
        Max("reference consumed applied force discrepancy / N",maxConsumed,.05);
        Max("pinned moving mass discrepancy / kg",maxMass,.001);
        Max("reference elastic storage discrepancy / J",maxStorage,.001);
        Max("reference rest/removal storage port discrepancy / J",maxPort,.001);
        Max("reference event old/new storage discrepancy / J",maxEventStorage,.001);
        Max("reference rest/strength state discrepancy",maxState,.002);
        Max("core closure envelope with declared ports / J",maxClosure,.1);
        Max("unattributed node force L1 / N",maxUnknown,1e-5);Max("force reconstruction L1 / N",maxAttribution,1e-5);
        Max("integration impulse discrepancy / kg m/s",maxImpulse,1e-3);Max("kinetic midpoint-work discrepancy / J",maxWork,1e-3);
        Max("uncommanded state energy / J",maxMutation,.001);Max("foreign channel work / J",maxForeign,1e-8);
        Max("simulated duration error / s",Math.Abs(time-d.DurationSeconds),.001);
        return new(checks.All(c=>c.Passed)?"Passed":"Failed",scope,checks);
    }
}
