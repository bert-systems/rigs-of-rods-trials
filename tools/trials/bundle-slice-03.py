"""Build a portable Slice 03 evidence bundle without copying runtime assets."""
import argparse,json,hashlib,zipfile,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);a=p.parse_args();root=Path(a.session).resolve()
files=set()
for directory in [root/'report',root/'media',root/'logs']:
 for f in directory.rglob('*'):
  if f.is_file() and f.suffix.lower() in ['.html','.png','.jpg','.mp4','.webm','.json','.jsonl','.log','.patch'] and f.name not in ['sha256-manifest.json','bundle-check.json'] and 'bundle-extracted' not in f.parts:
   files.add(f)
for f in root.glob('*transcript.log'):files.add(f)
for f in (root/'archive').glob('*/*'):
 if f.is_file() and f.suffix.lower() in ['.json','.jsonl','.rort','.log']:files.add(f)
hashes={f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(files)}
manifest=root/'report/sha256-manifest.json';manifest.write_text(json.dumps(hashes,indent=2),encoding='utf-8')
files.add(manifest);target=root/'report/slice-03-evidence.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(files):z.write(f,f.relative_to(root).as_posix())
extracted=root/'bundle-extracted';extracted.mkdir(exist_ok=True)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 # All names are generated from paths within this session; reject traversal.
 for name in z.namelist():
  dest=(extracted/name).resolve();assert dest.is_relative_to(extracted.resolve())
 z.extractall(extracted)
for name,digest in hashes.items():assert hashlib.sha256((extracted/name).read_bytes()).hexdigest()==digest,name
check=dict(files=len(files),allHashesMatch=True,zip=str(target),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),extracted=str(extracted))
(root/'report/bundle-check.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
print(json.dumps(check))
