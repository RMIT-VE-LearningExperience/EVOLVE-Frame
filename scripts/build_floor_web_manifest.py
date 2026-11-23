import pdfplumber,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path('tmp/python_geom_lib').resolve()))
from shapely.geometry import Polygon
pdf=pdfplumber.open('Leichhardt_Engineering Subfloor Frame (1).pdf');profiles=json.loads(Path('output/revit/floor_profiles.json').read_text());assemblies=json.loads(Path('output/revit/floor_assemblies_manifest.json').read_text());webs={};rows=[]
for name,pr in profiles.items():
 p=pdf.pages[pr['page']-1];left,bottom=pr['source_baseline'];scale=pr['scale'];right=left+pr['length']/scale;top=bottom-pr['height']/scale
 candidates=[]
 for s in p.curves:
  if not (s['x0']>=left-.1 and s['x1']<=right+.1 and s['top']>=top-.1 and s['bottom']<=bottom+.1 and s['height']>10 and len(s['pts'])>=10):continue
  parts=[];part=[]
  for command in s['path']:
   if command[0]=='m':
    if part:parts.append(part)
    part=[command[1]]
   elif command[0]=='l':part.append(command[1])
   elif command[0]=='h':
    if part:parts.append(part);part=[]
  if part:parts.append(part)
  for pts in parts:
   if len(pts)<10:continue
   candidates.append(dict(s,pts=pts,x0=min(q[0] for q in pts),x1=max(q[0] for q in pts),top=min(q[1] for q in pts),bottom=max(q[1] for q in pts)))
 filled={tuple(round(s[k],3) for k in ['x0','x1','top','bottom']) for s in candidates if s.get('fill')}
 selected=[];seen=set()
 for s in sorted(candidates,key=lambda s:not s.get('fill')):
  key=tuple(round(s[k],3) for k in ['x0','x1','top','bottom'])
  if key in seen:continue
  seen.add(key);pts=[]
  for x,y in s['pts']:
   q=[(x-left)*scale*pr['span']/pr['length'],(bottom-y)*scale]
   if not pts or math.dist(pts[-1],q)>.9:pts.append(q)
  if math.dist(pts[-1],pts[0])<.9:pts.pop()
  selected.append({'points':pts,'side':-1 if key in filled else 1})
 webs[name]=selected
for a in assemblies:
 for i,web in enumerate(webs[a['type']]):
  x=a['x']+(-46 if web['side']==-1 else 45)
  rows.append({'mark':a['mark']+f'-MSW-{i+1:02}','points':[[round(x,3),round(a['south']+p[0],3),round(2708+p[1],3)] for p in web['points']],'source':f'K0964 subfloor PDF p{a["page"]}; MultiStrut G300 Z275 1mm per Multinail MultiStrut_09_2024.pdf p3. Supplier side-profile outline; front/back inferred from filled/unfilled diagram; pressed ribs and nail teeth omitted.'})
fixed=[];repairs=0
for row in rows:
 poly=Polygon([(p[1],p[2]) for p in row['points']])
 if not poly.is_valid:poly=poly.buffer(0);repairs+=1
 parts=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
 for i,part in enumerate(parts):
  assert len(part.interiors)==0,'Unexpected web hole'
  item=dict(row);item['mark']+=f'-{i+1}' if len(parts)>1 else '';item['points']=[[row['points'][0][0],round(y,3),round(z,3)] for y,z in list(part.exterior.coords)[:-1]];fixed.append(item)
Path('output/revit/floor_web_manifest.json').write_text(json.dumps(fixed,indent=2));print(len(fixed),'individual MultiStrut steel webs;',repairs,'overlapping PDF subpaths unioned')
