namespace RoR.Trials;

// A bounded view of CRC-verified aggregate transitions. Dense impact detail remains authoritative
// when the aggregate projection reports omissions. No interpolation or inferred dissipation.
public static class TransitionReader
{
    public sealed record Event(long Tick,uint Beam,uint Kind,double LengthM,double OldRestM,double NewRestM,
        double OldK,double NewK,double OldStrengthN,double NewStrengthN,double OldStorageJ,double NewStorageJ,
        double LawStressN,double RestStoragePortJ,double RemovedStoragePortJ);
    public sealed record Page(bool ProjectionComplete,long Total,long Omitted,long ParameterChanges,long StrengthChanges,
        long Removed,double RestStoragePortJ,double RemovedStoragePortJ,long Offset,int Limit,List<Event> Events);
    public static Page Read(string path,ArchiveReader.Check capture,long offset=0,int limit=50)
    {
        if(offset<0||offset>1_000_000||limit<1||limit>100)throw new ArgumentException("Transition offset 0–1,000,000; page size 1–100.");
        if(!capture.Complete)throw new InvalidDataException("Transition view requires a complete verified aggregate archive.");
        long total=0,omitted=0,parameters=0,strength=0,removed=0,records=0;double restPort=0,removalPort=0;
        var events=new List<Event>();
        foreach(var r in ArchiveReader.VerifiedRecords(path)){
            ++records;
            double At(int n)=>BitConverter.ToDouble(r,n);
            long tick=(long)BitConverter.ToUInt64(r,0);
            omitted+=BitConverter.ToUInt32(r,1372);restPort+=At(1232);removalPort+=At(1240);
            for(int i=0;i<BitConverter.ToUInt32(r,1368);i++){
                int at=1376+i*88;uint beam=BitConverter.ToUInt32(r,at),kind=BitConverter.ToUInt32(r,at+4);
                double length=At(at+8),oldRest=At(at+16),newRest=At(at+24),oldK=At(at+32),newK=At(at+40),
                    oldStrength=At(at+48),newStrength=At(at+56),oldStorage=At(at+64),newStorage=At(at+72),stress=At(at+80);
                if((kind&9)!=0)++parameters;if(oldStrength!=newStrength)++strength;if((kind&2)!=0)++removed;
                if(total>=offset&&events.Count<limit)events.Add(new(tick,beam,kind,length,oldRest,newRest,oldK,newK,
                    oldStrength,newStrength,oldStorage,newStorage,stress,(kind&9)!=0?newStorage-oldStorage:0,(kind&2)!=0?-newStorage:0));
                ++total;
            }
        }
        if(records!=capture.Records)throw new InvalidDataException("Schema 2 transition archive required; verified record count changed.");
        return new(omitted==0,total,omitted,parameters,strength,removed,restPort,removalPort,offset,limit,events);
    }
}
