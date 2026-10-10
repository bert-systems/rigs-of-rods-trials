"""Portable review evidence, frozen inputs and inventories; dense originals retained."""
import argparse,json,hashlib,shutil,zipfile,time,html,os
from pathlib import Path
from html.parser import HTMLParser
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--repo',required=True);a=p.parse_args()
root=Path(a.session).resolve();repo=Path(a.repo).resolve();report=root/'report'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
stage=report/('review-stage-'+time.strftime('%Y%m%d-%H%M%S'));stage.mkdir();zpath=report/'slice-06-review.zip';assert not zpath.exists()
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
inputs=read(report/'report-inputs.json');htmlPath=Path(inputs['html']);mapping={}
shutil.copytree(report/'media',stage/'report/media')
for file in (report/'media').rglob('*'):
 if file.is_file():mapping[file.resolve().as_uri()]=(stage/'report/media'/file.relative_to(report/'media'))
shutil.copytree(root/'logs',stage/'logs')
for file in (root/'logs').rglob('*'):
 if file.is_file():mapping[file.resolve().as_uri()]=stage/'logs'/file.relative_to(root/'logs')
for file in report.rglob('*'):
 if not file.is_file() or stage in file.parents or report/'media' in file.parents:continue
 if file.relative_to(report).parts[0].startswith('review-stage') or file.relative_to(report).parts[0]=='review-extracted':continue
 if file.suffix not in ['.json','.txt','.patch','.log']:continue
 dst=stage/'records'/file.relative_to(report);copy(file,dst);mapping[file.resolve().as_uri()]=dst
source=read(Path(inputs['finalBuild']));inventory=read(report/source['sourceRecord'])
for name,expected in inventory['nativeSourceHashes'].items():
 src=repo/name;assert sha(src).upper()==expected;copy(src,stage/'source'/name)
for folder in ['apps/trials/coordinator','apps/trials/workbench','tests/trials','tools/trials','doc/project']:
 for src in (repo/folder).rglob('*'):
  if not src.is_file() or any(part in ['node_modules','bin','obj','dist'] for part in src.relative_to(repo/folder).parts):continue
  copy(src,stage/'source'/src.relative_to(repo))
for src in repo.glob('*.md'):copy(src,stage/'source'/src.name)
for name in ['conanfile.py','COPYING','CMakeLists.txt']:copy(repo/name,stage/'source'/name)
copy(root/'build/bin/RoR.exe',stage/'binaries/RoR-final.exe');copy(report/'RoR-before.exe',stage/'binaries/RoR-before.exe')
for src in (repo/'apps/trials/coordinator/bin/Release/net10.0').iterdir():
 if src.is_file():copy(src,stage/'binaries/coordinator'/src.name)
shutil.copytree(repo/'apps/trials/workbench/dist',stage/'binaries/workbench')
archiveRoots=[root/'archive',Path(r'C:\Users\berts\Documents\RoR-trials-evidence\trial-slice-06-2026-10-09-230333'),Path(r'C:\Users\berts\Documents\RoR-trials-evidence\trial-slice-06-2026-10-09-230333-visual')]
raw=[];attempts=[]
for archive in archiveRoots:
 for attempt in archive.iterdir():
  if not attempt.is_dir() or not (attempt/'manifest.json').exists():continue
  result=read(attempt/'result.json');attempts.append(dict(id=attempt.name,path=str(attempt),execution=result['execution'],capture=result['capture'],nativeSha256=result['executableSha256']))
  for src in attempt.iterdir():
   if not src.is_file() or src.suffix not in ['.json','.jsonl','.rort','.log']:continue
   raw.append(dict(attempt=attempt.name,path=str(src),bytes=src.stat().st_size,sha256=sha(src),included=src.name!='detail.rort'))
   if src.name!='detail.rort':copy(src,stage/'attempts'/attempt.name/src.name)
  logs=attempt/'worker/config/logs'
  if logs.exists():shutil.copytree(logs,stage/'attempts'/attempt.name/'native-logs')
(stage/'records/archive-inventory.json').write_text(json.dumps(dict(roots=[str(r) for r in archiveRoots],attempts=attempts,files=raw,denseOriginalsRetained=True),indent=2),encoding='utf-8')
page=htmlPath.read_text(encoding='utf-8')
for uri,dst in sorted(mapping.items(),key=lambda item:len(item[0]),reverse=True):
 page=page.replace(html.escape(uri,quote=True),html.escape(os.path.relpath(dst,stage/'report').replace('\\','/'),quote=True))
page=page.replace('<a href="'+html.escape(zpath.as_uri(),quote=True)+'">Portable review bundle</a>',
    '<a href="../SHA256SUMS.json">Review bundle hashes</a>')
(stage/'report/index.html').write_text(page,encoding='utf-8')
hashes=[dict(path=f.relative_to(stage).as_posix(),bytes=f.stat().st_size,sha256=sha(f)) for f in stage.rglob('*') if f.is_file()]
(stage/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
with zipfile.ZipFile(zpath,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for f in stage.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(stage).as_posix())
extract=report/'review-extracted';extract.mkdir()
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 for info in z.infolist():
  target=(extract/info.filename).resolve();assert target.is_relative_to(extract.resolve()),info.filename
 z.extractall(extract)
for h in hashes:assert sha(extract/h['path'])==h['sha256'],h['path']
summary=dict(zip=str(zpath),bytes=zpath.stat().st_size,sha256=sha(zpath),filesVerified=len(hashes),attemptsInventoried=len(attempts),denseOriginalsRetained=True,extractedReport=str(extract/'report/index.html'))
(report/'review-bundle.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary),flush=True)
