from pathlib import Path
import json,re
import pdfplumber
root=Path(__file__).resolve().parents[1]
out=root/'output/revit/source_audit'
packages={
 'architectural':'Leichhardt_Architectural Plans (1).pdf',
 'engineering':'Leichhardt_Engineering Plans (1).pdf',
 'roof':'Leichhardt_Engineering Roof Truss Frame (1).pdf',
 'subfloor':'Leichhardt_Engineering Subfloor Frame (1).pdf'}
rows=[]
for package,file in packages.items():
 with pdfplumber.open(root/file) as pdf:
  for i,page in enumerate(pdf.pages,1):
   text=page.extract_text() or ''
   (out/f'{package}-{i:02}-readable.txt').write_text(text,encoding='utf-8')
   dates=sorted(set(re.findall(r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b',text)))
   rev=sorted(set(re.findall(r'\bC[0-9]+\b',text)))
   issue=('20.01.2024 construction issue, revision dash' if package=='architectural' else
          'C1 construction issue 03/12/25' if package=='engineering' else
          'K0964 layout 3/04/2026' if i==len(pdf.pages) else 'K0964 detail/certification 10/04/2026')
   rows.append(dict(package=package,page=i,controlling_issue=issue,raw_date_candidates=dates,raw_mark_candidates=rev))
(out/'revision_register.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
