
"""Encode actual native renderer screenshots; do not use GDI pixels for OpenGL proof."""
import argparse,json,shutil,subprocess,statistics
from pathlib import Path
from PIL import Image,ImageStat
ap=argparse.ArgumentParser();ap.add_argument('--attempt',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
archive=Path(a.attempt).resolve();dest=Path(a.output).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
manifest=json.loads((archive/'manifest.json').read_text(encoding='utf-8'))
assert manifest.get('evidenceFrames'),'Enable -EvidenceFrames when starting the coordinator'
files=sorted((archive/'worker/config/screenshots').glob('*.png'));assert len(files)>=8,'Insufficient native renderer frames'
target=dest.parent/'native-renderer-frames';target.mkdir(exist_ok=True)
names=[]
for i,src in enumerate(files):
 with Image.open(src) as im:
  stats=ImageStat.Stat(im.convert('RGB'));assert statistics.mean(stats.mean)>10 and statistics.mean(stats.var)>50,src
 name='native-frame-'+str(i+1).zfill(4)+'.png';shutil.copy2(src,target/name);names.append({'index':i,'source':str(src),'copy':name})
with (dest.parent/'native-renderer-video.log').open('wb') as log:
 subprocess.run([r'C:\Users\berts\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe','-hide_banner','-y','-framerate','2','-i',str(target/'native-frame-%04d.png'),
   '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],stdout=log,stderr=log,check=True)
(dest.parent/'native-renderer-frame-manifest.json').write_text(json.dumps({'attempt':str(archive),'nativeExecutableSha256':manifest['executableSha256'],
 'capture':'RoR native render-window screenshot requests, 0.5 render seconds apart; screenshots can be delayed; no desktop capture',
 'encoding':'FFmpeg PNG sequence at nominal 2 fps; does not provide a physics measurement clock','frames':names},indent=2),encoding='utf-8')
print(json.dumps({'video':str(dest),'nativeFrames':len(files)}))
