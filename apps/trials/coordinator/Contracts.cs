using System.Text.Json;
namespace RoR.Trials;

public sealed record EnvironmentConfig(double Gravity = -9.81, double TemperatureK = 288.15,
    double Density = 1.225, double WindX = 0, double WindY = 0, double WindZ = 0);
public sealed record ExperimentDefinition(string Name, double LaunchSpeedMps = 5,
    double DurationSeconds = 12, double SettleSeconds = 3, int Repeats = 1,
    EnvironmentConfig? Environment = null, string Vehicle = "b6b0UID-semi.truck",
    string Terrain = "simple2.terrn2", string Scenario = "coast-v1");
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
    public string Coverage { get; set; } = "Total consumed force + ground/object contact; model attribution incomplete";
    public string? BlockedReason { get; set; }
    public int? ProcessId { get; set; }
    public string? ExecutableSha256 { get; set; }
    public string? ProcessPath { get; set; }
    public string? ArchivePath { get; set; }
    public long CommandSequence { get; set; }
    public JsonElement? WorkerStatus { get; set; }
    public JsonElement? Latest { get; set; }
    public List<JsonElement> History { get; set; } = [];
    public List<AttemptEvent> Events { get; set; } = [];
    public Dictionary<string, object> Metrics { get; set; } = [];
    public bool CancelRequested { get; set; }
    public bool Archived { get; set; }
}
public static class Contract
{
    public static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web) { WriteIndented = false };
    public static List<string> Validate(ExperimentDefinition d)
    {
        var errors = new List<string>();
        if (string.IsNullOrWhiteSpace(d.Name) || d.Name.Length > 120) errors.Add("Name must contain 1–120 characters.");
        if (d.Vehicle != "b6b0UID-semi.truck" || d.Terrain != "simple2.terrn2" || d.Scenario != "coast-v1")
            errors.Add("Slice 1 supports the pinned Daf / Simple2 coasting scenario only.");
        if (!double.IsFinite(d.LaunchSpeedMps) || d.LaunchSpeedMps < 0 || d.LaunchSpeedMps > 20) errors.Add("Launch speed must be 0–20 m/s.");
        if (!double.IsFinite(d.DurationSeconds) || d.DurationSeconds < 1 || d.DurationSeconds > 120) errors.Add("Duration must be 1–120 simulated seconds.");
        if (!double.IsFinite(d.SettleSeconds) || d.SettleSeconds < 2 || d.SettleSeconds > 30) errors.Add("Settling must be 2–30 simulated seconds.");
        if (d.Repeats < 1 || d.Repeats > 20) errors.Add("Repeats must be 1–20.");
        var e = d.Environment ?? new();
        if (!double.IsFinite(e.Gravity) || e.Gravity >= 0 || e.Gravity < -30) errors.Add("Gravity must be negative and at least −30 m/s²; zero gravity is not qualified.");
        if (!double.IsFinite(e.TemperatureK) || e.TemperatureK < 180 || e.TemperatureK > 350) errors.Add("Dry-air temperature must be 180–350 K.");
        if (!double.IsFinite(e.Density) || e.Density <= 0 || e.Density > 3) errors.Add("Density must be >0 and ≤3 kg/m³.");
        if (new[] { e.WindX, e.WindY, e.WindZ }.Any(v => !double.IsFinite(v)) ||
            Math.Sqrt(e.WindX * e.WindX + e.WindY * e.WindY + e.WindZ * e.WindZ) > 30) errors.Add("Wind magnitude must be ≤30 m/s.");
        return errors;
    }
}
