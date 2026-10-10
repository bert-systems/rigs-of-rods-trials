using RoR.Trials;
using System.Text;
void Check(bool valid,string name){if(!valid)throw new Exception(name);}
Check(Contract.Validate(new("reference")).Count==0,"valid reference config");
Check(Contract.Validate(new("phases",PerformanceProbe:true,ObserverProfiling:true)).Count==0,"diagnostic phase profile accepted with common probe");
Check(Contract.Validate(new("phases",ObserverProfiling:true)).Count>0,"phase profiling needs explicit common probe");
Check(Contract.Validate(new("phases",Observation:"off",PerformanceProbe:true,ObserverProfiling:true)).Count>0,"phase profiling cannot invent an off-mode ledger");
Check(Contract.Validate(new("zero",Environment:new(Gravity:0))).Count>0,"unqualified zero gravity rejected");
Check(Contract.Validate(new("asset",Vehicle:"../other.truck")).Count>0,"unsupported asset rejected");
Check(Contract.Validate(new("wind",Environment:new(WindX:31))).Count>0,"wind magnitude rejected");
Check(Contract.Validate(new("repeat",Repeats:21)).Count>0,"repeat bound");
Check(Contract.Validate(new("spring",0,5,0,1,new(Gravity:0),Vehicle:"ror-spring-v1.truck",Scenario:"spring-v1")).Count==0,"qualified dry zero-g fixture accepted");
Check(Contract.Validate(new("spring",0,5,0,1,new(Gravity:0),Scenario:"spring-v1")).Count>0,"fixture asset mismatch rejected");
Check(Contract.Validate(new("damper",0,5,0,1,new(Gravity:0,WindX:1),Vehicle:"ror-damper-v1.truck",Scenario:"damper-v1")).Count>0,"fixture wind rejected");
foreach(string scenario in new[]{"yield-tension-v1","yield-compression-v1","fracture-v1","protected-beam-v1"}){
 var definition=new ExperimentDefinition(scenario,0,.2,0,1,new(Gravity:0),Vehicle:"ror-"+scenario+".truck",Scenario:scenario);
 Check(Contract.Validate(definition).Count==0,"pinned transition fixture accepted: "+scenario);
 Check(Contract.Validate(definition with {DurationSeconds=2}).Count>0,"transition fixture qualification duration bounded");
 Check(Contract.Validate(definition with {Environment=new(Gravity:-9.81)}).Count>0,"transition fixture dry zero gravity required");
}
Check(ArchiveReader.Crc(Encoding.ASCII.GetBytes("123456789"))==0xcbf43926,"standard CRC check");
string dir=args.Length>0?Path.GetFullPath(args[0]):throw new Exception("Provide an outside-Git test output directory.");
Directory.CreateDirectory(dir);
var catalog=new Catalog(dir);
var attempt=new Attempt{Definition=new("persistent"),RevisionId="fixture",Execution="Completed",Capture="Incomplete"};
catalog.Save(attempt);
var recovered=catalog.Load().Single();
Check(recovered.Id==attempt.Id&&recovered.Capture=="Incomplete","catalog quality survives restart");
string file=Path.Combine(dir,"fixture.rort");
byte[] record=new byte[240]; BitConverter.GetBytes((ulong)1).CopyTo(record,0);
BitConverter.GetBytes((uint)1).CopyTo(record,12);
BitConverter.GetBytes(0.0005).CopyTo(record,24);BitConverter.GetBytes(2.0).CopyTo(record,32);
using(var s=File.Create(file))using(var w=new BinaryWriter(s)){
 w.Write(Encoding.ASCII.GetBytes("RORTRIAL"));w.Write((uint)1);w.Write((uint)240);
 w.Write(Encoding.ASCII.GetBytes("DATA"));w.Write((uint)1);w.Write((uint)240);w.Write(ArchiveReader.Crc(record));w.Write(record);w.Write(Encoding.ASCII.GetBytes("DONE"));
 w.Write(Encoding.ASCII.GetBytes("END!"));w.Write((ulong)1);w.Write((ulong)0);w.Write((uint)0);
}
var clean=ArchiveReader.Inspect(file);Check(clean.Complete&&clean.Records==1,"verified chunk/footer");
var bytes=File.ReadAllBytes(file);bytes[40]^=1;File.WriteAllBytes(Path.Combine(dir,"corrupt.rort"),bytes);
Check(!ArchiveReader.Inspect(Path.Combine(dir,"corrupt.rort")).Complete,"CRC corruption prevents complete capture");
bytes=File.ReadAllBytes(file);File.WriteAllBytes(Path.Combine(dir,"truncated.rort"),bytes[..^24]);
var partial=ArchiveReader.Inspect(Path.Combine(dir,"truncated.rort"));
Check(!partial.Complete&&partial.Records==1,"truncated footer retains verified prefix");
var missing=FixtureValidation.Evaluate(file,new("spring",0,5,0,1,new(Gravity:0),Vehicle:"ror-spring-v1.truck",Scenario:"spring-v1"),clean,true);
Check(missing.Status=="NotReady","v1 archive cannot qualify v2 fixture");
var noCapture=FixtureValidation.Evaluate(file,new("spring",0,5,0,1,new(Gravity:0),Vehicle:"ror-spring-v1.truck",Scenario:"spring-v1"),clean with {Complete=false},true);
Check(noCapture.Status=="NotReady","incomplete capture cannot pass fixture");

