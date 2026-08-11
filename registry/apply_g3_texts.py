#!/usr/bin/env python3
"""One-shot acquisition of five official Missouri SB 1012 text states."""
import hashlib,re,subprocess,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parent; T=R/'texts'; I=R/'incoming'; T.mkdir(exist_ok=True); I.mkdir(exist_ok=True)
D={
'01I':('https://www.senate.mo.gov/26info/pdf-bill/intro/SB1012.pdf','introduced-5687S.01I'),
'02C':('https://www.senate.mo.gov/26info/pdf-bill/comm/SB1012.pdf','scs-5687S.02C'),
'10F':('https://www.senate.mo.gov/BillTracking/Bills/BillInformation?amendmentId=309&handler=AmendmentPdf&year=2026','withdrawn-ss-5687S.10F'),
'16F':('https://www.senate.mo.gov/BillTracking/Bills/BillInformation?amendmentId=631&handler=AmendmentPdf&year=2026','ss2-5687S.16F'),
'16P':('https://www.senate.mo.gov/26info/pdf-bill/perf/SB1012.pdf','perfected-5687S.16P')}
def norm(s):
 s=s.replace('\r','').replace('\f','\n'); o=[]
 for x in s.splitlines():
  x=x.strip()
  if not x or re.fullmatch(r'\d+',x) or x=='✓': continue
  if re.fullmatch(r'(?:SCS |SS#?2? SCS )?SB 1012 \d+',x): continue
  x=re.sub(r'^\d+\s+(?=[A-Za-z\(\[\"“])','',x); o.append(x)
 return '\n'.join(o).strip()+'\n'
for k,(u,n) in D.items():
 p=I/f'mo-sb1012-2026--{n}.pdf'; t=T/f'mo-sb1012-2026--{n}.txt'
 q=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 registry-audit'})
 with urllib.request.urlopen(q,timeout=60) as r:p.write_bytes(r.read())
 if not p.read_bytes().startswith(b'%PDF'):raise SystemExit(f'{k}: not PDF')
 s=norm(subprocess.check_output(['pdftotext','-enc','UTF-8',str(p),'-'],text=True))
 if (k=='01I')==('1.2045' in s):raise SystemExit(f'{k}: §1.2045 topology check failed')
 t.write_text(s); print(k,p.stat().st_size,t.stat().st_size,hashlib.sha256(t.read_bytes()).hexdigest())
