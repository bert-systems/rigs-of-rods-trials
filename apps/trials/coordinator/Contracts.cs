using System.Text.Json;
namespace RoR.Trials;

public sealed record EnvironmentConfig(double Gravity = -9.81, double TemperatureK = 288.15,
    double Density = 1.225, double WindX = 0, double WindY = 0, double WindZ = 0);
public sealed record ExperimentDefinition(string Name, double LaunchSpeedMps = 5,
    double DurationSeconds = 12, double SettleSeconds = 3, int Repeats = 1,
    EnvironmentConfig? Environment = null, string Vehicle = "b6b0UID-semi.truck",
    string Terrain = "simple2.terrn2", string Scenario = "coast-v1", bool Accounting = true,
    string Observation = "full", bool PerformanceProbe = false, double BarrierDistanceM = 12,
    double? TargetImpactSpeedMps = null, string DetailFault = "none");
public sealed record AttemptEvent(long Sequence, DateTimeOffset Time, string Kind, string Message);
public sealed class Attempt
{
    public string Id { get; init; } = Guid.NewGuid().ToString("N");
    public string RevisionId { get; init; } = "";
    public string? RetryOf { get; init; }
    public ExperimentDefinition Definition { get; init; } = null!;
    public string DefinitionSha256 { get; init; } = "";
    public string Execution { get; set; } = "Queued";
    public string Capture { get; set; } = "Pending";
    public string Validation { get; set; } = "NotReady";
    public string Coverage { get; set; } = "16 consumed/generated force channels; linear beam storage subset; nonlinear and environmental closure unqualified";
    public string? BlockedReason { get; set; }
    public int? ProcessId { get; set; }
    public string? ExecutableSha256 { get; set; }
    public string? ProcessPath { get; set; }
    public string? ArchivePath { get; set; }
    public long CommandSequence { get; set; }
    public JsonElement? WorkerStatus { get; set; }
    public JsonElement? Latest { get; set; }
    public List<JsonElement> History { get; set; } = [];
    public JsonElement? Impact { get; set; }
    public JsonElement? DetailProgress { get; set; }
    public List<JsonElement> ImpactHistory { get; set; } = [];
    public List<AttemptEvent> Events { get; set; } = [];
    public Dictionary<string, object> Metrics { get; set; } = [];
    public bool CancelRequested { get; set; }
    public bool Archived { get; set; }
}
public static class Contract
{
    public static bool TransitionFixture(string scenario)=>scenario is "yield-tension-v1" or "yield-compression-v1" or "fracture-v1" or "protected-beam-v1";
    public static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web) { WriteIndented = false };
    public static List<string> Validate(ExperimentDefinition d)
    {
        var errors = new List<string>();
        if(d.Observation is not ("full" or "off"))errors.Add("Observation must be full or off.");
        if(d.Observation=="off"&&!d.PerformanceProbe)errors.Add("Ledger-off runs require the declared timing/state probe.");
        if (string.IsNullOrWhiteSpace(d.Name) || d.Name.Length > 120) errors.Add("Name must contain 1–120 characters.");
        bool transition=TransitionFixture(d.Scenario);
        bool fixture=transition||d.Scenario is "freefall-v1" or "spring-v1" or "damper-v1";
        bool barrier=d.Scenario=="barrier-v1";
        if ((!fixture && !barrier && d.Scenario!="coast-v1") || d.Terrain!="simple2.terrn2" ||
            d.Vehicle!=(fixture?"ror-"+d.Scenario+".truck":"b6b0UID-semi.truck"))
            errors.Add("Choose a pinned coast or analytical fixture scenario/asset pair.");
        if (!double.IsFinite(d.LaunchSpeedMps) || d.LaunchSpeedMps < 0 || d.LaunchSpeedMps > 20) errors.Add("Launch speed must be 0–20 m/s.");
        if (!double.IsFinite(d.DurationSeconds) || d.DurationSeconds < (fixture?.1:1) || d.DurationSeconds > (fixture?5:120)) errors.Add("Duration outside scenario range (fixture 0.1–5 s; coast 1–120 s).");
        if (!double.IsFinite(d.SettleSeconds) || (fixture ? d.SettleSeconds!=0 : d.SettleSeconds<2||d.SettleSeconds>30)) errors.Add("Fixtures require zero settling; coast requires 2–30 s.");
        if(fixture && d.LaunchSpeedMps!=0)errors.Add("Fixtures use the pinned initial state, with zero release speed.");
        if(transition&&d.DurationSeconds>1)errors.Add("Transition fixtures use a 0.1–1 s qualification window.");
        if (d.Repeats < 1 || d.Repeats > 20) errors.Add("Repeats must be 1–20.");
        if(d.DetailFault is not ("none" or "queue-overflow" or "storage-error" or "short-history"))errors.Add("Unknown detail fault qualification profile.");
        if(!barrier&&d.DetailFault!="none")errors.Add("Detail fault profiles require the controlled barrier scenario.");
        if(barrier){
            if(d.Observation!="full"||!d.Accounting)errors.Add("Barrier detail requires full force accounting.");
            if(!double.IsFinite(d.BarrierDistanceM)||d.BarrierDistanceM<1||d.BarrierDistanceM>100)errors.Add("Barrier distance must be 1–100 m from the initial front.");
            double target=d.TargetImpactSpeedMps??d.LaunchSpeedMps;
            if(!double.IsFinite(target)||target<=0||target>20||d.LaunchSpeedMps<=0)errors.Add("Barrier target/release speeds must be >0 and ≤20 m/s.");
            if(d.DurationSeconds<6)errors.Add("Barrier duration must be at least 6 s; pre/post coverage is verified from actual trigger ticks.");
        }
        var e = d.Environment ?? new();
        if (!double.IsFinite(e.Gravity) || e.Gravity < -30 || (transition||d.Scenario is "spring-v1" or "damper-v1" ? e.Gravity!=0 : e.Gravity>=0))
            errors.Add("Coast/freefall require negative gravity; spring/damper require zero gravity.");
        if(fixture && (e.WindX!=0 || e.WindY!=0 || e.WindZ!=0))errors.Add("Analytical dry fixtures require zero wind (drag disabled).");
        if (!double.IsFinite(e.TemperatureK) || e.TemperatureK < 180 || e.TemperatureK > 350) errors.Add("Dry-air temperature must be 180–350 K.");
        if (!double.IsFinite(e.Density) || e.Density <= 0 || e.Density > 3) errors.Add("Density must be >0 and ≤3 kg/m³.");
        if (new[] { e.WindX, e.WindY, e.WindZ }.Any(v => !double.IsFinite(v)) ||
            Math.Sqrt(e.WindX * e.WindX + e.WindY * e.WindY + e.WindZ * e.WindZ) > 30) errors.Add("Wind magnitude must be ≤30 m/s.");
        return errors;
    }
}