byte[] v2=new byte[2080];BitConverter.GetBytes((ulong)1).CopyTo(v2,0);
BitConverter.GetBytes((uint)1).CopyTo(v2,12);BitConverter.GetBytes((uint)1).CopyTo(v2,16);
BitConverter.GetBytes((uint)2).CopyTo(v2,20);BitConverter.GetBytes(.0005).CopyTo(v2,24);
BitConverter.GetBytes(100.0).CopyTo(v2,32);BitConverter.GetBytes((uint)4).CopyTo(v2,1348);
BitConverter.GetBytes((ulong)1).CopyTo(v2,1360);
void WriteV2(string name,byte[] r2){
 using var fs=File.Create(Path.Combine(dir,name));using var w=new BinaryWriter(fs);
 w.Write(Encoding.ASCII.GetBytes("RORTRIAL"));w.Write((uint)2);w.Write((uint)2080);
 w.Write(Encoding.ASCII.GetBytes("DATA"));w.Write((uint)1);w.Write((uint)2080);w.Write(ArchiveReader.Crc(r2));w.Write(r2);w.Write(Encoding.ASCII.GetBytes("DONE"));
 w.Write(Encoding.ASCII.GetBytes("END!"));w.Write((ulong)1);w.Write((ulong)0);w.Write((uint)0);
}
WriteV2("schema2.rort",v2);
var validV2=ArchiveReader.Inspect(Path.Combine(dir,"schema2.rort"));
Check(validV2.Complete&&validV2.Records==1,"schema2 complete finite record");
var invented=FixtureValidation.Evaluate(Path.Combine(dir,"schema2.rort"),new("spring",0,5,0,1,new(Gravity:0),Vehicle:"ror-spring-v1.truck",Scenario:"spring-v1"),validV2,true);
Check(invented.Status=="Failed","complete zeros cannot invent a physically passing spring");
BitConverter.GetBytes((uint)6).CopyTo(v2,20);WriteV2("observer-basic.rort",v2);
var basic=ArchiveReader.Inspect(Path.Combine(dir,"observer-basic.rort"));
Check(basic.Complete&&FixtureValidation.Evaluate(Path.Combine(dir,"observer-basic.rort"),new("spring",0,5,0,1,new(Gravity:0),Vehicle:"ror-spring-v1.truck",Scenario:"spring-v1"),basic,true).Status=="NotReady","disabled attribution cannot qualify despite complete capture");
BitConverter.GetBytes((uint)2).CopyTo(v2,20);BitConverter.GetBytes((uint)1).CopyTo(v2,1372);
WriteV2("events-lost.rort",v2);Check(!ArchiveReader.Inspect(Path.Combine(dir,"events-lost.rort")).Complete,"required transition overflow prevents complete capture");
BitConverter.GetBytes((uint)0).CopyTo(v2,1372);BitConverter.GetBytes(double.NaN).CopyTo(v2,240);
WriteV2("nonfinite-channel.rort",v2);Check(!ArchiveReader.Inspect(Path.Combine(dir,"nonfinite-channel.rort")).Complete,"finite base cannot hide a nonfinite channel");
Console.WriteLine("PASS: config bounds/capabilities, CRC, SQLite recovery, corruption and committed-prefix recovery");


