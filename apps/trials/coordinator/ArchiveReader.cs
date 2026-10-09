using System.Text;
namespace RoR.Trials;

// Only verified DONE+CRC blocks are analyzed. A truncated or corrupt tail stays incomplete.
public static class ArchiveReader
{
    public sealed record Check(long Records, bool Closed, bool Complete, long Dropped,
        double MaxMomentumResidual, double MaxWorkResidual, double MaxKinetic, string? Problem)
    { public Dictionary<string,double> Accounting {get;init;}=new(); }
    public static Check Inspect(string path)
    {
        long records=0, dropped=0; bool closed=false; double maxP=0,maxW=0,maxK=0;
        string? problem=null;
        var accounting=new Dictionary<string,double>{
            ["maxUnattributedNodeForceL1N"]=0,["maxAttributionResidualL1N"]=0,["mechanicalResidualSumJ"]=0,
            ["nonconservativeWorkSumJ"]=0,["windWorkSumJ"]=0,["relativeDragWorkSumJ"]=0,
            ["injectionKineticSumJ"]=0,["mutationKineticSumJ"]=0,["maxUnclosedBeams"]=0,["linearBeamParameterEvents"]=0,["breakEvents"]=0};
        double cpuSum=0;
        try
        {
            using var file=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.ReadWrite);
            using var r=new BinaryReader(file);
            if(Encoding.ASCII.GetString(r.ReadBytes(8))!="RORTRIAL")throw new InvalidDataException("Unknown archive magic.");
            uint schema=r.ReadUInt32(), recordSize=r.ReadUInt32();
            if(!(schema==1&&recordSize==240 || schema==2&&recordSize==2080))throw new InvalidDataException("Unknown archive schema/record length.");
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
                if(count==0 || count>128 || size!=count*recordSize) throw new InvalidDataException("Invalid block size.");
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
                    if(schema==2){
                        // Channels: consumed vector, work, generated vector, with explicit per-tick epochs.
                        for(int c=0;c<16;c++){
                            for(int j=0;j<3;j++)if(!double.IsFinite(b.ReadDouble()))problem="Nonfinite channel force.";
                            var cw=b.ReadDouble();if(!double.IsFinite(cw))problem="Nonfinite channel work.";
                            string key="work."+ChannelNames[c]+".J";
                            accounting[key]=accounting.GetValueOrDefault(key)+cw;
                            for(int j=0;j<3;j++)if(!double.IsFinite(b.ReadDouble()))problem="Nonfinite generated force.";
                        }
                        var v=new double[16];for(int j=0;j<16;j++){v[j]=b.ReadDouble();if(!double.IsFinite(v[j]))problem="Nonfinite accounting term.";}
                        accounting["mechanicalResidualSumJ"]+=v[4];accounting["nonconservativeWorkSumJ"]+=v[5];
                        accounting["injectionKineticSumJ"]+=v[6];accounting["mutationKineticSumJ"]+=v[7];
                        accounting["windWorkSumJ"]+=v[8];accounting["relativeDragWorkSumJ"]+=v[9];
                        accounting["maxUnattributedNodeForceL1N"]=Math.Max(accounting["maxUnattributedNodeForceL1N"],v[10]);
                        accounting["maxAttributionResidualL1N"]=Math.Max(accounting["maxAttributionResidualL1N"],v[11]);
                        cpuSum+=v[15];
                        for(int j=0;j<9;j++)if(!double.IsFinite(b.ReadDouble()))problem="Nonfinite state/fixed-node port.";
                        accounting["linearBeamParameterEvents"]+=b.ReadUInt32();accounting["breakEvents"]+=b.ReadUInt32();
                        accounting["maxUnclosedBeams"]=Math.Max(accounting["maxUnclosedBeams"],b.ReadUInt32());
                        if(b.ReadUInt32()<nodes)problem="Unprepared observer cohort.";
                        var consumed=b.ReadUInt64();var generated=b.ReadUInt64();
                        if(generated!=(ulong)tick || consumed>generated)problem="Invalid force epochs.";
                        uint events=b.ReadUInt32(),overflow=b.ReadUInt32();
                        if(events>8||overflow!=0)problem="Required beam-event overflow.";
                        for(int j=0;j<8;j++){
                            _=b.ReadUInt32();_=b.ReadUInt32();
                            for(int k2=0;k2<10;k2++)if(!double.IsFinite(b.ReadDouble()))problem="Nonfinite beam transition.";
                        }
                    }
                    ++records;
                }
            }
        }
        catch(Exception e) when(e is IOException or UnauthorizedAccessException or InvalidDataException)
        { problem=e.Message; }
        if(records==0 && problem==null) problem="No required observations.";
        if(!closed && problem==null) problem="No clean recorder footer; retain verified prefix.";
        accounting["meanPhysicsStepElapsedUs"]=records>0?cpuSum/records:0;
        return new(records,closed,closed&&problem==null,dropped,maxP,maxW,maxK,problem){Accounting=accounting};
    }
    public static readonly string[] ChannelNames=["gravity","genericDrag","groundObject","beamElastic","beamDamping","beamCorrection","wheels","aero","buoyancy","commands","mouse","cabContact","slide","interActor","freeForce","unattributed"];
    // Used only after Inspect confirms the entire archive and finite accounting records.
    public static IEnumerable<byte[]> VerifiedRecords(string path){
        using var s=File.OpenRead(path);using var b=new BinaryReader(s);
        b.ReadBytes(8);uint schema=b.ReadUInt32(),size=b.ReadUInt32();
        if(schema!=2||size!=2080)yield break;
        while(Encoding.ASCII.GetString(b.ReadBytes(4))=="DATA"){
            uint n=b.ReadUInt32(),length=b.ReadUInt32(),crc=b.ReadUInt32();var data=b.ReadBytes((int)length);
            if(n>128||length!=n*size||data.Length!=length||Crc(data)!=crc||Encoding.ASCII.GetString(b.ReadBytes(4))!="DONE")yield break;
            for(int i=0;i<n;i++)yield return data.AsSpan(i*(int)size,(int)size).ToArray();
        }
    }
    public static uint Crc(byte[] bytes)
    {
        uint crc=0xffffffff;
        foreach(byte value in bytes) { crc^=value; for(int i=0;i<8;i++) crc=(crc>>1)^(0xedb88320u&(0u-(crc&1))); }
        return ~crc;
    }
}
