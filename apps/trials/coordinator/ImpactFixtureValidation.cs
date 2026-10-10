namespace RoR.Trials;

// Per-step constitutive/contact reference driven by recorded native inputs, plus
// independently reduced dense/aggregate parity. This is not a trajectory oracle
// or a calibration of real material fracture energy.
public static class ImpactFixtureValidation
{
    public sealed record Timeline(long FirstContactTick,long? FirstParameterTick,long? FirstStrengthTick,long? FirstRemovalTick,long ParameterChanges,long StrengthChanges,long Removed);
    public static Timeline ReadTimeline(string path,long trigger)
    {
        long? parameter=null,strength=null,removed=null;long pp=0,ss=0,rr=0;
        foreach(var r in ArchiveReader.VerifiedRecords(path))for(int i=0;i<BitConverter.ToUInt32(r,1368);++i){
            long tick=BitConverter.ToInt64(r,0);uint kind=BitConverter.ToUInt32(r,1380+i*88);
            if((kind&1)!=0){parameter??=tick;++pp;}if((kind&4)!=0){strength??=tick;++ss;}if((kind&2)!=0){removed??=tick;++rr;}
        }
        return new(trigger,parameter,strength,removed,pp,ss,rr);
    }
    public static FixtureValidation.Result Evaluate(string path,ExperimentDefinition d,ArchiveReader.Check aggregate,DetailReader.Check? detail,bool executionComplete)
    {
        const string scope="two-mass-impact-reference-v1: later native collision, local law/integration conformance and dense/aggregate force/storage parity; material dissipation and vehicles unqualified";
        var checks=new List<FixtureValidation.Item>();
        if(!Contract.ImpactFixture(d.Scenario)||Contract.Validate(d).Count!=0||!executionComplete||!aggregate.Complete||detail is not {Complete:true,Nodes:4,Beams:3})return new("NotReady",scope,checks);
        void Max(string name,double value,double limit)=>checks.Add(new(name,value,limit,double.IsFinite(value)&&value<=limit));
        try{
            var records=ArchiveReader.VerifiedRecords(path).ToDictionary(r=>BitConverter.ToInt64(r,0));
            double D(byte[] r,int at)=>BitConverter.ToDouble(r,at);
            double F(byte[] r,int at)=>BitConverter.ToSingle(r,at);
            uint U(byte[] r,int at)=>BitConverter.ToUInt32(r,at);
            long firstTransition=0,firstStrength=0,firstRemoval=0,firstContact=0;
            int mismatches=0;double state=0,law=0,contactLaw=0,velocity=0,position=0,parity=0,ports=0,unknown=0,impulse=0,work=0;
            bool yield=d.Scenario=="impact-yield-v1";
            double positive=yield?200:1e9,negative=-positive;byte[]? previous=null;
            var initial=records[1];
            Max("pinned initial kinetic energy / J",Math.Abs(D(initial,136)-2500),1e-6);
            Max("pinned initial rest storage / J",Math.Abs(D(initial,1152)),1e-6);
            Max("pinned initial velocity / m/s",Math.Abs(D(initial,64)/200-5),1e-6);
            Max("prepared moving cohort / nodes",Math.Abs(U(initial,12)-2.0)+Math.Abs(U(initial,1348)-4.0),0);
            foreach(var r in records.Values){
                long tick=BitConverter.ToInt64(r,0);
                if(U(r,1368)>0&&firstTransition==0)firstTransition=tick;
                for(int i=0;i<U(r,1368);++i){uint kind=U(r,1380+i*88);
                    if((kind&4)!=0&&firstStrength==0)firstStrength=tick;
                    if((kind&2)!=0&&firstRemoval==0)firstRemoval=tick;
                }
                if(U(r,12)!=2||U(r,1348)!=4||(U(r,20)&~2u)!=0||U(r,1344)!=0||U(r,1372)!=0||
                   BitConverter.ToUInt64(r,1352)!=(ulong)(tick-1)||BitConverter.ToUInt64(r,1360)!=(ulong)tick)++mismatches;
                unknown=Math.Max(unknown,D(r,1216)+D(r,1224));
                impulse=Math.Max(impulse,Math.Sqrt(D(r,160)*D(r,160)+D(r,168)*D(r,168)+D(r,176)*D(r,176)));
                work=Math.Max(work,Math.Abs(D(r,184)));
            }
            foreach(var frame in DetailReader.VerifiedFrames(Path.Combine(Path.GetDirectoryName(path)!,"detail.rort"))){
                long tick=BitConverter.ToInt64(frame,0);var r=records[tick];double dt=D(frame,8);
                if(Math.Abs(dt-.0005)>1e-10||U(frame,32)!=1||U(frame,16)!=U(r,8))++mismatches;
                const int beam=128+4*256;double length=F(frame,beam+16),oldRest=F(frame,beam+40),oldStrength=F(frame,beam+48);
                bool active=U(frame,beam+52)!=0,removed=active&&(U(frame,beam+12)&3)!=0;
                if(previous==null&&(oldRest!=1||oldStrength!=2000||!active))++mismatches;
                if(U(frame,beam+4)!=0||U(frame,beam+8)!=1||F(frame,beam+24)!=10000||F(frame,beam+28)!=0||F(frame,beam+44)!=10000)++mismatches;
                for(int disabled=1;disabled<3;++disabled){int at=beam+disabled*112;
                    if((U(frame,at+12)&3)!=1||U(frame,at+52)!=0)++mismatches;
                    for(int j=64;j<112;j+=4)law=Math.Max(law,Math.Abs(F(frame,at+j)));
                }
                if(previous!=null){
                    state=Math.Max(state,Math.Abs(oldRest-F(previous,beam+20)));
                    state=Math.Max(state,Math.Abs(oldStrength-F(previous,beam+36)));
                    if(active!=((U(previous,beam+12)&3)==0))++mismatches;
                }
                double rest=oldRest,strength=oldStrength,extension=length-oldRest,stress=-10000*extension,applied=active?stress:0;
                bool predictedRemoval=false;
                if(active){
                    double magnitude=Math.Abs(stress),threshold=Math.Min(positive,Math.Min(-negative,strength));
                    if(magnitude>threshold){
                        if(stress>positive&&extension<0){
                            rest=Math.Max(.1,oldRest+extension+positive/10000*.75);applied=(stress+positive)*.5;
                            magnitude=applied;positive*=oldRest/rest;
                        }else if(stress<negative&&extension>0){
                            double deform=extension+negative/10000*.75;rest+=deform;applied=(stress+negative)*.5;
                            magnitude=-applied;negative*=rest/oldRest;strength-=deform*10000;
                        }
                        if(magnitude>strength){predictedRemoval=true;applied=0;}
                    }
                    law=Math.Max(law,Math.Abs(F(frame,beam+32)-stress));
                }
                law=Math.Max(law,Math.Abs(F(frame,beam+64)-applied)+Math.Abs(F(frame,beam+76)+applied));
                state=Math.Max(state,Math.Abs(F(frame,beam+20)-rest));
                // Separate units/limits: strength uses newton-scale float rounding.
                contactLaw=Math.Max(contactLaw,Math.Abs(F(frame,beam+36)-strength));
                if(predictedRemoval!=removed)++mismatches;
                uint kind=(F(frame,beam+20)!=oldRest?1u:0)|(removed?2u:0)|(F(frame,beam+36)!=oldStrength?4u:0);
                if(U(r,1368)!=(kind==0?0:1))++mismatches;
                if(kind!=0){
                    if(U(r,1376)!=0||U(r,1380)!=kind)++mismatches;
                    double l=D(r,1384),ur=5000*(l-F(frame,beam+20))*(l-F(frame,beam+20)),uo=5000*(l-oldRest)*(l-oldRest);
                    state=Math.Max(state,Math.Abs(l-length));
                    if(D(r,1408)!=10000||D(r,1416)!=10000)++mismatches;
                    law=Math.Max(law,Math.Abs(D(r,1456)-F(frame,beam+32)));
                    ports=Math.Max(ports,Math.Abs(D(r,1232)-((kind&1)!=0?ur-uo:0))+Math.Abs(D(r,1240)-((kind&2)!=0?-ur:0)));
                    ports=Math.Max(ports,Math.Abs(D(r,1440)-uo)+Math.Abs(D(r,1448)-ur));
                    state=Math.Max(state,Math.Abs(D(r,1392)-oldRest)+Math.Abs(D(r,1400)-F(frame,beam+20)));
                    contactLaw=Math.Max(contactLaw,Math.Abs(D(r,1424)-oldStrength)+Math.Abs(D(r,1432)-F(frame,beam+36)));
                }
                double[] sumForce=new double[3],sumMomentum=new double[3],sumContact=new double[3];double kinetic=0;
                for(int node=0;node<4;++node){int at=128+node*256;bool moving=node<2;
                    if(U(frame,at)!=node||U(frame,at+4)!=(moving?0:1)||F(frame,at+8)!=(moving?100:1))++mismatches;
                    for(int j=0;j<3;++j){double before=F(frame,at+28+j*4),after=F(frame,at+40+j*4),force=F(frame,at+52+j*4),channels=0;
                        for(int c=0;c<16;++c)channels+=F(frame,at+64+c*12+j*4);
                        for(int c=0;c<16;++c)if(c is not (2 or 3 or 4 or 5 or 15))law=Math.Max(law,Math.Abs(F(frame,at+64+c*12+j*4)));
                        law=Math.Max(law,Math.Abs(force-channels));
                        if(moving){velocity=Math.Max(velocity,Math.Abs(after-before-force/100*dt));sumForce[j]+=force;sumMomentum[j]+=100*after;kinetic+=50*after*after;
                            sumContact[j]+=F(frame,at+64+2*12+j*4);
                            if(previous!=null){velocity=Math.Max(velocity,Math.Abs(before-F(previous,at+40+j*4)));
                                position=Math.Max(position,Math.Abs(F(frame,at+16+j*4)-F(previous,at+16+j*4)-after*dt));}
                            if(previous!=null&&j==0){double carried=F(frame,at+64+3*12)+F(frame,at+64+4*12)+F(frame,at+64+5*12);
                                law=Math.Max(law,Math.Abs(carried-F(previous,beam+64+node*12)));}
                        }
                    }
                }
                for(int j=0;j<3;++j)parity=Math.Max(parity,Math.Abs(sumForce[j]-D(r,88+j*8))+Math.Abs(sumMomentum[j]-D(r,64+j*8))+Math.Abs(sumContact[j]-D(r,112+j*8)));
                parity=Math.Max(parity,Math.Abs(kinetic-D(r,144)));
                int contacts=checked((int)U(frame,28));
                for(int i=0;i<contacts;++i){int at=beam+3*112+i*104;
                    if(U(frame,at+4)!=2||U(frame,at+12)!=1||U(frame,at)>1||F(frame,at+88)!=100||F(frame,at+92)!=0)++mismatches;
                    if(F(frame,at+28)!=-1||F(frame,at+32)!=0||F(frame,at+36)!=0||F(frame,at+16)<514||F(frame,at+16)>515||
                       F(frame,at+20)!=20||F(frame,at+24)!=500)++mismatches;
                    double vn=0,fn=0;
                    for(int j=0;j<3;++j){vn+=F(frame,at+40+j*4)*F(frame,at+28+j*4);fn+=F(frame,at+76+j*4)*F(frame,at+28+j*4);}
                    double reaction=Math.Max(0,-fn-(vn<0?.8*vn*100/dt:0));
                    for(int j=0;j<3;++j){double raw=reaction*F(frame,at+28+j*4);
                        contactLaw=Math.Max(contactLaw,Math.Abs(raw-F(frame,at+52+j*4)));
                        contactLaw=Math.Max(contactLaw,Math.Abs(F(frame,at+64+j*4)-F(frame,at+52+j*4)));
                    }
                    if(reaction>0&&firstContact==0)firstContact=tick;
                }
                previous=frame;
            }
            Max("first consumed contact equals trigger",Math.Abs(firstContact-detail.TriggerTick),0);
            Max("two seconds of actual precontact history",firstContact>4000?0:1,0);
            Max("transition occurs strictly after consumed collision",firstTransition>firstContact&&firstTransition>1?0:1,0);
            Max("required postcollision strength/removal outcome",yield?(firstStrength>firstContact&&firstRemoval==0?0:1):(firstRemoval>firstContact&&firstStrength==0?0:1),0);
            Max("cohort/epoch/event/removal identity mismatches",mismatches,0);
            Max("local beam law/channel conformance / N",law,.1);
            Max("contact law and strength conformance / N",contactLaw,.25);
            Max("beam rest/state continuity / m",state,1e-5);
            Max("kick integration / velocity continuity / m/s",velocity,2e-6);
            Max("world-position drift step envelope / m",position,.00015);
            Max("dense versus aggregate force/momentum/kinetic parity",parity,1e-5);
            Max("declared storage/event ports / J",ports,.001);
            // Absolute float32 accumulation envelope at a ~0.8 MN contact kick.
            // Historical contactless fixture limits are unchanged.
            Max("unattributed/reconstructed contact rounding / N",unknown,.25);
            Max("integration impulse residual / kg m/s",impulse,.001);
            Max("kinetic midpoint work residual / J",work,.001);
            Max("pinned seven-second record count",Math.Abs(records.Count-14000),0);
            return new(checks.All(c=>c.Passed)?"Passed":"Failed",scope,checks);
        }catch(Exception e)when(e is IOException or InvalidDataException or OverflowException or KeyNotFoundException){
            checks.Add(new("Reference archive verification: "+e.Message,1,0,false));return new("Failed",scope,checks);
        }
    }
}
