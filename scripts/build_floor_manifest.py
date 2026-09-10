import pdfplumber,json,math,collections
from pathlib import Path
profiles=json.loads(Path('output/revit/floor_profiles.json').read_text());p=pdfplumber.open('Leichhardt_Engineering Subfloor Frame (1).pdf').pages[46]
words=p.extract_words(line_dir_rotated='ttb',char_dir_rotated='ltr',extra_attrs=['non_stroking_color']);labels=[]
for w in words:
 text=w['text'][::-1]
 if text in profiles:labels.append(dict(w,type=text))
edges=list({(round(e['x0'],3),round(e['top'],3),round(e['bottom'],3)) for e in p.edges if e['width']<.01 and e['height']>20 and 148<e['x0']<686 and 185<e['top']<392 and e['bottom']<393})
candidates=[]
for x,t,b in edges:
 for x2,t2,b2 in edges:
  if 1.7<x2-x<2.6 and abs(t-t2)<.15 and abs(b-b2)<.15:candidates.append({'x':(x+x2)/2,'top':t,'bottom':b})
sx=20610/(684.96-149.76);sy=7880/(391.44-186.84);rows=[];assemblies=[];counts=collections.Counter();used=set()
for w in sorted(labels,key=lambda w:(int(w['type'][2:]),w['x0'])):
 typ=w['type'];prof=profiles[typ];counts[typ]+=1;key=f'SF-{typ}-{counts[typ]:02}'
 y=(w['top']+w['bottom'])/2
 choices=[c for c in candidates if c['top']<y<c['bottom'] and abs((c['bottom']-c['top'])*sy-prof['span'])<100 and (c['x'],c['top'],c['bottom']) not in used]
 if typ=='FJ20':target=150.9
 else:target=w['x1']+1
 if not choices:raise ValueError((typ,'no match',w))
 score=lambda c:abs(c['x']-target) if typ=='FJ20' else min(abs(c['x']-target),abs(c['x']-(w['x0']-1)))
 c=min(choices,key=score);used.add((c['x'],c['top'],c['bottom']));x=6230+(c['x']-149.76)*sx
 # Model exact supplier length. The layout shows diagrammatic member extents.
 south=max(150,round(150+(391.44-c['bottom'])*sy,1));north=round(150+(391.44-c['top'])*sy,1)
 if abs(north-8030)<110:south=8030-prof['span']
 source=f'K0964 subfloor PDF p{prof["page"]}, layout p47; type {typ}; exact span {prof["span"]}mm. Fabrication IDs in group: '+', '.join(prof['ids'])+'. Layout labels type only; individual ID-to-position assignment pending. D01 retained. Proprietary metal webs not assigned an invented gauge.'
 for i,m in enumerate(prof['wood']):
  def point(q):return [round(x,2),round(south+q[0]*prof['span']/prof['length'],2),round(2708+q[1],2)]
  rows.append({'mark':key+f'-TIMBER-{i+1:02}','assembly':key,'a':point(m['a']),'b':point(m['b']),'normal':[0,1,0],'depth':m['depth'],'width':m['width'],'grade':'MGP10','source':source})
 assemblies.append({'mark':key,'type':typ,'x':round(x,2),'south':south,'north':south+prof['span'],'depth':prof['height'],'layout_span':round((c['bottom']-c['top'])*sy,1),'label_distance':round(score(c),2),'page':prof['page']})
Path('output/revit/floor_members_manifest.json').write_text(json.dumps(rows,indent=2));Path('output/revit/floor_assemblies_manifest.json').write_text(json.dumps(assemblies,indent=2))
print(len(assemblies),'joists;',len(rows),'timber parts')
print('TYPE COUNTS',dict(counts));print('LARGE LABEL DISTANCES',[a for a in assemblies if a['label_distance']>3]);print('QUANTITY MISMATCHES',[(t,counts[t],len(pr['ids'])) for t,pr in profiles.items() if counts[t]!=len(pr['ids'])])
print('DUPLICATE POSITIONS',[k for k,c in collections.Counter((a['x'],a['south'],a['north']) for a in assemblies).items() if c>1])
