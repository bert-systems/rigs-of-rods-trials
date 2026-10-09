using System.Text;
namespace RoR.Trials;

// Only verified DONE+CRC blocks are analyzed. A truncated or corrupt tail stays incomplete.
public static class ArchiveReader
{
    public sealed record Check(long Records, bool Closed, bool Complete, long Dropped,
        double MaxMomentumResidual, double MaxWorkResidual, double MaxKinetic, string? Problem);
    public static Check Inspect(string path)
    {
        long records=0, dropped=0; bool closed=false; double maxP=0,maxW=0,maxK=0;
        string? problem=null;
        try
        {
            using var file=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.ReadWrite);
            using var r=new BinaryReader(file);
            if(Encoding.ASCII.GetString(r.ReadBytes(8))!="RORTRIAL" || r.ReadUInt32()!=1 || r.ReadUInt32()!=240)
                throw new InvalidDataException("Unknown archive header.");
            long previousTick=0;
            while(file.Position<file.Length)
            {
                string marker=Encoding.ASCII.GetString(r.ReadBytes(4));
                if(marker=="END!")
                {
                    long written=(long)r.ReadUInt64(); dropped=(long)r.ReadUInt64(); var ioError=r.ReadUInt32();
                    closed=true;
                    if(written!=records || dropped>0 || ioError>0) problem="Recorder count, gap or I/O failure.";
                    if(file.Position!=file.Length) problem="Unexpected data after footer.";
                    break;
                }
                if(marker!="DATA") throw new InvalidDataException("Unknown block marker.");
                uint count=r.ReadUInt32(), size=r.ReadUInt32(), crc=r.ReadUInt32();
                if(count==0 || count>128 || size!=count*240) throw new InvalidDataException("Invalid block size.");
                byte[] bytes=r.ReadBytes((int)size);
                if(bytes.Length!=size || Encoding.ASCII.GetString(r.ReadBytes(4))!="DONE" || Crc(bytes)!=crc)
                    throw new InvalidDataException("Truncated or corrupt block.");
                using var memory=new MemoryStream(bytes); using var b=new BinaryReader(memory);
                for(int i=0;i<count;i++)
                {
                    long tick=(long)b.ReadUInt64(); _=b.ReadUInt32(); uint nodes=b.ReadUInt32(); _=b.ReadUInt32(); uint flags=b.ReadUInt32();
                    if(tick!=previousTick+1) problem="Required tick sequence gap.";
                    if((flags&1)!=0) problem="Invalid/nonfinite native observation.";
                    previousTick=tick;
                    double dt=b.ReadDouble(),mass=b.ReadDouble();
                    if(nodes==0 || !double.IsFinite(dt) || dt<=0 || !double.IsFinite(mass) || mass<=0) problem="Invalid node cohort or integration step.";
                    for(int n=0;n<12;n++) if(!double.IsFinite(b.ReadDouble())) problem="Nonfinite vector record."; // COM, p, F, contact
                    double before=b.ReadDouble(),k=b.ReadDouble(),work=b.ReadDouble();
                    if(!double.IsFinite(before)||!double.IsFinite(work)) problem="Nonfinite kinetic-work record.";
                    double x=b.ReadDouble(),y=b.ReadDouble(),z=b.ReadDouble(),w=b.ReadDouble();
                    if(!double.IsFinite(k)||!double.IsFinite(x)||!double.IsFinite(y)||!double.IsFinite(z)||!double.IsFinite(w))
                        problem="Nonfinite record.";
                    maxP=Math.Max(maxP,Math.Sqrt(x*x+y*y+z*z)); maxW=Math.Max(maxW,Math.Abs(w)); maxK=Math.Max(maxK,k);
                    for(int n=0;n<6;n++) if(!double.IsFinite(b.ReadDouble())) problem="Nonfinite environment/peak record."; // peak, gravity, density, wind
                    ++records;
                }
            }
        }
        catch(Exception e) when(e is IOException or UnauthorizedAccessException or InvalidDataException)
        { problem=e.Message; }
        if(records==0 && problem==null) problem="No required observations.";
        if(!closed && problem==null) problem="No clean recorder footer; retain verified prefix.";
        return new(records,closed,closed&&problem==null,dropped,maxP,maxW,maxK,problem);
    }
    public static uint Crc(byte[] bytes)
    {
        uint crc=0xffffffff;
        foreach(byte value in bytes) { crc^=value; for(int i=0;i<8;i++) crc=(crc>>1)^(0xedb88320u&(0u-(crc&1))); }
        return ~crc;
    }
}
