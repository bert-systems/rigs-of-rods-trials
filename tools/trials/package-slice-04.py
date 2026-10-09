"""Portable metadata/media evidence with one full raw window; preserve all original archives."""
import argparse,json,hashlib,zipfile,shutil,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--session',required=True);p.add_argument('--repo',required=True);a=p.parse_args();root=Path(a.session).resolve();repo=Path(a.repo).resolve();report=root/'report'
def digest(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest().upper()
canonical=json.loads((report/'canonical-visual.json').read_text(encoding='utf-8-sig'));id=canonical['id']
inventory=[]
for path in sorted((root/'archive').glob('*/*.rort')):
 inventory.append(dict(path=str(path.relative_to(root)).replace('\\','/'),bytes=path.stat().st_size,sha256=digest(path)))
 print('HASH '+str(path.relative_to(root)),flush=True)
(report/'raw-archive-inventory.json').write_text(json.dumps(dict(retention='All originals retained; bundle contains one representative raw window plus analytical fixture raw records',files=inventory),indent=2),encoding='utf-8')
dest=report/'portable-slice-04';dest.mkdir(exist_ok=False)
selected={}
for folder in ['logs','media']:
 for src in (root/folder).rglob('*'):
  if src.is_file():selected[src]=src.relative_to(root)
for src in report.rglob('*'):
 if src.is_file() and not any(x in src.parts for x in ['portable-slice-04','bundle-extracted']) and src.suffix!='.zip' and src.name not in ['bundle-check.json']:
  selected[src]=src.relative_to(root)
for attempt in (root/'archive').iterdir():
 if not attempt.is_dir():continue
 for src in attempt.iterdir():
  if src.is_file() and src.suffix in ['.json','.jsonl','.log','.txt','.as']:
   selected[src]=src.relative_to(root)
 # Preserve logs without copying each private runtime, DLLs or repeated content ZIPs.
 for src in (attempt/'worker/config/logs').glob('*'):
  if src.is_file():selected[src]=src.relative_to(root)
 result=attempt/'result.json'
 if result.exists():
  value=json.loads(result.read_text(encoding='utf-8-sig'))
  if attempt.name==id or value['definition']['scenario'] in ['freefall-v1','spring-v1','damper-v1']:
   for src in attempt.glob('*.rort'):selected[src]=src.relative_to(root)
for relative in ['PROJECT.md','AGENTS.md','architecture.md','todo.md','project-memory.md','apps/trials/README.md','apps/trials/detail-format.md','doc/project/slices/slice-04.md','doc/project/slices/slice-04-results.json']:
 src=repo/relative;selected[src]=Path('repository-docs')/relative
for src,relative in selected.items():
 target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
 if target.suffix=='.html':
  text=target.read_text(encoding='utf-8');prefix=root.as_uri()+'/'
  # Relative references make the extracted report/media independent of the source machine.
  import re,urllib.parse
  def relative_session(m):
   part=urllib.parse.unquote(m[2][len(prefix):])
   # Container hash/download references remain adjacent to the extracted bundle, never recursive.
   external=part in ['report/slice-04-evidence.zip','report/bundle-check.json']
   target_path=(root if external else dest)/part
   return m[1]+'="'+os.path.relpath(target_path,target.parent).replace('\\','/')+'"'
  text=re.sub(r'(href|src)="('+re.escape(prefix)+r'[^"]+)"',relative_session,text)
  repo_prefix=repo.as_uri()+'/'
  text=re.sub(r'(href|src)="('+re.escape(repo_prefix)+r'[^"]+)"',lambda m:m[1]+'="'+os.path.relpath(dest/'repository-docs'/urllib.parse.unquote(m[2][len(repo_prefix):]),target.parent).replace('\\','/')+'"',text)
  target.write_text(text,encoding='utf-8')
files={str(x.relative_to(dest)).replace('\\','/'):dict(bytes=x.stat().st_size,sha256=digest(x)) for x in dest.rglob('*') if x.is_file()}
(dest/'bundle-manifest.json').write_text(json.dumps(dict(files=files,representativeRawAttempt=id),indent=2),encoding='utf-8')
zip_path=report/'slice-04-evidence.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for path in dest.rglob('*'):
  if path.is_file():z.write(path,path.relative_to(dest))
extract=report/'bundle-extracted';extract.mkdir(exist_ok=False)
with zipfile.ZipFile(zip_path) as z:
 for item in z.infolist():
  target=(extract/item.filename).resolve();assert target.is_relative_to(extract.resolve()),item.filename
 z.extractall(extract)
assert all(digest(extract/key)==v['sha256'] and (extract/key).stat().st_size==v['bytes'] for key,v in files.items())
result=dict(zip=str(zip_path),bytes=zip_path.stat().st_size,sha256=digest(zip_path),files=len(files),allExtractedHashesMatch=True,pathTraversalCheck=True,rawWindowsInBundle=1,representativeRawAttempt=id,extractedReport=str(extract/'report/index.html'))
(report/'bundle-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)
