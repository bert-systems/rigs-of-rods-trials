using System.Text;
namespace RoR.Trials;

// Control probe is deliberately separate from force/energy captures. It cannot
// earn scientific Passed and never supplies fabricated accounting channels.
public static class ProbeReader
{
    public sealed record Check(long Records,bool Closed,bool Complete,long Dropped,string? Problem,double MedianUs,double P95Us,double MeanUs,long ReleasedRecords,long Fingerprints);
    public static Check Inspect(string path)
    {
        long records=0,dropped=0,released=0,hashes=0;string? problem=null;bool closed=false;
        var times=new List<double>();
        try {
            using var file=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.ReadWrite);
            using var b=new BinaryReader(file);
            if(Encoding.ASCII.GetString(b.ReadBytes(8))!="RORPROBE"||b.ReadUInt32()!=1||b.ReadUInt32()!=128)
                throw new InvalidDataException("Unknown control-probe schema.");
            ulong previous=0;
            while(file.Position<file.Length) {
                string marker=Encoding.ASCII.GetString(b.ReadBytes(4));
                if(marker=="END!"){
                    ulong durable=b.ReadUInt64();dropped=(long)b.ReadUInt64();uint io=b.ReadUInt32();closed=true;
                    if(durable!=(ulong)records||dropped>0||io>0||file.Position!=file.Length)problem="Probe footer/count/loss/I/O failure.";
                    break;
                }
                if(marker!="DATA")throw new InvalidDataException("Unknown probe block.");
                uint count=b.ReadUInt32(),size=b.ReadUInt32(),crc=b.ReadUInt32();
                if(count==0||count>128||size!=count*128)throw new InvalidDataException("Invalid probe block size.");
                byte[] data=b.ReadBytes((int)size);
                if(data.Length!=size||Encoding.ASCII.GetString(b.ReadBytes(4))!="DONE"||ArchiveReader.Crc(data)!=crc)
                    throw new InvalidDataException("Truncated or corrupt probe block.");
                for(int i=0;i<count;i++){
                    int at=i*128;double At(int o)=>BitConverter.ToDouble(data,at+o);
                    ulong tick=BitConverter.ToUInt64(data,at);
                    uint phase=BitConverter.ToUInt32(data,at+8),nodes=BitConverter.ToUInt32(data,at+12);
                    uint beams=BitConverter.ToUInt32(data,at+16),flags=BitConverter.ToUInt32(data,at+20);
                    uint hash=BitConverter.ToUInt32(data,at+96),initialized=BitConverter.ToUInt32(data,at+100);
                    if(tick!=previous+1)problem="Probe tick gap.";
                    if(phase>1||nodes==0||nodes>65536||beams>65536||flags!=0||initialized>1||hash!=(tick%200==0?1u:0u))
                        problem="Invalid probe cohort/flags/sampling cadence.";
                    if(!double.IsFinite(At(24))||At(24)<=0||!double.IsFinite(At(32))||At(32)<0)
                        problem="Invalid probe step/time.";
                    foreach(int o in new[]{40,48,56,64,72,80,104,112,120})if(!double.IsFinite(At(o)))problem="Nonfinite probe state.";
                    previous=tick;++records;if(records>300000)throw new InvalidDataException("Probe exceeds trial tick budget.");
                    if(hash==1)++hashes;
                    if(phase==1){times.Add(At(32));++released;}
                }
            }
        }catch(Exception e) when(e is IOException or InvalidDataException or UnauthorizedAccessException){problem=e.Message;}
        times.Sort();
        double Quantile(double q)=>times.Count==0?0:times[(int)Math.Floor((times.Count-1)*q)];
        return new(records,closed,closed&&problem==null&&records>0,dropped,problem??(closed?null:"No probe close footer."),
            Quantile(.5),Quantile(.95),times.Count==0?0:times.Average(),released,hashes);
    }
}
