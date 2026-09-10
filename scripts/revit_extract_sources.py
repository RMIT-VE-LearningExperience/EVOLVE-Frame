from pathlib import Path
import json
from pypdf import PdfReader
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'revit' / 'source_audit'
OUT.mkdir(parents=True, exist_ok=True)
register = []
for label, file in [
    ('architectural','Leichhardt_Architectural Plans (1).pdf'),
    ('engineering','Leichhardt_Engineering Plans (1).pdf'),
    ('roof','Leichhardt_Engineering Roof Truss Frame (1).pdf'),
    ('subfloor','Leichhardt_Engineering Subfloor Frame (1).pdf'),
]:
    reader = PdfReader(ROOT / file)
    sheets = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text(extraction_mode='layout')
        (OUT / f'{label}-{i:02}.txt').write_text(text, encoding='utf-8')
        sheets.append({'page':i, 'width_pt':float(page.mediabox.width), 'height_pt':float(page.mediabox.height), 'rotation':page.rotation})
    register.append({'package':label,'file':file,'pages':len(reader.pages),'metadata':{str(k):str(v) for k,v in (reader.metadata or {}).items()},'sheets':sheets})
(OUT / 'register.json').write_text(json.dumps(register, indent=2), encoding='utf-8')
print(json.dumps([{'package':r['package'],'pages':r['pages'],'metadata':r['metadata']} for r in register],indent=2))