Check(Contract.Validate(new("bad observation",Observation:"maybe")).Count>0,"unknown observation mode rejected");
Check(Contract.Validate(new("off",Observation:"off")).Count>0,"ledger-off requires declared common probe");
Check(Contract.Validate(new("off",Observation:"off",PerformanceProbe:true)).Count==0,"explicit ledger-off probe accepted");
Check(FixtureValidation.Evaluate(file,new("spring off",0,5,0,1,new(Gravity:0),Vehicle:"ror-spring-v1.truck",Scenario:"spring-v1",Observation:"off",PerformanceProbe:true),clean,true).Status=="NotReady","off fixture cannot earn science Passed");
byte[] probeRecord=new byte[128];
BitConverter.GetBytes((ulong)1).CopyTo(probeRecord,0);
BitConverter.GetBytes((uint)1).CopyTo(probeRecord,8);BitConverter.GetBytes((uint)4).CopyTo(probeRecord,12);
BitConverter.GetBytes(.0005).CopyTo(probeRecord,24);BitConverter.GetBytes(10.0).CopyTo(probeRecord,32);
string probePath=Path.Combine(dir,"probe.rort");
void WriteProbe(byte[] data,ulong lost=0){
 using var fs=File.Create(probePath);using var w=new BinaryWriter(fs);
 w.Write(Encoding.ASCII.GetBytes("RORPROBE"));w.Write((uint)1);w.Write((uint)128);
 w.Write(Encoding.ASCII.GetBytes("DATA"));w.Write((uint)1);w.Write((uint)128);w.Write(ArchiveReader.Crc(data));w.Write(data);w.Write(Encoding.ASCII.GetBytes("DONE"));
 w.Write(Encoding.ASCII.GetBytes("END!"));w.Write((ulong)1);w.Write(lost);w.Write((uint)0);
}
WriteProbe(probeRecord);
var probeClean=ProbeReader.Inspect(probePath);
Check(probeClean.Complete&&probeClean.MedianUs==10&&probeClean.ReleasedRecords==1,"probe valid CRC/time/cohort");
var damagedProbe=File.ReadAllBytes(probePath);damagedProbe[40]^=1;File.WriteAllBytes(probePath,damagedProbe);
Check(!ProbeReader.Inspect(probePath).Complete,"probe corruption cannot pass completeness");
WriteProbe(probeRecord,1);Check(!ProbeReader.Inspect(probePath).Complete&&ProbeReader.Inspect(probePath).Closed,"probe loss stays incomplete despite a closed footer");
WriteProbe(probeRecord);damagedProbe=File.ReadAllBytes(probePath);File.WriteAllBytes(probePath,damagedProbe[..^24]);
Check(!ProbeReader.Inspect(probePath).Complete&&!ProbeReader.Inspect(probePath).Closed&&ProbeReader.Inspect(probePath).Records==1,"probe interrupted close retains verified prefix");
BitConverter.GetBytes(double.NaN).CopyTo(probeRecord,32);WriteProbe(probeRecord);
Check(!ProbeReader.Inspect(probePath).Complete,"nonfinite probe time stays incomplete");
Console.WriteLine("PASS: observer profiles, probe CRC/finite/loss/prefix checks and no off-mode scientific pass");

