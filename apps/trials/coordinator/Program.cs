using RoR.Trials;
using System.Security.Cryptography;

var settings=new ConfigurationBuilder().AddCommandLine(args).Build();
var builder=WebApplication.CreateBuilder(new WebApplicationOptions { Args=args, WebRootPath=Path.GetFullPath(settings["web-root"]??"../workbench/dist") });
builder.WebHost.UseUrls("http://127.0.0.1:"+(builder.Configuration["port"]??"54321"));
builder.Services.AddSingleton<TrialService>();
builder.Services.AddHostedService(p=>p.GetRequiredService<TrialService>());
var app=builder.Build();
string session=Convert.ToHexString(RandomNumberGenerator.GetBytes(32));
app.Use(async(context,next)=>{
    if(context.Request.Host.Host is not ("127.0.0.1" or "localhost")) { context.Response.StatusCode=403; return; }
    if(context.Request.Method is not ("GET" or "HEAD"))
    {
        string origin=context.Request.Headers.Origin.ToString();
        if(origin.Length>0 && (!Uri.TryCreate(origin,UriKind.Absolute,out var uri) ||
            uri.Host!=context.Request.Host.Host || uri.Port!=context.Request.Host.Port))
        {context.Response.StatusCode=403;return;}
        if(context.Request.Headers["X-Trials-Session"]!=session){context.Response.StatusCode=403;return;}
    }
    context.Response.Headers["X-Content-Type-Options"]="nosniff";
    await next();
});
app.UseDefaultFiles();app.UseStaticFiles();
app.MapGet("/api/session",()=>new{session});
app.MapGet("/api/state",(TrialService s)=>s.Snapshot());
app.MapGet("/api/attempts/{id}/status",(string id,TrialService s)=>s.AttemptSnapshot(id) is {} a?Results.Ok(a):Results.NotFound());
app.MapPost("/api/experiments",(ExperimentDefinition definition,TrialService s)=>{
    try{return Results.Ok(new{attemptIds=s.Enqueue(definition)});}
    catch(ArgumentException e){return Results.BadRequest(new{error=e.Message});}
});
app.MapPost("/api/attempts/{id}/{operation}",(string id,string operation,TrialService s)=>{
    try{s.Command(id,operation);return Results.Ok(new{accepted=true});}
    catch(ArgumentException e){return Results.BadRequest(new{error=e.Message});}
});
app.MapGet("/api/attempts/{id}/artifacts/{name}",(string id,string name,TrialService s)=>{
    var path=s.Artifact(id,name);
    return path!=null&&File.Exists(path)?Results.File(path,name.EndsWith(".json")?"application/json":"application/octet-stream",name):Results.NotFound();
});
app.MapFallbackToFile("index.html");
app.Run();
