using RoR.Trials;
using System.Text;
void Check(bool valid,string name){if(!valid)throw new Exception(name);}
Check(Contract.Validate(new("reference")).Count==0,"valid reference config");
Check(Contract.Validate(new("zero",Environment:new(Gravity:0))).Count>0,"unqualified zero gravity rejected");
Check(Contract.Validate(new("asset",Vehicle:"../other.truck")).Count>0,"unsupported asset rejected");
Check(Contract.Validate(new("wind",Environment:new(WindX:31))).Count>0,"wind magnitude rejected");
Check(Contract.Validate(new("repeat",Repeats:21)).Count>0,"repeat bound");
Check(Contract.Validate(new("spring",0,5,0,1,new(Gravity:0),Vehicle:"ror-spring-v1.truck",Scenario:"spring-v1")).Count==0,"qualified dry zero-g fixture accepted");
Check(Contract.Validate(new("spring",0,5,0,1,new(Gravity:0),Scenario:"spring-v1")).Count>0,"fixture asset mismatch rejected");
Check(Contract.Validate(new("damper",0,5,0,1,new(Gravity:0,WindX:1),Vehicle:"ror-damper-v1.truck",Scenario:"damper-v1")).Count>0,"fixture wind rejected");
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
