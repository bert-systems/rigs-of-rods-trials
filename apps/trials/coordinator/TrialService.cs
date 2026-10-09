using System.Diagnostics;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading.Channels;
namespace RoR.Trials;

public sealed class TrialService : BackgroundService
{
    readonly object gate=new();
    readonly Catalog catalog;
    readonly List<Attempt> attempts;
    readonly Channel<string> queue=Channel.CreateUnbounded<string>(new(){SingleReader=true});
    readonly string gameBin, archive, renderer;
    readonly bool evidenceFrames;
    public TrialService(IConfiguration config)
    {
        evidenceFrames=string.Equals(config["evidence-frames"],"true",StringComparison.OrdinalIgnoreCase);
        renderer=config["renderer"]??"Direct3D9";
        if(renderer is not ("Direct3D9" or "OpenGL"))throw new ArgumentException("Renderer must be Direct3D9 or OpenGL.");
        gameBin=Path.GetFullPath(config["game-bin"] ?? throw new ArgumentException("--game-bin is required"));
        archive=Path.GetFullPath(config["archive"] ?? throw new ArgumentException("--archive is required"));
        if(archive.Contains("source-build-2026-10-08",StringComparison.OrdinalIgnoreCase) ||
           archive.StartsWith(Path.GetFullPath(config["repo"] ?? Directory.GetCurrentDirectory())+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException("Trial archives must be outside the checkout and protected baseline.");
        catalog=new(archive); attempts=catalog.Load();
        foreach(var a in attempts)
        {
            if(a.Definition.Scenario=="barrier-v1"&&a.Execution is "Completed" or "Failed" or "Cancelled")ImpactProjection.Restore(a);
            if(a.Execution=="Queued") queue.Writer.TryWrite(a.Id);
            else if(a.Execution is "Starting" or "Running" or "Finalizing" or "Paused" or "Pausing" or "Resuming" or "Cancelling")
            {
                a.Execution="Interrupted"; a.Capture="Incomplete"; a.Validation="NotReady";
                AddEvent(a,"recovery","Coordinator restart: retained partial attempt; no automatic retry.");
                catalog.Save(a);
            }
        }
    }
    public object Configuration => new { gameBin, archive, renderer, evidenceFrames, scenarios=new[]{"coast-v1","barrier-v1","freefall-v1","spring-v1","damper-v1","yield-tension-v1","yield-compression-v1","fracture-v1","protected-beam-v1"}, nativeCoverage="accounting-v2 / transition-flags-v2",
        retention="Manual; no automatic deletion", captureProfile="Every-step aggregates; barrier all-node/channel/beam/contact detail at 2 kHz, 2 s pre/4 s post; ~200 Hz summaries",
        unavailable=new[]{"Nonlinear storage and full model energy closure","Driven journeys","Flight/gust/particles"} };
    public object Snapshot(string? selected=null,bool compact=false)
    {
        lock(gate){string? focus=attempts.Find(a=>a.Id==selected)?.Id??attempts.Find(a=>a.Execution is "Running" or "Finalizing" or "Starting" or "Paused" or "Pausing" or "Resuming")?.Id??attempts.LastOrDefault()?.Id;return new { configuration=Configuration, attempts=attempts.Select(a=>new {
            a.Id,a.RevisionId,a.RetryOf,a.Definition,a.DefinitionSha256,a.Execution,a.Capture,a.Validation,a.Coverage,
            a.BlockedReason,a.ProcessId,a.ProcessPath,a.ExecutableSha256,a.ArchivePath,a.Latest,a.WorkerStatus,a.Impact,a.DetailProgress,
            history=(!compact||a.Id==focus?a.History:[]).ToArray(),impactHistory=(!compact||a.Id==focus?a.ImpactHistory:[]).ToArray(),events=a.Events.ToArray(),metrics=new Dictionary<string,object>(a.Metrics),a.Archived
        }).ToArray() };}
    }
    // Compact polling endpoint keeps completed history out of worker supervision reads.
    public object? AttemptSnapshot(string id)
    {
        lock(gate){
            var a=attempts.Find(x=>x.Id==id);if(a==null)return null;
            return new {a.Id,a.RevisionId,a.RetryOf,a.Definition,a.DefinitionSha256,a.Execution,a.Capture,a.Validation,a.Coverage,
                a.BlockedReason,a.ProcessId,a.ProcessPath,a.ExecutableSha256,a.ArchivePath,a.Latest,a.WorkerStatus,a.Impact,a.DetailProgress,
                events=a.Events.ToArray(),metrics=new Dictionary<string,object>(a.Metrics),a.Archived};
        }
    }
    public Attempt? Find(string id) { lock(gate) return attempts.Find(a=>a.Id==id); }
    public string[] Enqueue(ExperimentDefinition definition,string? retryOf=null)
    {
        var errors=Contract.Validate(definition);
        if(errors.Count>0) throw new ArgumentException(string.Join(" ",errors));
        var revision=Guid.NewGuid().ToString("N");
        var immutable=definition with { Environment=definition.Environment??new() };
        var hash=Convert.ToHexString(SHA256.HashData(JsonSerializer.SerializeToUtf8Bytes(immutable,Contract.Json)));
        List<string> ids=[];
        lock(gate) for(int i=0;i<definition.Repeats;i++)
        {
            var a=new Attempt{RevisionId=revision,RetryOf=retryOf,Definition=immutable,DefinitionSha256=hash};
            if(immutable.Observation=="off")a.Coverage="Ledger disabled: sentinel state and 10 Hz node/beam fingerprints only; no force/energy capture";
            a.ArchivePath=Path.Combine(archive,a.Id);
            Directory.CreateDirectory(a.ArchivePath);
            AddEvent(a,"queued",$"Repeat {i+1}/{definition.Repeats}; immutable revision {revision}.");
            attempts.Add(a); catalog.Save(a); ids.Add(a.Id); queue.Writer.TryWrite(a.Id);
        }
        return ids.ToArray();
    }
    public void Command(string id,string operation)
    {
        lock(gate)
        {
            var a=attempts.Find(a=>a.Id==id)??throw new ArgumentException("Unknown attempt.");
            if(operation=="retry")
            {
                if(a.Execution is not ("Completed" or "Failed" or "Cancelled" or "Interrupted")) throw new ArgumentException("Only a terminal attempt can be retried.");
                Enqueue(a.Definition with { Repeats=1 },a.Id); return;
            }
            if(operation=="archive")
            {
                if(a.Execution is not ("Completed" or "Failed" or "Cancelled" or "Interrupted")) throw new ArgumentException("Active attempts cannot be archived.");
                a.Archived=true; AddEvent(a,"archived","Marked archived; files retained. No deletion."); catalog.Save(a); return;
            }
            if(operation=="cancel" && a.Execution=="Queued")
            { a.Execution="Cancelled"; a.Capture="NotStarted"; AddEvent(a,"cancelled","Cancelled before launch."); catalog.Save(a); return; }
            if(operation=="pause" && a.Execution!="Running" || operation=="resume" && a.Execution!="Paused" ||
               operation=="cancel" && a.Execution is not ("Running" or "Paused") ||
               operation is not ("pause" or "resume" or "cancel")) throw new ArgumentException("Command not valid in the current execution state.");
            ++a.CommandSequence;
            AtomicJson(Path.Combine(a.ArchivePath!,"command.json"),new {sequence=a.CommandSequence,operation});
            if(operation=="cancel") a.CancelRequested=true;
            a.Execution=operation=="pause"?"Pausing":operation=="resume"?"Resuming":"Cancelling";
            AddEvent(a,"command-requested",$"{operation}; sequence {a.CommandSequence}, waiting for native applied tick.");
            catalog.Save(a);
        }
    }
    protected override async Task ExecuteAsync(CancellationToken stop)
    {
        await foreach(string id in queue.Reader.ReadAllAsync(stop))
        {
            var a=Find(id)!;
            if(a.Execution!="Queued") continue;
            while(!stop.IsCancellationRequested)
            {
                string? reason=Preflight(a.Definition);
                lock(gate) { a.BlockedReason=reason; catalog.Save(a); }
                if(reason==null) break;
                await Task.Delay(1000,stop);
                if(a.Execution!="Queued") break;
            }
            if(a.Execution!="Queued") continue;
            try { await Run(a,stop); }
            catch(Exception e)
            {
                lock(gate) { a.Execution="Failed"; a.Capture="Incomplete"; a.Validation="NotReady"; AddEvent(a,"failed",e.Message); catalog.Save(a); }
                AtomicJson(Path.Combine(a.ArchivePath!,"result.json"),a);
            }
        }
    }
    string? Preflight(ExperimentDefinition definition)
    {
        if(definition.Scenario=="barrier-v1"&&WorkerResources.MemoryPreflight() is {} memory)return memory;
        string exe=Path.Combine(gameBin,"RoR.exe");
        if(!File.Exists(exe)) return "Source-build RoR.exe unavailable: "+exe;
        if(!Directory.Exists(Path.Combine(gameBin,"resources")) || !Directory.Exists(Path.Combine(gameBin,"content")))
            return "Compiled runtime resources/content unavailable.";
        long reservation=definition.Scenario=="barrier-v1"?3L*1024*1024*1024:1L*1024*1024*1024;
        if(new DriveInfo(Path.GetPathRoot(archive)!).AvailableFreeSpace<10L*1024*1024*1024+reservation) return "Storage below 10 GiB floor plus declared attempt reservation; new launches held.";
        string storageProbe=Path.Combine(archive,".storage-preflight-"+Guid.NewGuid().ToString("N"));
        try{using(var probe=new FileStream(storageProbe,FileMode.CreateNew,FileAccess.Write)){probe.WriteByte(1);probe.Flush(true);}File.Delete(storageProbe);}
        catch(Exception e)when(e is IOException or UnauthorizedAccessException){return "Shared archive storage unavailable; new launches held: "+e.Message;}
        Attempt[] interrupted;
        lock(gate) interrupted=attempts.Where(x=>x.Execution=="Interrupted" && x.ProcessId!=null).ToArray();
        foreach(var old in interrupted)
        {
            try { var p=Process.GetProcessById(old.ProcessId!.Value); if(!p.HasExited && p.MainModule?.FileName==old.ProcessPath) return "Owned interrupted worker still running; stop it before new launches."; }
            catch(ArgumentException) {}
        }
        return null;
    }
    async Task Run(Attempt a,CancellationToken stop)
    {
        string dir=a.ArchivePath!, bin=Path.Combine(dir,"worker"), source=Path.Combine(gameBin,"RoR.exe");
        lock(gate) { a.Execution="Starting"; a.Capture="Recording"; AddEvent(a,"starting","Creating private source-built worker/profile."); catalog.Save(a); }
        CopyTree(gameBin,bin);
        using(var zip=ZipFile.Open(Path.Combine(bin,"content","trial-fixtures.zip"),ZipArchiveMode.Create))
            foreach(string fixture in Directory.GetFiles(Path.Combine(AppContext.BaseDirectory,"fixtures"),"*.truck").Order())
                zip.CreateEntryFromFile(fixture,Path.GetFileName(fixture));
        Directory.CreateDirectory(Path.Combine(bin,"config","config"));
        Directory.CreateDirectory(Path.Combine(bin,"config","scripts"));
        File.WriteAllLines(Path.Combine(bin,"config","config","RoR.cfg"),[
            "app_config_long_names = false","app_disable_online_api = true","diag_preset_veh_enter = true",
            "gfx_fps_limit = 60","gfx_shadow_type = None","gfx_sky_mode = 0","gfx_water_mode = 1"]);
        File.WriteAllText(Path.Combine(bin,"config","config","ogre.cfg"),renderer=="OpenGL"?OpenGlConfig:RendererConfig);
        if(renderer=="OpenGL"){
            var plugins=Path.Combine(bin,"plugins.cfg");
            File.WriteAllText(plugins,File.ReadAllText(plugins).Replace("Plugin=RenderSystem_Direct3D9","# Plugin=RenderSystem_Direct3D9").Replace("# Plugin=RenderSystem_GL\n","Plugin=RenderSystem_GL\n").Replace("# Plugin=RenderSystem_GL\r\n","Plugin=RenderSystem_GL\r\n"));
        }
        var script=EvidenceScript;
        if(evidenceFrames)script=script.Replace("bool initialized=false","float nextShot=.5;\n        bool initialized=false")
            .Replace("elapsed+=dt;","elapsed+=dt; if(elapsed>=nextShot){nextShot+=.5;game.pushMessage(MSG_APP_SCREENSHOT_REQUESTED,null);}")
            .Replace("if(!s1","if(false&&!s1").Replace("if(!s2","if(false&&!s2");
        File.WriteAllText(Path.Combine(bin,"config","scripts","trial-evidence.as"),script);
        var e=a.Definition.Environment!;
        AtomicJson(Path.Combine(dir,"native-config.json"),new {
            schema=1,a.Definition.Scenario,a.Definition.Accounting,a.Definition.Observation,a.Definition.PerformanceProbe,a.Definition.LaunchSpeedMps,a.Definition.DurationSeconds,a.Definition.SettleSeconds,
            a.Definition.BarrierDistanceM,a.Definition.DetailFault,gravity=e.Gravity,density=e.Density,windX=e.WindX,windY=e.WindY,windZ=e.WindZ
        });
        string exe=Path.Combine(bin,"RoR.exe");
        a.ExecutableSha256=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(exe)));
        if(a.ExecutableSha256!=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(source)))) throw new IOException("Copied executable hash mismatch.");
        AtomicJson(Path.Combine(dir,"manifest.json"),new {
            schema=5,transitionFlags="1 linear parameters / 2 removed / 4 strength / 8 unsupported parameters; state changes, not calibrated fracture energy",
            transitionFixture=Contract.TransitionFixture(a.Definition.Scenario)?new {profile="beam-transition-reference-v1",springNpm=10000,damperNspm=0,initialExtensionM=a.Definition.Scenario=="yield-compression-v1"?-.05:.05,yieldN=a.Definition.Scenario.StartsWith("yield-")?200:1e9,initialStrengthN=a.Definition.Scenario.StartsWith("yield-")?2000:200,plasticCoefficient=.25,protectedCabNode=a.Definition.Scenario=="protected-beam-v1"}:null,
            resourceEstimate=a.Definition.Scenario=="barrier-v1"?WorkerResources.DetailEstimate:null,
            impactProfile=a.Definition.Scenario=="barrier-v1"?"whole-pilot-f32-v1 / barrier-approach-capture-v1":null,
            requiredDetail=a.Definition.Scenario=="barrier-v1"?new{preTicks=4000,postTicks=8000,nodeBytes=256,beamBytes=112,contactBytes=104,prehistoryBudgetMiB=1024,writerQueueBudgetMiB=3072,rawReservationGiB=3,resourceProfile="daf-detail-resources-v2"}:null,
            barrierAsset=a.Definition.Scenario=="barrier-v1"?new{asset="controlled-concrete-box-v1",geometry="native fixed collision box and visible mesh; resolved transform/material in barrier.json",speedDefinition="Signed movable-node COM velocity along frozen direction at front-node crossing 0.25 m before face",speedToleranceMps=Math.Max(.1,(a.Definition.TargetImpactSpeedMps??a.Definition.LaunchSpeedMps)*.02),alignmentDegrees=1,lateralM=.25}:null,
            observerMode=a.Definition.Observation,performanceProbe=a.Definition.PerformanceProbe,
            probeDefinition="128-byte every-tick timer/sentinel; all-node world position/velocity/force/mass/cohort and beam L/k/d/strength/active FNV-1a diagnostic fingerprint every 200 ticks; shared probe cost excluded from timer; not an engine checkpoint",
            randomDrawPolicy="Native frand_11 sequence/draw operations preserved; no observer draws",renderer,evidenceFrames,visualCapture=evidenceFrames?"Native renderer screenshots requested every 0.5 render seconds; may be delayed":"Two native screenshots; optional external video",a.Id,a.RevisionId,a.RetryOf,a.Definition,a.DefinitionSha256,a.ExecutableSha256,sourceExecutable=source,
            privateExecutable=exe,requestedEnvironment=e,pressurePa=e.Density*287.05*e.TemperatureK,
            temperatureAdoption="Recorded dry-air state; drag uses explicit density; thermal exchange unimplemented",
            beamLengthKernel=a.Definition.Scenario is "coast-v1" or "barrier-v1"?"native fast inverse-square-root":"fixture precise square-root",
            fixtureGeometry=a.Definition.Scenario is "coast-v1" or "barrier-v1"?null:new {movingMassKg=100,fixedNodes=3,restLengthM=1,extensionM=a.Definition.Scenario=="yield-compression-v1"?-.05:.05,springNpm=a.Definition.Scenario=="freefall-v1"?0:10000,damperNspm=a.Definition.Scenario=="damper-v1"?200:0,drag=false,groundContact=false},
            coverage=a.Coverage,scope=a.Definition.Scenario is "coast-v1" or "barrier-v1"?"Vehicle study: partial model coverage":"Pinned analytical dry fixture; no vehicle/impact generalization",
            units="SI; native world axes Y-up; movable node cohort",retention="manual",
            assetHashes=Directory.GetFiles(Path.Combine(bin,"content"),"*.zip").ToDictionary(f=>Path.GetFileName(f),
                f=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(f))))
        });
        var start=new ProcessStartInfo(exe){WorkingDirectory=bin,UseShellExecute=false,CreateNoWindow=true,RedirectStandardOutput=true,RedirectStandardError=true};
        foreach(string value in new[]{"-map",a.Definition.Terrain,"-truck",a.Definition.Vehicle,"-enter","-runscript","trial-evidence.as"}) start.ArgumentList.Add(value);
        start.Environment["ROR_TRIAL_ARCHIVE"]=dir;
        using var process=Process.Start(start)??throw new IOException("Worker did not start.");
        a.ProcessId=process.Id; a.ProcessPath=exe;
        var stdout=process.StandardOutput.ReadToEndAsync(); var stderr=process.StandardError.ReadToEndAsync();
        lock(gate) { AddEvent(a,"process-started",$"PID {process.Id}; expected SHA256 {a.ExecutableSha256}."); catalog.Save(a); }
        var timer=Stopwatch.StartNew(); double paused=0,lastTime=0; long lastSummaryTick=0,lastAck=0;
        bool handshake=false,modules=false; long savedTick=0;double? releaseWall=null,physicsFinishedWall=null;
        using var summaries=new GrowingLines(Path.Combine(dir,a.Definition.Observation=="off"?"probe-summaries.jsonl":"summaries.jsonl"));
        var impactProjection=new ImpactProjection();
        using var impact=new GrowingLines(Path.Combine(dir,"impact-summaries.jsonl"));
        try
        {
            while(!process.HasExited)
            {
                await Task.Delay(100,stop);
                double current=timer.Elapsed.TotalSeconds;
                if(a.Execution=="Paused") paused+=current-lastTime;
                lastTime=current;
                if(!handshake)
                {
                    var hello=ReadJson(Path.Combine(dir,"handshake.json"));
                    if(hello is { } h)
                    {
                        if(h.GetProperty("schema").GetInt32()!=1 || h.GetProperty("observer").GetString()!="accounting-v2") throw new IOException("Native capability handshake mismatch.");
                        if(h.GetProperty("observation").GetString()!=a.Definition.Observation ||
                            h.GetProperty("performanceProbe").GetBoolean()!=a.Definition.PerformanceProbe)
                            throw new IOException("Native observer/probe mode mismatch.");
                        handshake=true;
                        lock(gate){ a.Execution="Running"; AddEvent(a,"handshake",$"Native {a.Definition.Observation}; declared probe {a.Definition.PerformanceProbe}; archive mode accepted."); catalog.Save(a); }
                    }
                }
                if(handshake&&!modules)
                {
                    process.Refresh();
                    try
                    {
                        var paths=process.Modules.Cast<ProcessModule>().Select(m=>m.FileName).ToArray();
                        string? observed=process.MainModule?.FileName;
                        if(!string.Equals(observed,exe,StringComparison.OrdinalIgnoreCase)) throw new IOException("Worker executable provenance mismatch.");
                        AtomicJson(Path.Combine(dir,"process-provenance.json"),new {pid=process.Id,startTimeUtc=process.StartTime.ToUniversalTime(),expectedExe=exe,observedExe=observed,sha256=a.ExecutableSha256,modules=paths});
                        modules=true;
                    }
                    catch(System.ComponentModel.Win32Exception) {}
                }
                var ack=ReadJson(Path.Combine(dir,"ack.json"));
                if(ack is { } v && v.GetProperty("sequence").GetInt64()>lastAck)
                {
                    lastAck=v.GetProperty("sequence").GetInt64();
                    lock(gate)
                    {
                        if(!v.GetProperty("applied").GetBoolean()) { a.Execution="Running"; AddEvent(a,"command-rejected","Native rejected command."); }
                        else { a.Execution=a.Execution=="Pausing"?"Paused":a.Execution=="Resuming"?"Running":a.Execution; AddEvent(a,"command-applied",$"Sequence {lastAck} at tick {v.GetProperty("appliedTick")}."); }
                        catalog.Save(a);
                    }
                }
                var health=ReadJson(Path.Combine(dir,"worker-status.json"));
                if(health is { } nativeStatus)
                {
                    lock(gate)
                    {
                        a.WorkerStatus=nativeStatus;
                        if(nativeStatus.GetProperty("released").GetBoolean())releaseWall??=current;
                        if(nativeStatus.GetProperty("timeSeconds").GetDouble()>=a.Definition.SettleSeconds+a.Definition.DurationSeconds){physicsFinishedWall??=current;
                            if(a.Execution=="Running"){a.Execution="Finalizing";AddEvent(a,"capture-finalizing","Physics reached target; native archive writers are draining. Quality remains pending.");catalog.Save(a);}}
                        a.DetailProgress=ReadJson(Path.Combine(dir,"detail-progress.json"))??a.DetailProgress;
                        if(nativeStatus.GetProperty("dropped").GetInt64()>0 || nativeStatus.GetProperty("ioError").GetBoolean() ||
                            nativeStatus.TryGetProperty("detailDropped",out var dl)&&dl.GetInt64()>0 || nativeStatus.TryGetProperty("detailIoError",out var di)&&di.GetBoolean()) a.Capture="Incomplete";
                    }
                }
                foreach(var sample in summaries.Read())
                {
                    long tick=sample.GetProperty("tick").GetInt64();
                    if(tick<=lastSummaryTick) continue;
                    lastSummaryTick=tick;
                    lock(gate)
                    {
                        a.Latest=sample;
                        if(tick%100==0) { a.History.Add(sample); if(a.History.Count>2000) a.History.RemoveAt(0); }
                        if(sample.GetProperty("dropped").GetInt64()>0 || (sample.GetProperty("flags").GetInt32()&1)!=0) a.Capture="Incomplete";
                        if(tick-savedTick>=1000) { catalog.Save(a); savedTick=tick; }
                    }
                }
                foreach(var point in impact.Read()){lock(gate){impactProjection.Add(a,point);
                    if(point.GetProperty("detailDropped").GetInt64()>0||point.GetProperty("detailIoError").GetBoolean())a.Capture="Incomplete";}}
                if(!handshake&&current>120 || current-paused>300 || paused>1800)
                    throw new TimeoutException("Worker startup/run/paused lease exceeded; preserve evidence.");
            }
            await process.WaitForExitAsync(stop);
        }
        finally
        {
            if(!process.HasExited)
            {
                AtomicJson(Path.Combine(dir,"command.json"),new {sequence=++a.CommandSequence,operation="cancel"});
                if(!process.WaitForExit(3000)) { process.Kill(true); process.WaitForExit(); }
            }
            File.WriteAllText(Path.Combine(dir,"stdout.log"),await stdout);
            File.WriteAllText(Path.Combine(dir,"stderr.log"),await stderr);
        }
        var finalHealth=ReadJson(Path.Combine(dir,"capture-health.json"));
        var finalStatus=ReadJson(Path.Combine(dir,"worker-status.json"));
        foreach(var sample in summaries.Read())
        {
            lock(gate) a.Latest=sample;
        }
        bool durationMet=finalHealth is { } fh && fh.GetProperty("released").GetBoolean() &&
            fh.GetProperty("timeSeconds").GetDouble()>=a.Definition.SettleSeconds+a.Definition.DurationSeconds;
        bool off=a.Definition.Observation=="off";
        var probe=a.Definition.PerformanceProbe?ProbeReader.Inspect(Path.Combine(dir,"probe.rort")):null;
        var check=off?new ArchiveReader.Check(probe!.Records,probe.Closed,probe.Complete,probe.Dropped,0,0,0,probe.Problem):
            ArchiveReader.Inspect(Path.Combine(dir,"steps.rort"));
        DetailReader.Check? detail=null;
        if(a.Definition.Scenario=="barrier-v1"){
            var health=ReadJson(Path.Combine(dir,"detail-health.json"));
            long trigger=health?.GetProperty("triggerTick").GetInt64()??0,end=health?.GetProperty("requiredEndTick").GetInt64()??0;
            if(trigger==0&&File.Exists(Path.Combine(dir,"impact-events.jsonl")))foreach(string line in File.ReadLines(Path.Combine(dir,"impact-events.jsonl"))){
                try{using var evt=JsonDocument.Parse(line);if(trigger==0)trigger=evt.RootElement.GetProperty("tick").GetInt64();end=evt.RootElement.GetProperty("windowEndTick").GetInt64();}catch(JsonException){}}
            detail=DetailReader.Inspect(Path.Combine(dir,"detail.rort"),trigger,end,Path.Combine(dir,"impact-beam-transitions.jsonl"),Path.Combine(dir,"detail-index.jsonl"));
            if(health is not {} dh||dh.GetProperty("ioError").GetBoolean()||dh.GetProperty("durable").GetInt64()!=detail.Records)a.Capture="Incomplete";
            if(!detail.Complete)a.Capture="Incomplete";
        }
        lock(gate){foreach(var point in impact.Read())impactProjection.Add(a,point);impactProjection.Flush(a);}
        lock(gate)
        {
            a.Execution=a.CancelRequested?"Cancelled":process.ExitCode==0&&handshake&&modules&&durationMet?"Completed":"Failed";
            a.WorkerStatus=finalHealth??finalStatus;
            if(finalHealth is not { } health || health.GetProperty("ioError").GetBoolean() ||
               health.GetProperty("dropped").GetInt64()>0) a.Capture="Incomplete";
            a.Capture=check.Complete&&(probe==null||probe.Complete)&&a.Capture!="Incomplete"?"Complete":"Incomplete";
            var qualification=FixtureValidation.Evaluate(Path.Combine(dir,"steps.rort"),a.Definition,check,a.Execution=="Completed"&&a.Capture=="Complete");
            a.Validation=qualification.Status;
            a.Metrics=new() {["durationMet"]=durationMet,["workerWallSeconds"]=timer.Elapsed.TotalSeconds,["records"]=check.Records,["cleanClose"]=check.Closed,["dropped"]=check.Dropped,
                ["maxMomentumUpdateResidualKgMps"]=check.MaxMomentumResidual,["maxKineticWorkResidualJ"]=check.MaxWorkResidual,
                ["maxKineticJ"]=check.MaxKinetic,["captureProblem"]=check.Problem??"",["workerExitCode"]=process.ExitCode};
            if(physicsFinishedWall is double finished)a.Metrics["observedPhysicsFinishedWallSeconds"]=finished;
            if(releaseWall is double release)a.Metrics["observedReleaseWallSeconds"]=release;
            if(!off)a.Metrics["accounting"]=check.Accounting;
            else {
                a.Metrics.Remove("maxMomentumUpdateResidualKgMps");a.Metrics.Remove("maxKineticWorkResidualJ");a.Metrics.Remove("maxKineticJ");
            }
            if(probe!=null)a.Metrics["performanceProbe"]=probe;
            a.Metrics["qualification"]=qualification;
            if(!off&&check.Complete)a.Metrics["beamTransitions"]=TransitionReader.Read(Path.Combine(dir,"steps.rort"),check,0,20);
            if(detail!=null){a.Metrics["impactDetail"]=detail;a.Metrics["impactQualification"]=ImpactQualification.Evaluate(a.Definition,detail,ReadJson(Path.Combine(dir,"approach.json")),a.Execution=="Completed",a.Capture=="Complete");}

            AddEvent(a,"finished",$"{a.Execution}; capture {a.Capture}; validation {a.Validation} ({qualification.Scope}).");
            catalog.Save(a);
        }
        AtomicJson(Path.Combine(dir,"result.json"),a);
    }
    static void AddEvent(Attempt a,string kind,string message) => a.Events.Add(new(a.Events.Count+1,DateTimeOffset.UtcNow,kind,message));
    static void AtomicJson(string path,object value)
    {
        string temp=path+".tmp";
        File.WriteAllText(temp,JsonSerializer.Serialize(value,Contract.Json));
        File.Move(temp,path,true);
    }
    static JsonElement? ReadJson(string path)
    {
        try { using var document=JsonDocument.Parse(File.ReadAllText(path)); return document.RootElement.Clone(); }
        catch(Exception e) when(e is IOException or JsonException or UnauthorizedAccessException) { return null; }
    }
    static void CopyTree(string source,string target)
    {
        Directory.CreateDirectory(target);
        foreach(string f in Directory.GetFiles(source)) File.Copy(f,Path.Combine(target,Path.GetFileName(f)),false);
        foreach(string d in Directory.GetDirectories(source))
            if(Path.GetFileName(d)!="config") CopyTree(d,Path.Combine(target,Path.GetFileName(d)));
    }
    public string? Artifact(string id,string name)
    {
        var a=Find(id); if(a==null)return null;
        if(new[]{"manifest.json","result.json","steps.rort","summaries.jsonl","capture-health.json","native-events.jsonl","process-provenance.json","beam-transitions.jsonl","probe.rort","probe-health.json","probe-summaries.jsonl","detail.rort","detail-health.json","detail-profile.json","detail-gaps.jsonl","barrier.json","approach.json","impact-events.jsonl","impact-summaries.jsonl","impact-beam-transitions.jsonl","contact-materials.json","detail-index.jsonl","detail-progress.json"}.Contains(name))
            return Path.Combine(a.ArchivePath!,name);
        return null;
    }
    const string OpenGlConfig="Render System=OpenGL Rendering Subsystem\n\n[OpenGL Rendering Subsystem]\nFull Screen=No\nVideo Mode=1280 x 720\nFSAA=0\nVSync=Yes\nRTT Preferred Mode=FBO\n";
    const string RendererConfig="Render System=Direct3D9 Rendering Subsystem\n\n[Direct3D9 Rendering Subsystem]\nAllow NVPerfHUD=No\nFSAA=0\nFloating-point mode=Fastest\nFull Screen=No\nMulti device memory hint=Use minimum system memory\nRendering Device=Monitor-1-NVIDIA GeForce RTX 3090\nResource Creation Policy=Create on all devices\nUse Multihead=Auto\nVSync=Yes\nVSync Interval=1\nVideo Mode=1280 x 720 @ 32-bit colour\nsRGB Gamma Conversion=No\n";
    const string EvidenceScript="""
        float elapsed=0;
        bool initialized=false,open=true,s1=false,s2=false;
        void main(){game.log("TRIAL observer accounting-v2; source-built physics");}
        void frameStep(float dt) {
            BeamClass@ truck=game.getCurrentTruck();
            if(truck is null)return;
            if(!initialized) {
                EngineClass@ engine=truck.getEngine();
                if(engine !is null){engine.stopEngine();engine.setGear(0);}
                if(truck.getParkingBrake())truck.parkingbrakeToggle();
                initialized=true;
            }
            truck.setEventSimulatedValue(EV_TRUCK_ACCELERATE,0);
            truck.setEventSimulatedValue(EV_TRUCK_BRAKE,0);
            elapsed+=dt;
            ImGui::SetNextWindowPos(vector2(20,20),ImGuiCond_Always);
            ImGui::SetNextWindowSize(vector2(470,130));
            if(ImGui::Begin("RoR Trials / source-built worker",open,ImGuiWindowFlags_NoResize)){
                ImGui::Text("Native force channels / core energy accounting");
                ImGui::Text("Pinned scenario | Simple2 | fresh native process");
                ImGui::Text("Wheel speed: "+truck.getWheelSpeed()+" m/s");
                ImGui::Text("Fixture qualification is evaluated after capture closes");
                ImGui::End();
            }
            if(!s1&&elapsed>4){s1=true;game.pushMessage(MSG_APP_SCREENSHOT_REQUESTED,null);}
            if(!s2&&elapsed>9){s2=true;game.pushMessage(MSG_APP_SCREENSHOT_REQUESTED,null);}
        }
        """;
}
sealed class GrowingLines(string path) : IDisposable
{
    FileStream? stream;
    string pending="";
    public List<JsonElement> Read()
    {
        List<JsonElement> values=[];
        if(stream==null) { if(!File.Exists(path))return values; stream=new(path,FileMode.Open,FileAccess.Read,FileShare.ReadWrite); }
        byte[] buffer=new byte[8192];
        while(true)
        {
            int count=stream.Read(buffer,0,buffer.Length); if(count==0)break;
            pending+=System.Text.Encoding.UTF8.GetString(buffer,0,count);
            int newline;
            while((newline=pending.IndexOf('\n'))>=0)
            {
                string line=pending[..newline]; pending=pending[(newline+1)..];
                try { using var doc=JsonDocument.Parse(line); values.Add(doc.RootElement.Clone()); }
                catch(JsonException) { /* Binary archive health is authoritative, corrupt projection is omitted. */ }
            }
        }
        return values;
    }
    public void Dispose()=>stream?.Dispose();
}
