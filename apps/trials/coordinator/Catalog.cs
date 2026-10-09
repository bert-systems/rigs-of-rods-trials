using Microsoft.Data.Sqlite;
using System.Text.Json;
namespace RoR.Trials;

public sealed class Catalog
{
    readonly string connection;
    public Catalog(string archive)
    {
        Directory.CreateDirectory(archive);
        connection = $"Data Source={Path.Combine(archive,"catalog.sqlite")}";
        using var db = Open();
        using var sql = db.CreateCommand();
        sql.CommandText = "PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS attempts(id TEXT PRIMARY KEY, body TEXT NOT NULL);";
        sql.ExecuteNonQuery();
    }
    SqliteConnection Open() { var db = new SqliteConnection(connection); db.Open(); return db; }
    public List<Attempt> Load()
    {
        using var db = Open(); using var sql = db.CreateCommand();
        sql.CommandText = "SELECT body FROM attempts ORDER BY rowid;";
        using var reader = sql.ExecuteReader(); var attempts = new List<Attempt>();
        while (reader.Read()) attempts.Add(JsonSerializer.Deserialize<Attempt>(reader.GetString(0), Contract.Json)!);
        return attempts;
    }
    public void Save(Attempt attempt)
    {
        using var db = Open(); using var sql = db.CreateCommand();
        sql.CommandText = "INSERT INTO attempts(id,body) VALUES($id,$body) ON CONFLICT(id) DO UPDATE SET body=$body;";
        sql.Parameters.AddWithValue("$id", attempt.Id);
        sql.Parameters.AddWithValue("$body", JsonSerializer.Serialize(attempt, Contract.Json));
        sql.ExecuteNonQuery();
    }
}
