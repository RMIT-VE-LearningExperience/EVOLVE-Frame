import pdfplumber, math, json, re
from pathlib import Path
pages=[2,3,5,6,8,9,10,11,12,14,16,18,20,21]
pdf=pdfplumber.open('Leichhardt_Engineering Roof Truss Frame (1).pdf')
profiles={}
for num in pages:
 p=pdf.pages[num-1]; text=Path(f'output/revit/source_audit/roof-{num:02}-readable.txt').read_text(encoding='utf-8')
 name=re.search(r'Truss: Layout created (\w+)',text)[1];width=float(re.search(r'Width: (\d+)',text)[1])
 shapes=[s for s in p.curves+p.rects if s.get('fill') and s.get('non_stroking_color')==(0.980469,0.785156,0.195068)]
 left=min(s['x0'] for s in shapes);right=max(s['x1'] for s in shapes);scale=width/(right-left)
 # Bottom chords are the long horizontal members in the lower part of each profile.
 horiz=[s for s in shapes if s['width']>s['height']*3]
 baseline=max(s['bottom'] for s in horiz)
 if name in ['T1','T2','T3','T4','C1','C2','J1','J2','J3','J4','J5']: offset=550
 elif name=='H1':offset=778
 elif name=='T5':offset=390
 else:offset=345
 members=[]
 for i,s in enumerate(shapes):
  pts=s['pts'];edges=[]
  for a,b in zip(pts,pts[1:]+pts[:1]):
   length=math.dist(a,b)
   if length>0:edges.append((length,a,b))
  edges.sort(reverse=True);_,a,b=edges[0]
  # Opposite long edge yields the member axis; rounded web caps remain square-cut in the coordination family.
  ux,uy=b[0]-a[0],b[1]-a[1]
  parallel=[e for e in edges[1:] if abs(ux*(e[2][1]-e[1][1])-uy*(e[2][0]-e[1][0]))/(math.hypot(ux,uy)*e[0])<.03]
  _,c,d=parallel[0] if parallel else edges[1]
  if math.dist(a,c)>math.dist(a,d):c,d=d,c
  pa=[(a[0]+c[0])/2,(a[1]+c[1])/2];pb=[(b[0]+d[0])/2,(b[1]+d[1])/2]
  convert=lambda q:[round((q[0]-left)*scale-offset,2),round((baseline-q[1])*scale,2)]
  ma,mb=convert(pa),convert(pb)
  if ma[0]>mb[0]:ma,mb=mb,ma
  depth=round(abs(ux*(c[1]-a[1])-uy*(c[0]-a[0]))/math.hypot(ux,uy)*scale)
  if abs(depth-90)<8:depth=90
  elif abs(depth-120)<8:depth=120
  members.append({'index':i+1,'a':ma,'b':mb,'depth':depth,'width':35})
 profiles[name]={'page':num,'transport_width':width,'scale_mm_per_pt':scale,'baseline_pdf':baseline,'members':members}
Path('output/revit/roof_profiles.json').write_text(json.dumps(profiles,indent=2))
for name,p in profiles.items():print(name,[(m['index'],m['depth'],m['a'],m['b']) for m in p['members']])

