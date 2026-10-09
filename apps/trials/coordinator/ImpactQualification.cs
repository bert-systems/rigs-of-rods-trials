using System.Text.Json;
namespace RoR.Trials;
public static class ImpactQualification
{
    public sealed record Result(string Status,string Profile,string Scope,List<FixtureValidation.Item> Checks);
    public static Result Evaluate(ExperimentDefinition d,DetailReader.Check detail,JsonElement? approach,bool completed,bool captureComplete)
    {
        var checks=new List<FixtureValidation.Item>();
        const string scope="Controlled approach and required 2 kHz impact capture only; vehicle energy/material accuracy remains NotReady";
        if(!completed||!captureComplete||!detail.Complete||approach is not {} a||d.DetailFault!="none")return new("NotReady","barrier-approach-capture-v1",scope,checks);
        void Check(string name,double observed,double limit)=>checks.Add(new(name,observed,limit,double.IsFinite(observed)&&observed<=limit));
        double target=d.TargetImpactSpeedMps??d.LaunchSpeedMps;
        Check("approach speed absolute error / m/s",Math.Abs(a.GetProperty("speedMps").GetDouble()-target),Math.Max(.1,target*.02));
        Check("heading alignment / degrees",Math.Abs(a.GetProperty("headingDegrees").GetDouble()),1);
        Check("lateral displacement / m",Math.Abs(a.GetProperty("lateralM").GetDouble()),.25);
        Check("approach must precede consumed impact / ticks",Math.Max(0,a.GetProperty("tick").GetInt64()-detail.TriggerTick),0);
        Check("required prehistory missing / ticks",Math.Abs(detail.FirstTick-(detail.TriggerTick-4000)),0);
        Check("required detail dropped / records",detail.Dropped,0);
        return new(checks.All(c=>c.Passed)?"Passed":"Failed","barrier-approach-capture-v1",scope,checks);
    }
}