Check(Contract.Validate(new("barrier",DurationSeconds:8,Scenario:"barrier-v1")).Count==0,"pinned barrier definition");
Check(Contract.Validate(new("barrier",Scenario:"barrier-v1",Observation:"off",PerformanceProbe:true)).Count>0,"required detail cannot disable ledger");
Check(Contract.Validate(new("barrier",Scenario:"barrier-v1",BarrierDistanceM:double.NaN)).Count>0,"finite barrier geometry");
Check(Contract.Validate(new("barrier",DetailFault:"queue-overflow")).Count>0,"fault profiles scoped to barrier qualification");
string detailPath=Path.Combine(dir,"synthetic-detail.rort");
void WriteDetail(bool gap=false,bool loss=false){
 using var s=File.Create(detailPath);using var w=new BinaryWriter(s);
 w.Write(Encoding.ASCII.GetBytes("RORDTAIL"));foreach(uint value in new uint[]{1,1,1,36,4000,8000})w.Write(value);
 long count=0;
 for(long tick=1001;tick<=13001;++tick){
  if(gap&&tick==7000)continue;
  bool contact=tick==5001;byte[] frame=new byte[128+256+112+(contact?104:0)];
  BitConverter.GetBytes((ulong)tick).CopyTo(frame,0);BitConverter.GetBytes(.0005).CopyTo(frame,8);
  BitConverter.GetBytes(1).CopyTo(frame,20);BitConverter.GetBytes(1).CopyTo(frame,24);BitConverter.GetBytes(contact?1:0).CopyTo(frame,28);
  BitConverter.GetBytes(100f).CopyTo(frame,136);
  if(contact){int at=496;BitConverter.GetBytes(2).CopyTo(frame,at+4);BitConverter.GetBytes(1).CopyTo(frame,at+12);BitConverter.GetBytes(100f).CopyTo(frame,at+64);}
  w.Write(Encoding.ASCII.GetBytes("DATA"));w.Write((uint)1);w.Write((uint)frame.Length);w.Write(ArchiveReader.Crc(frame));w.Write(frame);w.Write(Encoding.ASCII.GetBytes("DONE"));++count;
 }
 w.Write(Encoding.ASCII.GetBytes("END!"));w.Write((ulong)count);w.Write(loss?1ul:0ul);w.Write(0ul);w.Write(0u);
}
WriteDetail();var detailGood=DetailReader.Inspect(detailPath,5001,13001);
Check(detailGood.Complete&&detailGood.Records==12001&&detailGood.BarrierApplications==1&&detailGood.BarrierImpulseNs[0]==.05,"complete synthetic 2 kHz pre/post window and applied impulse");
WriteDetail(gap:true);var detailGap=DetailReader.Inspect(detailPath,5001,13001);
Check(!detailGap.Complete&&detailGap.Records==12000&&detailGap.LastTick==13001,"required gap remains incomplete while later detail is recovered");
WriteDetail(loss:true);Check(!DetailReader.Inspect(detailPath,5001,13001).Complete,"sticky detail loss footer");
WriteDetail();using(var f=new FileStream(detailPath,FileMode.Open,FileAccess.Write)){f.SetLength(f.Length-32);}
var detailPrefix=DetailReader.Inspect(detailPath,5001,13001);
Check(!detailPrefix.Complete&&!detailPrefix.Closed&&detailPrefix.Records==12001,"abrupt detail close retains committed prefix");
WriteDetail();using(var f=new FileStream(detailPath,FileMode.Open,FileAccess.ReadWrite)){f.Position=52;int value=f.ReadByte();f.Position=52;f.WriteByte((byte)(value^1));}
Check(!DetailReader.Inspect(detailPath,5001,13001).Complete,"detail CRC corruption rejects frame");
Console.WriteLine("PASS: barrier geometry/profiles, required detail CRC/gap/loss/prefix and actual impulse decoding");
var projected=new Attempt();var envelopes=new ImpactProjection();
for(int tick=10;tick<=100;tick+=10){
 var sample=System.Text.Json.JsonSerializer.SerializeToElement(new{tick,timeSeconds=tick*.0005,peakNetBarrierForceN=tick==40?999:1,detailDropped=0,detailIoError=false});
 envelopes.Add(projected,sample);
}
Check(projected.ImpactHistory.Count==1&&projected.ImpactHistory[0].GetProperty("peakNetBarrierForceN").GetDouble()==999,"20 Hz display preserves transient 200 Hz envelope peak");
envelopes.Add(projected,System.Text.Json.JsonSerializer.SerializeToElement(new{tick=120,timeSeconds=.06,peakNetBarrierForceN=1,detailDropped=1,detailIoError=false}));envelopes.Flush(projected);
Check(projected.ImpactHistory[^1].GetProperty("gap").GetBoolean(),"gap/loss breaks scientific chart path");
Console.WriteLine("PASS: peak-preserving projection and visible gap semantics");

byte[] strengthRecord=new byte[2080];
BitConverter.GetBytes(1ul).CopyTo(strengthRecord,0);BitConverter.GetBytes(1u).CopyTo(strengthRecord,12);
BitConverter.GetBytes(.0005).CopyTo(strengthRecord,24);BitConverter.GetBytes(100.0).CopyTo(strengthRecord,32);
BitConverter.GetBytes(4u).CopyTo(strengthRecord,1348);BitConverter.GetBytes(1ul).CopyTo(strengthRecord,1360);
BitConverter.GetBytes(1u).CopyTo(strengthRecord,1368);BitConverter.GetBytes(4u).CopyTo(strengthRecord,1380);
BitConverter.GetBytes(200.0).CopyTo(strengthRecord,1424);BitConverter.GetBytes(400.0).CopyTo(strengthRecord,1432);
WriteV2("strength.rort",strengthRecord);string strengthPath=Path.Combine(dir,"strength.rort");
var strengthCheck=ArchiveReader.Inspect(strengthPath);var strengthPage=TransitionReader.Read(strengthPath,strengthCheck,0,1);
Check(strengthPage.ProjectionComplete&&strengthPage.StrengthChanges==1&&strengthPage.ParameterChanges==0&&strengthPage.Removed==0&&strengthPage.RestStoragePortJ==0&&strengthPage.RemovedStoragePortJ==0,"strength-only transition does not invent energy or removal");
Check(TransitionReader.Read(strengthPath,strengthCheck,1,1).Events.Count==0,"transition pagination ends without repeated events");
bool invalidPage=false;try{TransitionReader.Read(strengthPath,strengthCheck,0,101);}catch(ArgumentException){invalidPage=true;}
Check(invalidPage,"transition API bounded page size");
bool invalidCapture=false;try{TransitionReader.Read(strengthPath,strengthCheck with {Complete=false});}catch(InvalidDataException){invalidCapture=true;}
Check(invalidCapture,"incomplete aggregate cannot serve verified transition view");
Console.WriteLine("PASS: transition fixtures, strength-only zero storage ports, bounded pages and quality gate");

