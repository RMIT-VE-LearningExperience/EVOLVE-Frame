import json,math
from pathlib import Path
walls=json.loads(Path('output/revit/build_manifest.json').read_text())['walls'];rows=[]
offsets={'GF-N':(0,-75),'GF-E':(-75,0),'GF-S':(0,75),'GF-ALF-E':(75,0),'GF-ALF-N':(0,75),'GF-NOOK-E':(-75,0),'GF-GAR-S':(0,75),'FF-N':(0,-50),'FF-S':(0,50),'FF-W':(50,0),'FF-E':(-50,0)}
for wall in walls:
 mark=wall['mark']
 if mark in ['GF-GAR-W','GF-GAR-N','GF-GAR-E']:continue # Architectural masonry boundary enclosure; not assumed to be timber veneer.
 a=list(wall['a']);b=list(wall['b']);off=offsets.get(mark,(0,0));a=[a[i]+off[i] for i in range(2)];b=[b[i]+off[i] for i in range(2)]
 if mark=='GF-GAR-S':a[0]=6320
 h=abs(a[1]-b[1])<.01
 if (h and a[0]>b[0]) or (not h and a[1]>b[1]):a,b=b,a
 axis=0 if h else 1;lo=a[axis];hi=b[axis];direction=[1,0,0] if h else [0,1,0]
 bottom=wall['z'];top=bottom+wall['height'] if mark=='FF-STAIR-DWARF' else 5740 if mark.startswith('FF-') else 2750
 bp=45 if mark.startswith('FF-') else 35;studbase=bottom+bp;studtop=top-90;spacing=600 if mark.startswith('FF-') else 450
 openings=[]
 for o in wall['openings']:
  if o['centre']+o['width']/2<=lo or o['centre']-o['width']/2>=hi:continue
  openings.append(dict(o,L=o['centre']-o['width']/2,R=o['centre']+o['width']/2,low=bottom+o['sill'],high=bottom+o['sill']+o['height']))
 def xyz(s,z):return [round(s,2),a[1],round(z,2)] if h else [a[0],round(s,2),round(z,2)]
 def member(key,p,q,depth=90,width=45,normal=None,grade='MGP10'):
  if math.dist(p,q)<5:return
  rows.append({'mark':'WF-'+mark+'-'+key,'assembly':mark,'a':p,'b':q,'normal':normal or direction,'depth':depth,'width':width,'grade':grade,'source':'A07/A08 setout; A13 common studs90x45 GF450/FF600, plates, nogs; S13 minimum framing. Nominal opening sizes, rough allowances and load-specific lintels pending. D01: GF top plates retain ceiling datum and clash42mm with413 joists.'})
 # Sole plates are interrupted at doors; double top plates are separate members.
 cuts=sorted([(o['L'],o['R']) for o in openings if o['low']<=bottom+1]);start=lo
 for i,(l,r) in enumerate(cuts+[(hi,hi)]):
  if l>start:member(f'BP{i:02}',xyz(start,bottom+bp/2),xyz(min(l,hi),bottom+bp/2),bp,90)
  start=max(start,r)
 for i,z in enumerate([top-67.5,top-22.5]):member('TP'+str(i+1),xyz(lo,z),xyz(hi,z),45,90)
 positions=[lo+22.5,hi-22.5];positions += [lo+22.5+i*spacing for i in range(1,math.ceil((hi-lo-45)/spacing)) if lo+22.5+i*spacing<hi-22.5]
 for o in openings:
  positions += [o['L']-67.5,o['L']-22.5,o['R']+22.5,o['R']+67.5]
 positions=sorted(set(round(x,2) for x in positions if lo+20<=x<=hi-20))
 # Suppress near-duplicate common studs where the jamb pack controls.
 jambs=[o[k]+d for o in openings for k,ds in [('L',[-67.5,-22.5]),('R',[22.5,67.5])] for d in ds]
 positions=[x for x in positions if x in jambs or not any(0<abs(x-j)<44.9 for j in jambs)]
 for i,s in enumerate(positions):
  intervals=[(studbase,studtop)]
  for o in openings:
   if o['L']-22.4<s<o['R']+22.4:
    intervals=[]
    if o['low']-45>studbase:intervals.append((studbase,o['low']-45))
    if o['high']+45<studtop:intervals.append((o['high']+45,studtop))
  for j,(z0,z1) in enumerate(intervals):member(f'S{i:03}-{j}',xyz(s,z0),xyz(s,z1))
 for i,o in enumerate(openings):
  if o['low']>bottom+1:member(f'SILL{i:02}',xyz(o['L'],o['low']-22.5),xyz(o['R'],o['low']-22.5),45,90)
  member(f'HEAD-RAIL{i:02}',xyz(o['L'],o['high']+22.5),xyz(o['R'],o['high']+22.5),45,90)
 z=(studbase+studtop)/2
 for i,(l,r) in enumerate(zip(positions,positions[1:])):
  if r-l<47:continue
  if any(l<o['R'] and r>o['L'] and o['low']-45<z<o['high']+45 for o in openings):continue
  member(f'N{i:03}',xyz(l+22.5,z),xyz(r-22.5,z),35,70,grade='Merch Pine')
Path('output/revit/wall_frame_manifest.json').write_text(json.dumps(rows,indent=2))
print(len(rows),'wall-frame members')
