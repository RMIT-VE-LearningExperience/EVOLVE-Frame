import json,math
from pathlib import Path
p=json.loads(Path('output/revit/roof_profiles.json').read_text());items=[];assemblies=[]
chords={'T1':[1,2,5,6],'T2':[1,2,3,6,7],'T3':[1,2,3,8,9],'T4':[1,2,3,6,7],'T5':[1,2,12,13],'T6':[1,5],'H1':[1,2,3]}
labels={'T1':['TC1-L','BC+1T','TOW1-L','TOW2-L','TC1-R','BC1+1T-R','TOW1-R','TOW2-R'], 'T5':['TC1','TC2','W0','TOW1','TOW2','TOW3','TOW4','TOW5','TOW6','W7','W8','BC1+1T','BC2+1T'],'T6':['TC1','W0','W1','W2','BC1'],'H1':['TC1','TC2','BC1','TOW1','TOW2']}
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def sub(a,b):return [a[0]-b[0],a[1]-b[1]]
def extend_web(a,b,cs):
 result=[]
 for end,other in [(a,b),(b,a)]:
  direction=sub(end,other);candidates=[]
  for c,d in cs:
   v=sub(d,c);den=cross(direction,v)
   if abs(den)<1e-6:continue
   t=cross(sub(c,end),v)/den;u=cross(sub(c,end),direction)/den
   if -.005<=t and -.02<=u<=1.02 and t*math.hypot(*direction)<260:candidates.append((t,[end[i]+t*direction[i] for i in range(2)]))
  result.append(min(candidates,key=lambda q:q[0])[1] if candidates else end)
 return result
def add(name,key,origin,direction,z):
 prof=p[name];normal=[-direction[1],direction[0],0];cs=[(m['a'],m['b']) for m in prof['members'] if m['index'] in chords.get(name,[])]
 assemblies.append({'mark':key,'type':name,'origin':origin,'direction':direction,'base':z,'source_page':prof['page']})
 for m in prof['members']:
  a,b=m['a'],m['b']
  if name=='J5':a,b=([2533-q[0],q[1]] for q in (a,b))
  if name in chords and m['index'] not in chords[name]:a,b=extend_web(a,b,cs)
  conv=lambda q:[round(origin[0]+q[0]*direction[0],2),round(origin[1]+q[0]*direction[1],2),round(z+q[1],2)]
  label=labels.get(name,[]);member=label[m['index']-1] if label else ('M%02d'%m['index'])
  grade='MGP12' if name=='H1' and m['index'] in [1,2] else 'MGP10'
  items.append({'mark':key+'-'+member,'assembly':key,'a':conv(a),'b':conv(b),'normal':normal,'depth':m['depth'],'width':m['width'],'grade':grade,'source':f'K0964 roof PDF p{prof["page"]}; layout p22; member axes derived from dimension-calibrated supplier drawing; square coordination end cuts; connector plates pending'})
for i in range(15):add('T1',f'RT-T1-{i+1:02}',[10237.5+900*i,150],[0,1],5740)
add('T4','RT-T4-01',[8437.5,150],[0,1],5740)
add('T2','RT-T2-01',[24632.5,150],[0,1],5740)
for i,x in enumerate([9337.5,23732.5]):add('T3',f'RT-T3-{i+1:02}',[x,150],[0,1],5740)
for i,(x,y,dx,dy) in enumerate([(6230,150,1,1),(6230,8030,1,-1),(26840,150,-1,1),(26840,8030,-1,-1)]):
 add('H1',f'RT-H1-{i+1:02}',[x,y],[dx/math.sqrt(2),dy/math.sqrt(2)],5740)
 for name,offset in [('C1',390),('C2',1290)]:
  add(name,f'RT-{name}-{i*2+1:02}',[x+dx*offset,y],[0,dy],5740)
  add(name,f'RT-{name}-{i*2+2:02}',[x,y+dy*offset],[dx,0],5740)
for side,x,dx in [('W',6230,1),('E',26840,-1)]:
 for j,y in enumerate([2340,5840]):add('J1',f'RT-J1-{side}{j+1}',[x,y],[dx,0],5740)
 add('J3',f'RT-J3-{side}',[x,4090],[dx,0],5740)
 for name,y in [('J2' if side=='E' else 'J4',3190),('J2' if side=='E' else 'J5',4990)]:add(name,f'RT-{name}-{side}-{int(y)}',[x,y],[dx,0],5740)
for i,pdfx in enumerate([101.46,119.76,138,156.30,174.60,192.84,211.08,229.38]):
 x=150+(pdfx-99.12)*(6080/(229.8-99.12));add('T5',f'RT-T5-{i+1:02}',[x,3060],[0,1],2750)
for i,pdfy in enumerate([212.88,228.60,244.26,259.98,275.64]):
 y=8030-(pdfy-207.96)*(7880/(377.16-207.96));add('T6',f'RT-T6-{i+1:02}',[27890,y],[-1,0],2750)
Path('output/revit/roof_members_manifest.json').write_text(json.dumps(items,indent=2))
Path('output/revit/roof_assemblies_manifest.json').write_text(json.dumps(assemblies,indent=2))
print(len(assemblies),'trusses;',len(items),'members')
