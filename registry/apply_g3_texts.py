#!/usr/bin/env python3
"""One-shot normalisation of the five stored official Missouri SB 1012 PDFs."""
import hashlib,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent; T=R/'texts'; I=R/'incoming'
N={'01I':'introduced-5687S.01I','02C':'scs-5687S.02C','10F':'withdrawn-ss-5687S.10F','16F':'ss2-5687S.16F','16P':'perfected-5687S.16P'}
def norm(s):
 s=s.replace('\r','').replace('\f','\n'); o=[]
 for x in s.splitlines():
  x=x.strip()
  if not x or re.fullmatch(r'\d+',x) or x=='✓': continue
  if re.fullmatch(r'(?:SS#?\s*2\s+)?(?:SCS\s+)?SB\s+1012(?:\s+\d+)?',x,re.I): continue
  x=re.sub(r'^\d+\s+(?=[A-Za-z\(\[\"“])','',x); o.append(x)
 # pdftotext puts Missouri statutory subsection numbers such as "2." on their
 # own line. legdiff deliberately recognises "2. Text" rather than a bare decimal,
 # so join only a bare 1–3 digit subsection marker to the next extracted line.
 merged=[]; i=0
 while i<len(o):
  if re.fullmatch(r'\d{1,3}\.',o[i]) and i+1<len(o):
   merged.append(o[i]+' '+o[i+1]); i+=2
  else:
   merged.append(o[i]); i+=1
 return '\n'.join(merged).strip()+'\n'
for k,n in N.items():
 p=I/f'mo-sb1012-2026--{n}.pdf'; t=T/f'mo-sb1012-2026--{n}.txt'
 if not p.exists() or not p.read_bytes().startswith(b'%PDF'):raise SystemExit(f'{k}: stored source PDF missing')
 s=norm(subprocess.check_output(['pdftotext','-enc','UTF-8',str(p),'-'],text=True))
 if (k=='01I')==('1.2045' in s):raise SystemExit(f'{k}: §1.2045 topology check failed')
 t.write_text(s); print(k,t.stat().st_size,hashlib.sha256(t.read_bytes()).hexdigest())
