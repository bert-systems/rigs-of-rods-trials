
"""Package real captured video with WebM and a codec-independent image player.
Preserves source videos. Requires ffmpeg and Pillow; outputs outside Git."""
import argparse,json,subprocess,html,statistics,shutil
from pathlib import Path
from PIL import Image,ImageStat,ImageChops
ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--output',required=True);ap.add_argument('--title',default='Native simulation evidence');a=ap.parse_args()
src=Path(a.input).resolve();dest=Path(a.output).resolve();dest.mkdir(parents=True,exist_ok=True)
if src!=dest/'original.mp4':shutil.copy2(src,dest/'original.mp4')
ff=r'C:\Users\berts\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe'
def run(args,log):
 with (dest/log).open('wb') as out:subprocess.run([ff,'-hide_banner','-y',*args],stdout=out,stderr=out,check=True)
run(['-i',str(src),'-an','-vf','scale=960:-2','-c:v','libvpx-vp9','-threads','4','-row-mt','1','-crf','32','-b:v','0','-pix_fmt','yuv420p',str(dest/'simulation.webm')],'transcode.log')
frames=dest/'frames';frames.mkdir(exist_ok=True)
run(['-i',str(src),'-vf','fps=4,scale=960:-2','-q:v','3',str(frames/'frame-%04d.jpg')],'frames.log')
files=sorted(frames.glob('frame-*.jpg'));metrics=[];previous=None
for f in files:
 with Image.open(f) as im:
  im=im.convert('RGB').resize((160,90));stat=ImageStat.Stat(im)
  diff=statistics.mean(ImageStat.Stat(ImageChops.difference(im,previous)).mean) if previous else None
  metrics.append({'frame':f.name,'timeSeconds':(len(metrics)+.5)/4,'mean':statistics.mean(stat.mean),'variance':statistics.mean(stat.var),'previousPixelDifference':diff})
  previous=im.copy()
assert len(files)>2 and all(m['mean']>10 and m['variance']>50 for m in metrics),'Blank or uninspectable frame sequence'
assert any((m['previousPixelDifference'] or 0)>.01 for m in metrics),'Sequence shows no changing pixels'
data={'source':str(src),'sourcePreserved':True,'fps':4,'sampleTime':'4 Hz fps filter, first image at nominal 0.125 s; timestamp +/-0.125 s','frames':metrics}
(dest/'media-check.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
title=html.escape(a.title)
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>'''+title+'''</title><style>body{background:#0b1620;color:#dce7ed;max-width:1100px;margin:35px auto;padding:0 22px;font:16px system-ui}h1{font-size:30px}p{color:#acbdc8;line-height:1.5}img,video{width:100%;background:#14232e;border:1px solid #324654;border-radius:10px}button{padding:10px 20px;background:#2a6c76;color:white;border:0;border-radius:5px;cursor:pointer}input{width:65%;margin:15px}output{font-variant-numeric:tabular-nums}.controls{display:flex;align-items:center;gap:10px}a{color:#6bd2c9}details{margin:22px 0}</style>
<h1>'''+title+'''</h1><p>This image player shows decoded frames from the real native recording. It uses ordinary images and continues to work when embedded video playback shows a blank screen. Resolution 960 px; four frames per second. It is visual evidence, not a telemetry measurement clock.</p>
<img id="sequence" src="frames/frame-0001.jpg" alt="Decoded native simulation frame">
<div class="controls"><button id="play">Play frames</button><input id="seek" type="range" min="0" max="'''+str(len(files)-1)+'''" value="0" step="1" aria-label="Recorded frame"><output id="stamp">0.125 s</output></div>
<details><summary>Standard video playback · WebM with original MP4 link</summary><p>If video is blank, use the image player above.</p>
<video controls playsinline preload="metadata" poster="frames/frame-0001.jpg"><source src="simulation.webm" type="video/webm"></video><p><a href="'''+'original.mp4'+'''">Open the preserved original MP4</a></p></details>
<p><a href="media-check.json">Decoded frame diagnostics</a> · <a href="transcode.log">Transcode log</a></p>
<script>
const image=document.getElementById('sequence'),slider=document.getElementById('seek'),stamp=document.getElementById('stamp'),play=document.getElementById('play');
let index=0,timer=null;const count='''+str(len(files))+''';
function show(n){index=n;slider.value=n;image.src='frames/frame-'+String(n+1).padStart(4,'0')+'.jpg';stamp.textContent=((n+.5)/4).toFixed(3)+' s';}
function stop(){clearInterval(timer);timer=null;play.textContent='Play frames';}
slider.oninput=()=>{stop();show(Number(slider.value));};
play.onclick=()=>{if(timer){stop();return;}play.textContent='Pause frames';timer=setInterval(()=>{show((index+1)%count);},250);};
</script></html>'''
(dest/'playback.html').write_text(page,encoding='utf-8')
print(json.dumps({'output':str(dest),'frames':len(files),'blankFrames':0,'minMean':min(m['mean'] for m in metrics)}))
