import ast,datetime,hashlib,json,re,shutil,subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit

root=Path(r'D:\Rigs of Rods\rigs-of-rods-trials')
records=root/'doc/project/design/2026-10-08'
output=records/'implementation-documentation-validation.json'
if not output.exists():output.write_text('{}\n',encoding='utf-8')
def run(args):
 r=subprocess.run(args,cwd=root,text=True,encoding='utf-8',errors='replace',capture_output=True)
 return {'exitCode':r.returncode,'output':r.stdout.strip(),'errors':r.stderr.strip()}
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
docs=[root/x for x in ['README.md','AGENTS.md','PROJECT.md','architecture.md','todo.md','project-memory.md','platform.md']]
docs+=sorted((root/'doc/project').rglob('*.md'))
problems=[];links=[];white=[];preserved_whitespace=[]
baseline_readme=run(['git','show','HEAD:README.md'])['output'].splitlines()
for doc in docs:
 text=doc.read_text(encoding='utf-8-sig')
 for line_no,line in enumerate(text.splitlines(),1):
  if line.rstrip()!=line:
   item={'file':str(doc.relative_to(root)),'line':line_no}
   if doc==root/'README.md' and line in baseline_readme:preserved_whitespace.append(item)
   else:white.append(item)
 for href in re.findall(r'(?<!!)\[[^\]\n]+\]\(([^)]+)\)',text):
  href=href.strip().strip('<>')
  if urlsplit(href).scheme:continue
  parts=href.split('#',1)
  target=(doc.parent/unquote(parts[0])).resolve() if parts[0] else doc
  exists=target.exists();valid=None
  if exists and len(parts)>1 and parts[1]:
   fragment=unquote(parts[1])
   if target.suffix=='.html':
    valid=bool(re.search(r'\bid=["\']'+re.escape(fragment)+r'["\']',target.read_text(encoding='utf-8')))
   elif re.fullmatch(r'L\d+(?:-L?\d+)?',fragment) and target.is_file():
    nums=[int(n) for n in re.findall(r'\d+',fragment)]
    valid=1<=min(nums)<=max(nums)<=len(target.read_text(encoding='utf-8-sig').splitlines())
  links.append({'document':str(doc.relative_to(root)),'href':href,'exists':exists,'anchorValid':valid})
  if not exists or valid is False:problems.append('Invalid local target: '+str(doc.relative_to(root))+' '+href)
if white:problems.append('Markdown trailing whitespace')
syntax=[]
for name in ('verify-implementation.py','verify-implementation-docs.py'):
 try:ast.parse((records/name).read_text(encoding='utf-8'));syntax.append({'file':name,'valid':True})
 except SyntaxError as e:syntax.append({'file':name,'valid':False,'error':str(e)});problems.append(name+' syntax')
node=r'C:\Users\berts\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
for name in ('render-implementation.mjs','implementation-client.js'):
 check=run([node,'--check',str(records/name)])
 syntax.append({'file':name,'valid':check['exitCode']==0,'errors':check['errors']})
 if check['exitCode']:problems.append(name+' syntax')
for name in ('implementation-review.md',):
 text=(records/name).read_text(encoding='utf-8')
 if 'report-validation.json' not in text:problems.append('Missing QA record link')
protected=[]
baseline=root.parent/'source-build-2026-10-08'
for name in ('provenance.json','verification.json','report-validation.json','conan.lock','build-proof.as'):
 copy=root/'doc/project/baselines/2026-10-08'/name
 original=baseline/('scripts' if name.endswith('.as') else 'report')/name
 a=digest(copy);b=digest(original)
 protected.append({'file':str(copy.relative_to(root)),'original':str(original),'sha256':a,'matchesOriginal':a==b})
 if a!=b:problems.append('Historical baseline copy changed: '+name)
