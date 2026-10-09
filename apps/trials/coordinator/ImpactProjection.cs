using System.Text.Json;
namespace RoR.Trials;
// Each 20 Hz display point preserves the maximum of all ten 200 Hz summary envelopes.
public sealed class ImpactProjection
{
    double peak;long previous;bool gap;JsonElement? last;
    public void Add(Attempt attempt,JsonElement sample){
        long tick=sample.GetProperty("tick").GetInt64();
        if(previous!=0&&tick<=previous)return;
        gap|=previous!=0&&tick!=previous+10;
        gap|=sample.GetProperty("detailDropped").GetInt64()>0||sample.GetProperty("detailIoError").GetBoolean();
        peak=Math.Max(peak,sample.GetProperty("peakNetBarrierForceN").GetDouble());previous=tick;last=sample;attempt.Impact=sample;
        if(tick%100==0)Flush(attempt);
    }
    public void Flush(Attempt attempt){
        if(last is not {} sample)return;
        attempt.ImpactHistory.Add(JsonSerializer.SerializeToElement(new{tick=sample.GetProperty("tick").GetInt64(),timeSeconds=sample.GetProperty("timeSeconds").GetDouble(),peakNetBarrierForceN=peak,gap},Contract.Json));
        if(attempt.ImpactHistory.Count>2000)attempt.ImpactHistory.RemoveAt(0);
        peak=0;gap=false;last=null;
    }
    public static void Restore(Attempt attempt){
        string path=Path.Combine(attempt.ArchivePath!,"impact-summaries.jsonl");if(!File.Exists(path))return;
        attempt.ImpactHistory.Clear();var collector=new ImpactProjection();
        foreach(string line in File.ReadLines(path)){try{using var doc=JsonDocument.Parse(line);collector.Add(attempt,doc.RootElement.Clone());}catch(JsonException){}}
        collector.Flush(attempt);
    }
}
