"""Portable evidence package; preserve originals and verify every extracted file hash."""
import argparse,hashlib,json,shutil,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--repo',required=True);a=p.parse_args()
root=Path(a.session).resolve();repo=Path(a.repo).resolve();report=root/'report';stage=report/'portable-slice-05';stage.mkdir()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest().upper()
def copy(src,dest):dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
copy(report/'index.html',stage/'report/index.html')
for f in (report/'media').rglob('*'):
 if f.is_file():copy(f,stage/'report/media'/f.relative_to(report/'media'))
for f in report.iterdir():
 if f.is_file() and f.suffix in ['.json','.patch']:copy(f,stage/'report'/f.name)
for pattern in ['verification-05-*','ui-05-*']:
 for directory in report.glob(pattern):
  for f in directory.glob('*.json'):copy(f,stage/'report'/directory.name/f.name)
for f in (root/'logs').glob('*'):
 if f.is_file():copy(f,stage/'logs'/f.name)
copy(root/'contract-final/native-reinspection.json',stage/'contract-final/native-reinspection.json')
inventory=[]
for directory in (root/'archive').iterdir():
 if not directory.is_dir():continue
 for f in directory.iterdir():
  if f.is_file():
   copy(f,stage/'archive'/directory.name/f.name)
   inventory.append(dict(path=str(f.relative_to(root)),bytes=f.stat().st_size,sha256=sha(f)))
 copy(directory/'worker/content/trial-fixtures.zip',stage/'archive'/directory.name/'trial-fixtures.zip')
source=json.loads(next(report.glob('source-*.json')).read_text(encoding='utf-8-sig'))
for name in source['nativeSourceHashes']:
 f=repo/name;assert sha(f)==source['nativeSourceHashes'][name],name;copy(f,stage/'frozen-source'/name)
for folder in ['apps/trials','tests/trials','tools/trials']:
 for f in (repo/folder).rglob('*'):
  if f.is_file() and not set(f.relative_to(repo).parts)&{'node_modules','bin','obj','dist','__pycache__'} and f.suffix in {'.cs','.csproj','.json','.jsx','.css','.html','.md','.py','.ps1','.cpp','.txt'}:
   copy(f,stage/'frozen-source'/f.relative_to(repo))
for name in ['AGENTS.md','PROJECT.md','architecture.md','project-memory.md','todo.md']:copy(repo/name,stage/'frozen-source'/name)
copy(root/'build/bin/RoR.exe',stage/'build-proof/RoR.exe')
(stage/'report/raw-file-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
(report/'raw-file-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
doc=(stage/'report/index.html').read_text(encoding='utf-8')
doc=doc.replace((report/'media').as_uri(),'media').replace(report.as_uri(),'..PLACEHOLDER')
doc=doc.replace(root.as_uri(),'..').replace('..PLACEHOLDER','.')
(stage/'report/index.html').write_text(doc,encoding='utf-8')
files=sorted(f for f in stage.rglob('*') if f.is_file());manifest=[dict(path=f.relative_to(stage).as_posix(),bytes=f.stat().st_size,sha256=sha(f)) for f in files]
(stage/'bundle-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
zip_path=report/'slice-05-evidence.zip'
with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in stage.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(stage).as_posix())
extracted=report/'bundle-extracted';extracted.mkdir()
with zipfile.ZipFile(zip_path) as z:
 for item in z.infolist():
  target=(extracted/item.filename).resolve();assert target.is_relative_to(extracted.resolve()),item.filename
 z.extractall(extracted)
for item in manifest:
 f=extracted/item['path'];assert f.stat().st_size==item['bytes'] and sha(f)==item['sha256'],item['path']
assert sha(stage/'bundle-manifest.json')==sha(extracted/'bundle-manifest.json')
result=dict(zip=str(zip_path),bytes=zip_path.stat().st_size,sha256=sha(zip_path),verifiedFiles=len(manifest)+1,
 rawFiles=len(inventory),rawBytes=sum(i['bytes'] for i in inventory),extractedReport=str(extracted/'report/index.html'),allExtractedHashesMatch=True,originalsRetained=True)
(report/'package.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