verify=json.loads((root/'doc/project/baselines/2026-10-08/verification.json').read_text())
exe=Path(verify['sourceExecutable']);actual=digest(exe)
protected.append({'file':str(exe),'sha256':actual,'recordedSha256':verify['sha256'],'matchesOriginal':actual.lower()==verify['sha256'].lower()})
if actual.lower()!=verify['sha256'].lower():problems.append('Baseline executable changed')
for rel,record in [
 ('doc/project/reports/platform-evaluation-2026-10-08.html','doc/project/research/2026-10-08/report-validation.json'),
 ('doc/project/reports/trial-architecture-options-2026-10-08.html','doc/project/design/2026-10-08/report-validation.json')]:
 observed=digest(root/rel);expected=json.loads((root/record).read_text())['reportSha256']
 protected.append({'file':rel,'sha256':observed,'recordedSha256':expected,'matchesOriginal':observed==expected})
 if observed!=expected:problems.append('Historical evaluation report changed: '+rel)
identity={k:run(args) for k,args in {
 'branch':['git','branch','--show-current'],
 'head':['git','rev-parse','HEAD'],
 'origin':['git','remote','get-url','origin'],
 'content':['git','submodule','status','content'],
 'trackedChangedFiles':['git','diff','--name-only'],
 'status':['git','status','--short']
}.items()}
for k,value in identity.items():
 if value['exitCode']:problems.append('Git identity '+k)
changed=identity['trackedChangedFiles']['output'].splitlines()
if changed!=['README.md']:problems.append('Unexpected tracked source changes')
whitespace=run(['git','-c','core.whitespace=trailing-space,space-before-tab,cr-at-eol','diff','--check'])
if whitespace['exitCode']:problems.append('Git diff whitespace')
sdk=run(['dotnet','--list-sdks'])
if sdk['exitCode']:problems.append('SDK inspection')
browser=json.loads((records/'implementation-report-validation.json').read_text(encoding='utf-8'))
if not browser['allChecksPassed']:problems.append('Implementation report checks')
if browser['reportSha256']!=digest(root/'doc/project/reports/trial-implementation-spec-2026-10-08.html'):problems.append('Stale report QA hash')
if browser['specificationSha256']!=digest(root/'doc/project/design/trial-platform-implementation-spec.md'):problems.append('Stale specification QA hash')
result={
 'checkedAtLocal':datetime.datetime.now().astimezone().isoformat(),
 'allChecksPassed':not problems,'problems':problems,
 'documents':len(docs),'localLinkCount':len(links),'localLinks':links,
 'markdownTrailingWhitespace':white,'preservedUpstreamWhitespace':preserved_whitespace,'syntaxChecks':syntax,
 'protectedEvidence':protected,'identity':identity,'gitWhitespace':whitespace,
 'readOnlyInstalledSdks':sdk,
 'archiveVolumeSnapshot':{'volume':'D:','freeBytes':shutil.disk_usage(root).free,'qualification':'Dated observation, not a reserved capacity or performance promise.'},
 'reportValidation':str(records/'implementation-report-validation.json'),
 'manualVisualReview':{
  'reviewedDirectory':r'D:\Rigs of Rods\trial-implementation-review-2026-10-08-192235-052329',
  'views':['desktop-overview.png','selected-architecture.png','capture-quality-policy.png','required-gap-explorer.png','mobile-overview.png','mobile-policy.png'],
  'finding':'Readable diagrams, controls and labels; no clipping seen. Final rerender changes one grammar word and passed browser QA again.'
 },
 'scope':'Repository documentation/reference/syntax and protected-evidence integrity checks only. No engine implementation, game build/run, framework installation, calibrated physical result, Git commit or push.'
}
output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'allChecksPassed':not problems,'problems':problems,'documents':len(docs),'localLinkCount':len(links),'protectedEvidenceChecks':len(protected),'trackedChangedFiles':changed,'reportCaptureDirectory':browser['captureDirectory']},indent=2))
raise SystemExit(0 if not problems else 1)