var laterImpact=new ExperimentDefinition("later collision",5,7,0,Environment:new(Gravity:0),Vehicle:"ror-impact-yield-v1.truck",Scenario:"impact-yield-v1",BarrierDistanceM:13);
Check(Contract.Validate(laterImpact).Count==0,"pinned later collision fixture");
foreach(var invalid in new[]{laterImpact with {DurationSeconds=5},laterImpact with {LaunchSpeedMps=0},laterImpact with {BarrierDistanceM=12},
    laterImpact with {Environment=new(Gravity:-9.81)},laterImpact with {Observation="off",PerformanceProbe=true},laterImpact with {Accounting=false}})
    Check(Contract.Validate(invalid).Count>0,"later impact cannot silently change frozen state/capture");
Check(ImpactFixtureValidation.Evaluate(strengthPath,laterImpact,strengthCheck,null,true).Status=="NotReady","aggregate alone cannot certify later collision science");
Check(Contract.HasDetail("impact-fracture-v1")&&!Contract.TransitionFixture("impact-fracture-v1"),"later impact is distinct from tick-1 fixture");
Console.WriteLine("PASS: pinned later-collision contracts and mandatory dense qualification gate");


if(args.Length>1){
 var inspected=new List<object>();
 var impactCorruptionChecked=new HashSet<string>();
 foreach(var nativeDir in Directory.GetFiles(Path.GetFullPath(args[1]),"manifest.json",SearchOption.AllDirectories).Select(Path.GetDirectoryName).Distinct().Where(d=>File.Exists(Path.Combine(d!,"steps.rort"))||File.Exists(Path.Combine(d!,"probe.rort")))){
  string path=Path.Combine(nativeDir!,"probe.rort");
  var check=File.Exists(path)?ProbeReader.Inspect(path):null;
  Check(check==null||check.Complete&&check.Closed,"retained native probe reinspection: "+path);
  string aggregate=Path.Combine(Path.GetDirectoryName(path)!,"steps.rort");
  if(File.Exists(aggregate))Check(ArchiveReader.Inspect(aggregate).Complete,"retained native aggregate reinspection: "+aggregate);
  string manifest=Path.Combine(Path.GetDirectoryName(path)!,"manifest.json");
  using var m=System.Text.Json.JsonDocument.Parse(File.ReadAllText(manifest));
  var definition=System.Text.Json.JsonSerializer.Deserialize<ExperimentDefinition>(m.RootElement.GetProperty("definition").GetRawText(),Contract.Json)!;
  Check(check!=null||!definition.PerformanceProbe,"required native probe is present");
  if(Contract.TransitionFixture(definition.Scenario)){
   var original=ArchiveReader.Inspect(aggregate);
   Check(FixtureValidation.Evaluate(aggregate,definition,original,true).Status=="Passed","final independent native transition reference: "+aggregate);
   var originalBytes=File.ReadAllBytes(aggregate);int length=BitConverter.ToInt32(originalBytes,24);
   foreach(var mutation in new[]{"kind","port","storage","epoch"}){
    var forged=(byte[])originalBytes.Clone();
    if(mutation=="kind")BitConverter.GetBytes(0u).CopyTo(forged,32+1380);
    if(mutation=="port")BitConverter.GetBytes(10.0).CopyTo(forged,32+1232);
    if(mutation=="storage")BitConverter.GetBytes(200.0).CopyTo(forged,32+1440);
    if(mutation=="epoch")BitConverter.GetBytes(1ul).CopyTo(forged,32+1352);
    BitConverter.GetBytes(ArchiveReader.Crc(forged.AsSpan(32,length).ToArray())).CopyTo(forged,28);
    string forgedPath=Path.Combine(dir,definition.Scenario+"-"+mutation+".rort");File.WriteAllBytes(forgedPath,forged);
    var forgedCheck=ArchiveReader.Inspect(forgedPath);Check(forgedCheck.Complete,"forged reference retains valid capture CRC");
    Check(FixtureValidation.Evaluate(forgedPath,definition,forgedCheck,true).Status=="Failed","CRC-valid wrong "+mutation+" cannot earn scientific Passed");
   }
  }
  if(Contract.ImpactFixture(definition.Scenario)){
   string detailFile=Path.Combine(Path.GetDirectoryName(path)!,"detail.rort");
   using var h=System.Text.Json.JsonDocument.Parse(File.ReadAllText(Path.Combine(Path.GetDirectoryName(path)!,"detail-health.json")));
   long trigger=h.RootElement.GetProperty("triggerTick").GetInt64(),end=h.RootElement.GetProperty("requiredEndTick").GetInt64();
   var dense=DetailReader.Inspect(detailFile,trigger,end);var ledger=ArchiveReader.Inspect(aggregate);
   string expected=definition.DetailFault=="none"?"Passed":"NotReady";
   Check(ImpactFixtureValidation.Evaluate(aggregate,definition,ledger,dense,true).Status==expected,"final later impact reference: "+path);
   if(dense.Complete&&impactCorruptionChecked.Add(definition.Scenario))foreach(string mutation in new[]{"kind","port","epoch","contact","velocity","strength"}){
    string caseDir=Path.Combine(dir,definition.Scenario+"-"+mutation);Directory.CreateDirectory(caseDir);
    string mutatedAggregate=Path.Combine(caseDir,"steps.rort"),mutatedDetail=Path.Combine(caseDir,"detail.rort");
    File.Copy(aggregate,mutatedAggregate);File.Copy(detailFile,mutatedDetail);
    bool denseMutation=mutation is "contact" or "velocity" or "strength";
    string target=denseMutation?mutatedDetail:mutatedAggregate;var forged=File.ReadAllBytes(target);int position=denseMutation?32:16;bool changed=false;
    while(position<forged.Length&&Encoding.ASCII.GetString(forged,position,4)=="DATA"){
     int count=BitConverter.ToInt32(forged,position+4),size=BitConverter.ToInt32(forged,position+8),start=position+16;
     for(int i=0;i<count&&!changed;++i){int at=start+(denseMutation?0:i*2080);long tick=BitConverter.ToInt64(forged,at);
      if(mutation=="epoch"){BitConverter.GetBytes(1ul).CopyTo(forged,at+1352);changed=true;}
      if(mutation is "kind" or "port"&&BitConverter.ToUInt32(forged,at+1368)>0){
       if(mutation=="kind")BitConverter.GetBytes(0u).CopyTo(forged,at+1380);else BitConverter.GetBytes(50.0).CopyTo(forged,at+1232);changed=true;
      }
      if(denseMutation&&tick==trigger){
       if(mutation=="contact")BitConverter.GetBytes(1f).CopyTo(forged,at+128+4*256+3*112+28);
       if(mutation=="velocity")BitConverter.GetBytes(12f).CopyTo(forged,at+128+40);
       if(mutation=="strength")BitConverter.GetBytes(123f).CopyTo(forged,at+128+4*256+36);
       changed=true;
      }
     }
     if(changed){BitConverter.GetBytes(ArchiveReader.Crc(forged.AsSpan(start,size).ToArray())).CopyTo(forged,position+12);break;}
     position+=size+20;
    }
    Check(changed,"semantic mutation selected a real record");File.WriteAllBytes(target,forged);
    var fakeLedger=ArchiveReader.Inspect(mutatedAggregate);var fakeDense=DetailReader.Inspect(mutatedDetail,trigger,end);
    Check(fakeLedger.Complete&&fakeDense.Complete,"semantic adversary retains both valid byte captures: "+mutation);
    Check(ImpactFixtureValidation.Evaluate(mutatedAggregate,definition,fakeLedger,fakeDense,true).Status=="Failed","CRC-valid later impact "+mutation+" cannot pass science");
   }
  }
  inspected.Add(new{path,check});
 }
 File.WriteAllText(Path.Combine(dir,"native-reinspection.json"),System.Text.Json.JsonSerializer.Serialize(inspected,Contract.Json));
 Console.WriteLine($"PASS: {inspected.Count} retained native attempts reinspected by final coordinator reader");
}
