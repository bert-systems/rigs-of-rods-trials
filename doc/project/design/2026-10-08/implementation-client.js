(() => {
 const states={
  complete:{execution:'Completed',capture:'Complete',validation:'Pending automated checks',queue:'Continue eligible independent trials',note:'Complete capture permits validation to run. It does not establish physical accuracy or guarantee a pass.'},
  gap:{execution:'Running; may complete normally',capture:'Incomplete — required gap retained',validation:'Cannot pass',queue:'Continue eligible independent trials after finish',note:'Keep observing and retain later samples. Gap intervals remain explicit; the archive cannot silently reconstruct missing measurements.'},
  crash:{execution:'Failed — process exit',capture:'Partial / tail uncertainty assessed',validation:'No completed-trial pass',queue:'Continue eligible trials; manual retry is a new attempt',note:'Recover verified committed prefixes and preserve diagnostics. Physical checkpoint restoration is outside the first release.'},
  pause:{execution:'Paused — acknowledged boundary',capture:'Quality retained; no advancing physics ticks',validation:'Pending completion and checks',queue:'Active attempt retains its slot',note:'Resume uses the same live process and records the boundary. The final idle/lease contract remains engineering work.'},
  storage:{execution:'Queued — preflight blocked',capture:'No attempt launched',validation:'Not evaluated',queue:'Hold new launches',note:'Shared storage insufficiency blocks new launches. Existing archives remain until explicit manual archive/cleanup; active loss still follows the continuation policy.'},
  failedcheck:{execution:'Completed',capture:'Complete',validation:'Failed scoped check',queue:'Continue eligible independent trials',note:'Retain measured values, thresholds and evidence. Manual retry creates a new attempt rather than editing the failed result.'},
  disconnect:{execution:'Running under coordinator ownership',capture:'Native archive determines quality',validation:'Pending automated checks',queue:'Coordinator continues eligible queue',note:'The browser shows last-known time and resynchronizes. A slow or disconnected view does not block native physics or repeat a physical command.'}
 };
 const choice=document.getElementById('policy-case');
 function update(){
  const state=states[choice.value];
  for(const key of ['execution','capture','validation','queue'])document.getElementById('policy-'+key).textContent=state[key];
  document.getElementById('policy-note').textContent=state.note;
 }
 choice.addEventListener('change',update);update();
})();
