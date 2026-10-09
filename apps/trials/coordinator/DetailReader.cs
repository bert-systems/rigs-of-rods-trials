using System.Text;
namespace RoR.Trials;

// Streaming reader: only CRC+DONE frames contribute, including after injected gaps.
public static class DetailReader
{
    public sealed record Check(long Records,bool Closed,bool Complete,string? Problem,long FirstTick,long LastTick,
        long TriggerTick,long Dropped,long MissingRequiredTicks,int Nodes,int Beams,long ContactApplications,
        long BarrierApplications,long ParameterTransitions,long StrengthTransitions,long RemovedBeams,
        double PeakApplicationForceN,double PeakNetBarrierForceN,double[] BarrierImpulseNs,double BarrierWorkJ,
        double MaxBeamStrain,Dictionary<int,double> NodePeakForceN)
    {public double[] NormalImpulseNs {get;init;}=new double[3];public double[] TangentialImpulseNs {get;init;}=new double[3];
     public double PeakNormalApplicationForceN {get;init;}public double PeakTangentialApplicationForceN {get;init;}}
    public static Check Inspect(string path,long triggerTick,long requiredEndTick,string? transitionsPath=null,string? indexPath=null)
    {
        long records=0,first=0,last=0,dropped=0,missing=0,contacts=0,barrier=0,parameters=0,strength=0,removed=0;
        int nodes=0,beams=0;bool closed=false;string? problem=null;
        double peak=0,peakNet=0,work=0,strain=0;double[] impulse=new double[3];Dictionary<int,double> nodePeaks=[];
        using var transitions=transitionsPath==null?null:new StreamWriter(transitionsPath,false,Encoding.UTF8);
        using var index=indexPath==null?null:new StreamWriter(indexPath,false,Encoding.UTF8);
        double[] normalImpulse=new double[3],tangentialImpulse=new double[3];double peakNormal=0,peakTangential=0;
        try{
            using var f=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.ReadWrite);
            using var r=new BinaryReader(f);
            if(Encoding.ASCII.GetString(r.ReadBytes(8))!="RORDTAIL"||r.ReadUInt32()!=1)throw new InvalidDataException("Unknown detail schema.");
            nodes=checked((int)r.ReadUInt32());beams=checked((int)r.ReadUInt32());uint cap=r.ReadUInt32(),pre=r.ReadUInt32(),post=r.ReadUInt32();
            if(nodes<=0||nodes>65536||beams<0||beams>65536||cap!=nodes*4+32||pre!=4000||post!=8000)throw new InvalidDataException("Invalid required detail profile.");
            while(f.Position<f.Length){
                long offset=f.Position;string marker=Encoding.ASCII.GetString(r.ReadBytes(4));
                if(marker=="END!"){
                    long written=checked((long)r.ReadUInt64());dropped=checked((long)r.ReadUInt64());missing=checked((long)r.ReadUInt64());uint io=r.ReadUInt32();closed=true;
                    if(written!=records||dropped>0||missing>0||io!=0)problem="Required detail loss or writer failure.";
                    if(f.Position!=f.Length)problem="Unexpected detail tail.";break;
                }
                if(marker!="DATA")throw new InvalidDataException("Invalid detail marker.");
                uint count=r.ReadUInt32(),size=r.ReadUInt32(),crc=r.ReadUInt32();
                long max=128L+nodes*256L+beams*112L+cap*104L;
                if(count!=1||size<128L+nodes*256L+beams*112L||size>max||size>16*1024*1024)throw new InvalidDataException("Invalid detail frame size.");
                var data=r.ReadBytes((int)size);
                if(data.Length!=size||ArchiveReader.Crc(data)!=crc||Encoding.ASCII.GetString(r.ReadBytes(4))!="DONE")throw new InvalidDataException("Truncated/corrupt detail frame; retain committed prefix.");
                var frame=data.AsSpan();
                long tick=checked((long)BitConverter.ToUInt64(frame));double dt=BitConverter.ToDouble(frame[8..]);
                int nn=BitConverter.ToInt32(frame[20..]),bb=BitConverter.ToInt32(frame[24..]),cc=BitConverter.ToInt32(frame[28..]);
                uint flags=BitConverter.ToUInt32(frame[36..]),lost=BitConverter.ToUInt32(frame[40..]);
                if(tick<=0||!double.IsFinite(dt)||dt<=0||nn!=nodes||bb!=beams||cc<0||cc>cap||size!=128L+nodes*256L+beams*112L+cc*104L)throw new InvalidDataException("Invalid detail cohort/clock/payload.");
                if(last!=0&&tick!=last+1)problem="Required detail tick gap.";
                if((flags&1)!=0||lost>0)problem="Contact application overflow.";
                for(int at=48;at<128;at+=8)if(!double.IsFinite(BitConverter.ToDouble(frame[at..])))throw new InvalidDataException("Nonfinite detail reduction.");
                for(int i=0;i<nodes;++i){int at=128+i*256;
                    if(BitConverter.ToInt32(frame[at..])!=i)throw new InvalidDataException("Invalid node identity.");
                    for(int k=8;k<256;k+=4)if(!float.IsFinite(BitConverter.ToSingle(frame[(at+k)..])))throw new InvalidDataException("Nonfinite node detail.");
                }
                for(int i=0;i<beams;++i){int at=128+nodes*256+i*112;
                    if(BitConverter.ToInt32(frame[at..])!=i||BitConverter.ToUInt32(frame[(at+4)..])>=nodes||BitConverter.ToUInt32(frame[(at+8)..])>=nodes)throw new InvalidDataException("Invalid beam identity/endpoints.");
                    for(int k=16;k<52;k+=4)if(!float.IsFinite(BitConverter.ToSingle(frame[(at+k)..])))throw new InvalidDataException("Nonfinite beam detail.");
                    for(int k=64;k<112;k+=4)if(!float.IsFinite(BitConverter.ToSingle(frame[(at+k)..])))throw new InvalidDataException("Nonfinite beam force application.");
                    float length=BitConverter.ToSingle(frame[(at+16)..]),rest=BitConverter.ToSingle(frame[(at+20)..]),kval=BitConverter.ToSingle(frame[(at+24)..]),strengthNow=BitConverter.ToSingle(frame[(at+36)..]);
                    float oldRest=BitConverter.ToSingle(frame[(at+40)..]),oldK=BitConverter.ToSingle(frame[(at+44)..]),oldStrength=BitConverter.ToSingle(frame[(at+48)..]);
                    uint beamFlags=BitConverter.ToUInt32(frame[(at+12)..]),beforeActive=BitConverter.ToUInt32(frame[(at+52)..]);
                    bool param=rest!=oldRest||kval!=oldK,weak=strengthNow!=oldStrength,remove=beforeActive!=0&&(beamFlags&3)!=0;
                    if(rest>0)strain=Math.Max(strain,Math.Abs(length-rest)/rest);
                    if(param)++parameters;if(weak)++strength;if(remove)++removed;
                    if(param||weak||remove)transitions?.WriteLine(System.Text.Json.JsonSerializer.Serialize(new{tick,beam=i,lengthM=length,oldRestM=oldRest,newRestM=rest,oldK,newK=kval,oldStrengthN=oldStrength,newStrengthN=strengthNow,beamFlags,removed=remove,storageInterpretation="Linear diagnostic only; removal is not fracture dissipation"},Contract.Json));
                }
                double[] net=new double[3];
                for(int i=0;i<cc;++i){int at=128+nodes*256+beams*112+i*104;
                    int node=BitConverter.ToInt32(frame[at..]);uint kind=BitConverter.ToUInt32(frame[(at+4)..]),isBarrier=BitConverter.ToUInt32(frame[(at+12)..]);
                    if(node<0||node>=nodes||kind is <1 or >3||isBarrier>1)throw new InvalidDataException("Invalid contact identity.");
                    for(int k=16;k<96;k+=4)if(!float.IsFinite(BitConverter.ToSingle(frame[(at+k)..])))throw new InvalidDataException("Nonfinite contact detail.");
                    ++contacts;if(isBarrier==0)continue;++barrier;
                    double f2=0,dot=0;int nodeAt=128+node*256;
                    for(int j=0;j<3;++j)dot+=BitConverter.ToSingle(frame[(at+64+j*4)..])*BitConverter.ToSingle(frame[(at+28+j*4)..]);
                    double tangent2=0;
                    for(int j=0;j<3;++j){double applied=BitConverter.ToSingle(frame[(at+64+j*4)..]);
                        net[j]+=applied;impulse[j]+=applied*dt;f2+=applied*applied;
                        double normal=dot*BitConverter.ToSingle(frame[(at+28+j*4)..]),tangent=applied-normal;
                        normalImpulse[j]+=normal*dt;tangentialImpulse[j]+=tangent*dt;tangent2+=tangent*tangent;
                        double before=BitConverter.ToSingle(frame[(nodeAt+28+j*4)..]),after=BitConverter.ToSingle(frame[(nodeAt+40+j*4)..]);
                        work+=applied*(before+after)*.5*dt;
                    }
                    double mag=Math.Sqrt(f2);peak=Math.Max(peak,mag);nodePeaks[node]=Math.Max(nodePeaks.GetValueOrDefault(node),mag);
                    peakNormal=Math.Max(peakNormal,Math.Abs(dot));peakTangential=Math.Max(peakTangential,Math.Sqrt(tangent2));
                }
                peakNet=Math.Max(peakNet,Math.Sqrt(net.Sum(v=>v*v)));
                if(first==0)first=tick;last=tick;++records;
                index?.WriteLine(System.Text.Json.JsonSerializer.Serialize(new{tick,offset,size,crc},Contract.Json));
            }
        }catch(Exception e)when(e is IOException or UnauthorizedAccessException or InvalidDataException or OverflowException){problem=e.Message;}
        if(!closed)problem??="No clean detail footer; verified prefix retained.";
        if(triggerTick<=0||requiredEndTick<triggerTick+8000)problem??="No declared consumed impact window.";
        if(first!=triggerTick-4000||last<requiredEndTick)problem??="Required pre/posthistory unavailable.";
        if(records==0||barrier==0)problem??="No required impact detail.";
        return new(records,closed,closed&&problem==null,problem,first,last,triggerTick,dropped,missing,nodes,beams,contacts,barrier,parameters,strength,removed,peak,peakNet,impulse,work,strain,nodePeaks){
            NormalImpulseNs=normalImpulse,TangentialImpulseNs=tangentialImpulse,PeakNormalApplicationForceN=peakNormal,PeakTangentialApplicationForceN=peakTangential};
    }

    public static object? Sample(string directory,long tick,int node,int beam)
    {
        string indexPath=Path.Combine(directory,"detail-index.jsonl");if(!File.Exists(indexPath))return null;
        long offset=-1;
        foreach(string line in File.ReadLines(indexPath)){using var entry=System.Text.Json.JsonDocument.Parse(line);
            if(entry.RootElement.GetProperty("tick").GetInt64()==tick){offset=entry.RootElement.GetProperty("offset").GetInt64();break;}}
        if(offset<32)return null;
        using var f=File.OpenRead(Path.Combine(directory,"detail.rort"));using var r=new BinaryReader(f);
        if(Encoding.ASCII.GetString(r.ReadBytes(8))!="RORDTAIL"||r.ReadUInt32()!=1)throw new InvalidDataException("Invalid indexed detail.");
        int nodes=checked((int)r.ReadUInt32()),beams=checked((int)r.ReadUInt32());uint cap=r.ReadUInt32();
        if(node<0||node>=nodes||beam<0||beam>=beams)throw new ArgumentException("Node/beam outside recorded cohort.");
        f.Position=offset;if(Encoding.ASCII.GetString(r.ReadBytes(4))!="DATA"||r.ReadUInt32()!=1)throw new InvalidDataException("Invalid index offset.");
        uint size=r.ReadUInt32(),crc=r.ReadUInt32();if(size>128L+nodes*256L+beams*112L+cap*104L||size<128L+nodes*256L+beams*112L)throw new InvalidDataException("Invalid indexed frame length.");
        byte[] data=r.ReadBytes((int)size);if(data.Length!=size||ArchiveReader.Crc(data)!=crc||Encoding.ASCII.GetString(r.ReadBytes(4))!="DONE"||BitConverter.ToInt64(data,0)!=tick)throw new InvalidDataException("Indexed frame failed checksum/identity.");
        double[] Vector(int at)=>[BitConverter.ToSingle(data,at),BitConverter.ToSingle(data,at+4),BitConverter.ToSingle(data,at+8)];
        int n=128+node*256,b=128+nodes*256+beam*112,count=BitConverter.ToInt32(data,28);
        var channels=Enumerable.Range(0,16).ToDictionary(i=>ArchiveReader.ChannelNames[i],i=>Vector(n+64+i*12));
        List<object> contacts=[];
        for(int i=0;i<count;++i){int c=128+nodes*256+beams*112+i*104;var normal=Vector(c+28);var force=Vector(c+64);double dot=force.Zip(normal,(x,y)=>x*y).Sum();
            double[] normalForce=normal.Select(x=>x*dot).ToArray(),tangent=force.Zip(normalForce,(x,y)=>x-y).ToArray();
            contacts.Add(new{node=BitConverter.ToUInt32(data,c),kind=BitConverter.ToUInt32(data,c+4),feature=BitConverter.ToUInt32(data,c+8),barrier=BitConverter.ToUInt32(data,c+12)!=0,materialId=BitConverter.ToUInt32(data,c+96),positionM=Vector(c+16),normal,velocityMps=Vector(c+40),rawForceN=Vector(c+52),appliedForceN=force,normalForceN=normalForce,tangentialForceN=tangent});}
        return new{tick,dt=BitConverter.ToDouble(data,8),precision="Native float32 state/applications; double tick clock",node=new{id=node,massKg=BitConverter.ToSingle(data,n+8),positionM=Vector(n+16),beforeVelocityMps=Vector(n+28),velocityMps=Vector(n+40),consumedForceN=Vector(n+52),channels},
            beam=new{id=beam,node1=BitConverter.ToUInt32(data,b+4),node2=BitConverter.ToUInt32(data,b+8),flags=BitConverter.ToUInt32(data,b+12),lengthM=BitConverter.ToSingle(data,b+16),restM=BitConverter.ToSingle(data,b+20),stressN=BitConverter.ToSingle(data,b+32),strengthN=BitConverter.ToSingle(data,b+36),beforeRestM=BitConverter.ToSingle(data,b+40),beforeStrengthN=BitConverter.ToSingle(data,b+48),generatedNode1ForceN=Vector(b+64),generatedNode2ForceN=Vector(b+76),elasticForceN=Vector(b+88),dampingForceN=Vector(b+100)},contacts};
    }
}
