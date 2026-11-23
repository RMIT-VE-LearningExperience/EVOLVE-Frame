import pdfplumber,json,re,math
from pathlib import Path
pdf=pdfplumber.open('Leichhardt_Engineering Subfloor Frame (1).pdf');profiles={}
for n,p in enumerate(pdf.pages[:-1],1):
 text=Path(f'output/revit/source_audit/subfloor-{n:02}-readable.txt').read_text(encoding='utf-8')
 match=re.search(r'Joist Name: (FJ\d+)',text)
 def yellow(s):
  c=s.get('non_stroking_color')
  return s.get('fill') and isinstance(c,tuple) and len(c)==3 and .9<c[0]<1 and .65<c[1]<.82 and .3<c[2]<.5
 wood=[s for s in p.curves+p.rects if yellow(s)]
 if not match or not wood:continue
 name=match[1];span=float(re.search(r'Span:\s*(\d+)',text)[1]);ids=re.search(r'Joists: (.*?) Laminations:',text)
 ids=re.findall(r'FJ\d+',ids[1]) if ids else []
 height=360 if 'MSJ-360' in text else 413
 top=min(s['top'] for s in wood);bottom=max(s['bottom'] for s in wood);left=min(s['x0'] for s in wood);scale=height/(bottom-top)
 shapes=[]
 for s in wood:
  points=s['pts'];x0=(s['x0']-left)*scale;x1=(s['x1']-left)*scale;z0=(bottom-s['bottom'])*scale;z1=(bottom-s['top'])*scale
  if x1-x0>z1-z0: a=[x0,(z0+z1)/2];b=[x1,(z0+z1)/2];depth=45;width=90
  else:a=[(x0+x1)/2,z0];b=[(x0+x1)/2,z1];depth=90;width=45
  shapes.append({'a':[round(q,2) for q in a],'b':[round(q,2) for q in b],'depth':depth,'width':width})
 record={'page':n,'span':span,'ids':ids,'height':height,'length':round((max(s['x1'] for s in wood)-left)*scale,2),'wood':shapes,'source_baseline':[left,bottom],'scale':scale}
 if name not in profiles:profiles[name]=record
 else:profiles[name]['ids']=list(dict.fromkeys(profiles[name]['ids']+ids))
Path('output/revit/floor_profiles.json').write_text(json.dumps(profiles,indent=2))
print([(k,v['page'],v['height'],v['span'],v['length'],len(v['ids']),len(v['wood'])) for k,v in profiles.items()])
