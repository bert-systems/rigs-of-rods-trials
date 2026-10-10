"""Freeze Slice07 source, every small native raw stream and portable review media."""
import argparse, hashlib, html, json, os, shutil, time, zipfile
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--repo',required=True);a=p.parse_args()
root=Path(a.session).resolve();repo=Path(a.repo).resolve();report=root/'report'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
stage=report/('review-stage-'+time.strftime('%Y%m%d-%H%M%S'));stage.mkdir()
zpath=report/'slice-07-review.zip';assert not zpath.exists()
mapping={}
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);mapping[src.resolve().as_uri()]=dst
def tree(src,dst,skip=()):
 for f in src.rglob('*'):
  if f.is_file() and not any(part in skip for part in f.relative_to(src).parts):copy(f,dst/f.relative_to(src))
tree(report/'media',stage/'report/media');tree(root/'logs',stage/'logs')
for f in report.rglob('*'):
 if not f.is_file():continue
 parts=f.relative_to(report).parts
 if parts[0]=='media' or parts[0].startswith('review-') or parts[0]=='slice-07-review.zip':continue
 if f.suffix in ['.json','.txt','.patch','.log','.png']:copy(f,stage/'records'/f.relative_to(report))
build=read(sorted(report.glob('build-*.json'))[-1]);inventory=read(report/build['sourceRecord'])
assert sha(root/'build/bin/RoR.exe').upper()==build['sha256']
for name,expected in inventory['nativeSourceHashes'].items():
 src=repo/name;assert sha(src).upper()==expected;copy(src,stage/'source'/name)
for folder in ['apps/trials','tests/trials','tools/trials','doc/project']:
 tree(repo/folder,stage/'source'/folder,skip=('node_modules','bin','obj','dist','__pycache__'))
for src in repo.glob('*.md'):copy(src,stage/'source'/src.name)
for name in ['conanfile.py','COPYING','CMakeLists.txt']:copy(repo/name,stage/'source'/name)
copy(root/'build/bin/RoR.exe',stage/'binaries/RoR-source-build.exe')
tree(repo/'apps/trials/coordinator/bin/Release/net10.0',stage/'binaries/coordinator')
tree(repo/'apps/trials/workbench/dist',stage/'binaries/workbench')
raw=[];attempts=[]
for attempt in sorted((root/'archive').iterdir()):
 if not attempt.is_dir() or not (attempt/'manifest.json').exists():continue
 result=read(attempt/'result.json');assert result['executableSha256']==build['sha256']
 attempts.append(dict(id=attempt.name,path=str(attempt),execution=result['execution'],capture=result['capture'],nativeSha256=result['executableSha256']))
 for src in attempt.iterdir():
  if src.is_file():
   raw.append(dict(attempt=attempt.name,path=str(src),bytes=src.stat().st_size,sha256=sha(src),included=True))
   copy(src,stage/'attempts'/attempt.name/src.name)
 logs=attempt/'worker/config/logs'
 if logs.exists():tree(logs,stage/'attempts'/attempt.name/'native-logs')
assert len(attempts)==20
adversaries=[]
for test in root.glob('contract-*'):
 for f in test.rglob('*'):
  if not f.is_file():continue
  adversaries.append(dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f),included=f.suffix in ['.json','.txt','.log']))
  if f.suffix in ['.json','.txt','.log']:copy(f,stage/'test-records'/f.relative_to(root))
(stage/'records/archive-inventory.json').write_text(json.dumps(dict(attempts=attempts,files=raw,originalsRetained=True,adversarialArtifacts=adversaries),indent=2),encoding='utf-8')
page=(repo/'doc/project/reports/trial-slice-07-2026-10-10.html').read_text(encoding='utf-8')
for uri,dst in sorted(mapping.items(),key=lambda item:len(item[0]),reverse=True):
 page=page.replace(html.escape(uri,quote=True),html.escape(os.path.relpath(dst,stage/'report').replace('\\','/'),quote=True))
page=page.replace('<a href="'+html.escape(zpath.as_uri(),quote=True)+'">Portable review bundle</a>','<a href="../SHA256SUMS.json">Review bundle hashes</a>')
(stage/'report/index.html').write_text(page,encoding='utf-8')
hashes=[dict(path=f.relative_to(stage).as_posix(),bytes=f.stat().st_size,sha256=sha(f)) for f in stage.rglob('*') if f.is_file()]
(stage/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
with zipfile.ZipFile(zpath,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for f in stage.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(stage).as_posix())
extract=report/'review-extracted';extract.mkdir()
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 for info in z.infolist():assert (extract/info.filename).resolve().is_relative_to(extract.resolve()),info.filename
 z.extractall(extract)
for h in hashes:assert sha(extract/h['path'])==h['sha256'],h['path']
summary=dict(zip=str(zpath),bytes=zpath.stat().st_size,sha256=sha(zpath),filesVerified=len(hashes),attemptsInventoried=len(attempts),denseStreamsIncluded=True,originalsRetained=True,excluded='Native dependency DLLs, private worker/runtime trees, compiler/cache outputs; native exe is an identity artifact, not a standalone distribution',extractedReport=str(extract/'report/index.html'))
(report/'review-bundle.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary),flush=True)
