using RoR.Trials;
using System.Text;
void Check(bool valid,string name){if(!valid)throw new Exception(name);}
Check(Contract.Validate(new("reference")).Count==0,"valid reference config");
Check(Contract.Validate(new("zero",Environment:new(Gravity:0))).Count>0,"unqualified zero gravity rejected");
Check(Contract.Validate(new("asset",Vehicle:"../other.truck")).Count>0,"unsupported asset rejected");
Check(Contract.Validate(new("wind",Environment:new(WindX:31))).Count>0,"wind magnitude rejected");
Check(Contract.Validate(new("repeat",Repeats:21)).Count>0,"repeat bound");
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
Console.WriteLine("PASS: config bounds/capabilities, CRC, SQLite recovery, corruption and committed-prefix recovery");
