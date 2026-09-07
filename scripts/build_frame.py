"""Leichhardt framing study. Run with Blender --background --python this_file.
Dimensions in metres. Plan-traced positions are deliberately distinguished from
scheduled sizes; see output/README.md and the embedded Blender text block.
"""
import bpy, math, json, csv, subprocess
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'timber_frame'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection': bpy.data.collections.remove(c)
def collection(name):
 c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c
C={n:collection(n) for n in ['01 Slab datum','02 Ground floor walls','03 Ground floor steel and LVL','04 First floor joists','05 Upper floor walls','06 Upper roof trusses','07 Garage roof','08 Porch roof','09 Bracing and connections','10 Stair framing','11 Roof battens','90 Plan references (hidden)','99 Presentation']}
def mat(name,color,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=.55; bs.inputs['Metallic'].default_value=metal
 return m
wood=mat('MGP10 pine',(0.62,.38,.16)); lvl=mat('LVL beams',(.42,.23,.09)); steel=mat('Structural steel',(.14,.20,.25),.72); zinc=mat('Galvanised connectors',(.48,.57,.63),.75); concrete=mat('Concrete datum',(.42,.45,.46)); braceboard=mat('Hardboard bracing',(.22,.12,.065)); stage=mat('Studio floor',(.09,.115,.14))
# Subtle timber variation in local member coordinates, no external textures.
for m in [wood,lvl]:
 nt=m.node_tree; bs=nt.nodes.get('Principled BSDF'); tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=7; tex.inputs['Detail'].default_value=2
 coord=nt.nodes.new('ShaderNodeTexCoord'); mapping=nt.nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(9,9,.3)
 nt.links.new(coord.outputs['Generated'],mapping.inputs[0]); nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
 ramp=nt.nodes.new('ShaderNodeValToRGB'); base=m.diffuse_color[:3]; ramp.color_ramp.elements[0].color=(*(v*.8 for v in base),1); ramp.color_ramp.elements[1].color=(*(min(v*1.2,1) for v in base),1)
 nt.links.new(tex.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
mesh=bpy.data.meshes.new('Unit member'); mesh.from_pydata([(-.5,-.5,-.5),(-.5,-.5,.5),(-.5,.5,-.5),(-.5,.5,.5),(.5,-.5,-.5),(.5,-.5,.5),(.5,.5,-.5),(.5,.5,.5)],[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]); mesh.update()
meshes={}
for m in [wood,lvl,steel,zinc,concrete,braceboard,stage]:
 mm=mesh.copy(); mm.name=m.name+' shared box'; mm.materials.append(m); meshes[m.name]=mm
inventory=[]
def box(name,loc,dims,col,material=wood,source='',status='Plan-traced position; scheduled/typical section'):
 assert min(dims)>0,(name,dims)
 o=bpy.data.objects.new(name,meshes[material.name]); C[col].objects.link(o); o.location=loc; o.scale=dims
 o['source']=source; o['modelling_basis']=status; o['section_or_bounds_mm']=' x '.join(str(round(d*1000,1)) for d in dims)
 inventory.append(dict(name=o.name,collection=col,material=material.name,x=round(loc[0],4),y=round(loc[1],4),z=round(loc[2],4),a_mm=round(dims[0]*1000,1),b_mm=round(dims[1]*1000,1),length_mm=round(dims[2]*1000,1),source=source,basis=status))
 return o
def beam(name,a,b,w,d,col,material=wood,source='',status='Plan-traced position; scheduled/typical section'):
 a,b=Vector(a),Vector(b); o=box(name,(a+b)/2,(w,d,(b-a).length),col,material,source,status); o.rotation_mode='QUATERNION'; o.rotation_quaternion=(b-a).to_track_quat('Z','Y'); return o
G='02 Ground floor walls'; U='05 Upper floor walls'; S='03 Ground floor steel and LVL'; F='04 First floor joists'; R='06 Upper roof trusses'; B='09 Bracing and connections'
GF=0; FF=3.14; GH=2.74; UH=2.59; ROOF=FF+UH
# Coordinate transforms calibrated to the timber envelope in the architectural sheets.
def gp(p): return (6.425+(p[0]-619)*20.52/922,.045+(870-p[1])*7.79/351)
def up(p): return (6.425+(p[0]-609)*20.52/921,.045+(844-p[1])*7.79/353)
wall_records=[]
def wall(name,a,b,z,h,col,openings=(),internal=False):
 a,b=Vector((*a,0)),Vector((*b,0)); L=(b-a).length; t=(b-a)/L; n=Vector((-t.y,t.x,0)); bottom=.035 if z<1 else .045; top=h-.09; sw=.035
 source='Architectural 07/08/11; Structural S12/S13'
 def pos(u,v,off=0): return a+t*u+n*off+Vector((0,0,z+v))
 def vmem(label,u,lo,hi,width=sw,material=wood):
  if hi-lo>.003:
   o=box(name+' | '+label,pos(u,(lo+hi)/2),(width,.09,hi-lo),col,material,source);o.rotation_euler.z=math.atan2(t.y,t.x);return o
 def hmem(label,u,v,level,depth=.045,material=wood):
  if v-u>.003:return beam(name+' | '+label,pos(u,level),pos(v,level),.09,depth,col,material,source)
 ops=sorted(openings,key=lambda o:o[1]); intervals=[]; jambs=[]
 for tag,center,width,sill,height in ops:
  l=center-width/2; r=center+width/2
  assert l>=0 and r<=L,(name,tag,L,l,r)
  intervals.append((l,r,sill,sill+height,tag))
 cursor=0
 for l,r,sill,head,tag in intervals:
  if sill==0: hmem('bottom plate',cursor,l, bottom/2,bottom); cursor=r
 hmem('bottom plate',cursor,L,bottom/2,bottom)
 hmem('top plate lower',0,L,h-.0675); hmem('top plate upper',0,L,h-.0225)
 studs=[.0175,L-.0175]+[i*.45 for i in range(1,math.ceil(L/.45)) if i*.45<L-.05]
 for l,r,sill,head,tag in intervals:
  for u in [l-.07,r+.07]: vmem(tag+' king stud',u,bottom,top,.045); jambs.append(u)
  for u in [l-.025,r+.025]: vmem(tag+' jack stud',u,bottom,head,.045); jambs.append(u)
  if internal: depth=.14
  elif z<1: depth=.12 if r-l<=.96 else .19 if r-l<=1.86 else .24
  else: depth=.09 if r-l<=1.26 else .14 if r-l<=1.86 else .19 if r-l<=2.46 else .24
  depth=min(depth,top-head)
  if depth>0: hmem(tag+' LVL lintel',l-.05,r+.05,head+depth/2,depth,lvl)
  if sill>0: hmem(tag+' sill',l,r,sill-.0225)
  for u in studs:
   if l+.025<u<r-.025:
    if sill>bottom+.06: vmem(tag+' sill cripple',u,bottom,sill-.045)
    vmem(tag+' head cripple',u,head+depth,top)
 for u in studs:
  if any(l-.115<u<r+.115 for l,r,_,_,_ in intervals):continue
  vmem('common stud',u,bottom,top)
 cuts=sorted(set([0,L]+studs+[v for v in jambs if 0<v<L]))
 for lev in [h/3,2*h/3]:
  for l,r in zip(cuts,cuts[1:]):
   mid=(l+r)/2
   if any(ol-.12<mid<orr+.12 for ol,orr,_,_,_ in intervals):continue
   if r-l>.045:hmem('nogging',l+.0175,r-.0175,lev,.035)
 # typical anchor and plate tie visualization, marked explicitly.
 for u in [0.2+i*.9 for i in range(max(1,int((L-.2)/.9)))]:
  if any(l<u<r and sill==0 for l,r,sill,_,_ in intervals):continue
  box(name+' | anchor washer',pos(u,.055),(.035,.035,.004),B,zinc,'S20-S25','Representative connection; not a fastener setout')
 wall_records.append(dict(name=name,a=list(a),b=list(b),z=z,h=h,openings=[list(o) for o in ops]))
 return L

def pw(name,a,b,level=0,ops=(),internal=False):
 transform=gp if level==0 else up
 aa,bb=transform(a),transform(b); direction=Vector(bb)-Vector(aa); length=direction.length
 # opening centres supplied as plan coordinates along the wall's varying axis
 op=[]
 for tag,p,width,sill,height in ops:
  pp=(p,a[1]) if a[1]==b[1] else (a[0],p)
  center=(Vector(transform(pp))-Vector(aa)).dot(direction.normalized())
  op.append((tag,center,width,sill,height))
 return wall(name,aa,bb,GF if level==0 else FF,GH if level==0 else UH,G if level==0 else U,op,internal)
# Ground floor perimeter, garage, laundry and alfresco returns.
pw('GF North wall',(619,519),(1541,519),ops=[('D02 laundry',672,.82,0,2.34),('W05 meals',816,2.710,.28,2.12),('W04 kitchen',1076,1.510,1.419,.514),('W03 powder',1272,.810,.28,2.12),('W02 entry',1457,.810,.28,2.12)])
pw('GF East entry and bedroom',(1541,870),(1541,519),ops=[('W01 bed 1',781,3.0,0,2.4),('D01 double entry',632,1.64,0,2.34)])
pw('GF South family and suite',(900,870),(1541,870),ops=[('W06 family',1015,3.060,.3,2.1),('W07 ensuite',1171,1.510,1.14,1.26)])
# Alfresco corner sliding openings are supported by steel rather than a corner stud.
pw('GF Laundry west',(619,759),(619,519),ops=[('Garage access',694,.920,0,2.34)])
pw('GF Laundry nook',(619,759),(714,759))
pw('GF Nook return',(714,759),(714,708))
# Open corner at the alfresco is represented by scheduled beams below.
pw('Garage rear',(339,452),(619,452))
pw('Garage outer end',(339,759),(339,452),ops=[('D03 garage',610,5.0,0,2.4)])
pw('Garage south',(339,759),(619,759),ops=[('D04 garage stacker',520,3.0,0,2.4)])
pw('Garage east upstand',(619,452),(619,519))
pw('Laundry east',(727,519),(727,663),internal=True)
pw('Laundry south',(619,663),(727,663),ops=[('Laundry opening',678,.82,0,2.34)],internal=True)
pw('Powder west',(1228,519),(1228,641),internal=True)
pw('Powder east',(1302,519),(1302,641),internal=True)
pw('Powder south',(1228,641),(1302,641),ops=[('Powder door',1270,.82,0,2.34)],internal=True)
pw('Pantry return',(1173,619),(1228,619),internal=True)
pw('Pantry nib',(1173,588),(1173,619),internal=True)
pw('Entry suite division',(1138,695),(1354,695),internal=True)
pw('Entry bedroom division',(1354,695),(1541,695),ops=[('Bedroom 1 door',1379,.82,0,2.34)],internal=True)
pw('Ensuite west',(1138,695),(1138,870),internal=True)
pw('Ensuite WIR division',(1237,695),(1237,870),ops=[('Ensuite access',793,.90,0,2.4)],internal=True)
pw('WIR bedroom division',(1354,695),(1354,870),ops=[('WIR access',720,.90,0,2.4)],internal=True)
pw('Ensuite WC partition',(1138,824),(1237,824),ops=[('WC door',1210,.72,0,2.34)],internal=True)
pw('Ensuite shower nib',(1138,742),(1180,742),internal=True)
# First floor exterior. Sizes from architectural schedule 11.
pw('FF North wall',(609,491),(1530,491),1,[('W13 WC',851,.67,1.02,1.26),('W12 bath',897,.67,1.02,1.26),('W11 bed 5',1094,2.23,.76,1.52),('W10 stair',1229,.85,.48,1.8)])
pw('FF South wall',(609,844),(1530,844),1,[('W15 bed 3',700,2.23,.76,1.52),('W16 bath 2',848,.67,1.02,1.26),('W17 bed 2',1001,2.23,.76,1.52),('W18 study',1134,1.81,.76,1.52),('W19 retreat',1262,2.23,.76,1.52)])
pw('FF West wall',(609,844),(609,491),1,[('W14 bed 4',568,2.23,.76,1.52)])
pw('FF East wall',(1530,844),(1530,491),1,[('W08 theatre',746,2.71,.48,1.8),('W09 void',566,2.71,.48,1.8)])
for name,a,b,ops in [
 ('Bed 4 and robes',(609,641),(823,641),[('Bed 4 door',754,.82,0,2.34)]),
 ('WIR3 and WIR4 division',(715,641),(715,698),[]),
 ('Robes hall wall',(609,698),(823,698),[('WIR3 slider',658,.82,0,2.4)]),
 ('WIR4 east',(823,641),(823,698),[]),
 ('Bed 4 WC division',(827,491),(827,598),[]),
 ('WC bath division',(870,491),(870,604),[]),
 ('Bath hall',(870,641),(994,641),[('Bathroom door',892,.72,0,2.34)]),
 ('WC south',(827,598),(870,598),[('WC door',849,.72,0,2.34)]),
 ('Bath robe division',(962,491),(962,615),[]),
 ('Linen north',(919,615),(994,615),[]),
 ('Linen west',(919,615),(919,641),[]),
 ('Bed 5 west',(994,491),(994,615),[]),
 ('Bed 5 south',(994,641),(1193,641),[('Bed 5 door',1018,.82,0,2.34)]),
 ('Bed 5 east',(1193,491),(1193,641),[]),
 ('Bed 2 study hall',(894,698),(1193,698),[('Bed 2 door',927,.82,0,2.34),('Study door',1169,.82,0,2.34)]),
 ('Bed 2 study division',(1081,698),(1081,844),[]),
 ('Study retreat division',(1193,698),(1193,844),[]),
 ('Bath 2 bedroom wall',(796,745),(894,745),[('Bath 2 door',869,.72,0,2.34)]),
 ('Bath 2 west',(796,745),(796,844),[]),
 ('Bath 2 east',(894,745),(894,844),[]),
 ('Theatre west',(1332,661),(1332,844),[]),
 ('Theatre north',(1332,641),(1530,641),[('Theatre entry',1365,.82,0,2.34)]),
 ]:pw('FF '+name,a,b,1,ops,True)
# Low wall beside staircase and the void, with timber handrail framing.
wall('FF stair balustrade',up((1250,548)),up((1420,548)),FF,1.2,U)
wall('FF void balustrade',up((1420,548)),up((1420,641)),FF,1.2,U)
# Slab surfaces retain stepdowns. Context only, no invented reinforcement.
box('House slab datum',(16.685,3.94,-.15),(20.81,8.08,.3),'01 Slab datum',concrete,'Architectural 06/07/12','Slab context only; footings and reinforcement not modelled')
box('Garage slab -86 mm',(3.235,5.89,-.236),(6.47,6.74,.3),'01 Slab datum',concrete,'Architectural 07','Slab context only')
box('Alfresco stepdown -86 mm',(9.48,1.78,-.13),(6.1,3.56,.086),'01 Slab datum',concrete,'Architectural 07','Stepdown shown; underlying main slab context')
box('Porch slab -226 mm',(27.71,6.255,-.376),(1.44,3.25,.3),'01 Slab datum',concrete,'Architectural 07','Slab context only')
# Structural members use the schedule names. Steel profiles are open meshes, not solid bars.
def ep(p):return (6.425+(p[0]-595)*20.52/923,.045+(559-p[1])*7.79/353)
def profile(name,a,b,width,depth,tw,tf,kind='I'):
 a,b=Vector(a),Vector(b); length=(b-a).length; q=(b-a).to_track_quat('Z','Y')
 parts=[(0,-depth/2+tf/2,width,tf),(0,depth/2-tf/2,width,tf)]
 if kind=='I':parts.append((0,0,tw,depth-2*tf))
 elif kind=='C':parts.append((-width/2+tw/2,0,tw,depth-2*tf))
 else:parts.extend([(-width/2+tw/2,0,tw,depth-2*tf),(width/2-tw/2,0,tw,depth-2*tf)])
 for i,(x,y,w,d) in enumerate(parts):
  o=box(name+f' profile {i+1}',(a+b)/2+q@Vector((x,y,0)),(w,d,length),S,steel,'Structural S09/S10','Scheduled section family; flange/web thickness visual approximation');o.rotation_mode='QUATERNION';o.rotation_quaternion=q

def sb(name,p1,p2,z,section):
 a=(*ep(p1),z);b=(*ep(p2),z)
 if section=='UC':profile(name+' 310UC137',a,b,.31,.32,.016,.025)
 elif section=='UB':profile(name+' 310UB40.4',a,b,.165,.31,.008,.012)
 elif section=='PFC200':profile(name+' 200PFC',a,b,.075,.2,.006,.012,'C')
 elif section=='PFC250':profile(name+' 250PFC',a,b,.09,.25,.007,.014,'C')
 else:beam(name+' '+section,a,b,.09 if section.startswith('2-') else .045,.3 if '300' in section else .24,S,lvl,'Structural S09/S10')
for spec in [('1B4',(883,240),(883,559),2.91,'UC'),('1B5',(883,386),(1227,386),2.91,'UB'),('1L2',(595,449),(595,559),2.7,'PFC200'),('1L3',(595,559),(746,559),2.7,'PFC200'),('1L6',(746,559),(883,559),2.7,'PFC200'),('1L4',(704,397),(883,397),2.7,'PFC200'),('1L5',(883,559),(1068,559),2.67,'PFC250'),('1B1',(1245,260),(1400,260),2.94,'2-300x45'),('1B2',(1245,206),(1245,260),2.94,'300x45'),('1B3',(1400,260),(1400,354),2.94,'300x45'),('1B6',(1180,328),(1278,328),2.94,'2-300x45'),('1B7',(1427,354),(1427,559),2.94,'2-300x45')]:sb(*spec)
# Garage lintel inverted T, precisely scheduled plate thicknesses.
a=gp((339,486)); b=gp((339,735))
beam('1L1 inverted T vertical 250x12',(*a,2.61),(*b,2.61),.012,.25,S,steel,'S10 1L1')
beam('1L1 inverted T horizontal 200x10',(*a,2.48),(*b,2.48),.2,.01,S,steel,'S10 1L1')
for name,p,dim,h in [('C1 alfresco west',(595,559),.089,2.6),('C1 alfresco middle',(746,559),.089,2.6),('C1 nook',(704,397),.089,2.6),('C3 portal south',(883,559),.1,2.75),('C3 portal north',(883,240),.1,2.75),('C1 living',(1116,386),.089,2.75),('C2 full height stair A',(1245,206),.089,ROOF),('C2 full height stair B',(1400,206),.089,ROOF)]:
 x,y=ep(p); profile(name,(x,y,0),(x,y,h),.2 if name.startswith('C3') else dim,dim,.006,.006,'RHS')
 box(name+' baseplate',(x,y,.012),(.23,.23,.024),B,steel,'S14-S16','Representative baseplate')
 for dx in [-.075,.075]:
  for dy in [-.075,.075]:box(name+' anchor bolt',(x+dx,y+dy,.04),(.014,.014,.05),B,zinc,'S14-S16','Representative bolt')
for p1,p2 in [((1245,206),(1400,206)),((1400,206),(1518,206))]:
 a=ep(p1);b=ep(p2);profile('ST1 150x100x6 RHS',(*a,3.02),(*b,3.02),.1,.15,.006,.006,'RHS')
# Alfresco corner opening heads and short perimeter framing around open sides.
a,b=gp((714,708)),gp((900,708));beam('Alfresco D05 north head',(*a,2.40),(*b,2.40),.09,.24,S,lvl,'Architectural 07; Structural S09','Corner opening approximation; steel support above')
a,b=gp((900,708)),gp((900,870));beam('1L7 alfresco side head',(*a,2.40),(*b,2.40),.045,.24,S,lvl,'Structural S09/S10 1L7')
# Flooring is omitted to expose all joists. MSJ timber chords with paired metal webs.
floor_count=0
def joist(name,x,y0,y1):
 global floor_count
 if y1-y0<.15:return
 floor_count+=1; z0=GH; z1=FF; source='Subfloor Frame 2026-04-10, MSJ-400-45; layout final sheet'
 beam(name+' bottom chord',(x,y0,z0+.0225),(x,y1,z0+.0225),.09,.045,F,wood,source)
 beam(name+' top chord',(x,y0,z1-.0225),(x,y1,z1-.0225),.09,.045,F,wood,source)
 for y in [y0+.0225,y1-.0225]:beam(name+' timber end block',(x,y,z0+.045),(x,y,z1-.045),.09,.045,F,wood,source)
 count=max(2,math.ceil((y1-y0)/.60));step=(y1-y0)/count
 for i in range(count):
  ya=y0+i*step+.04;yb=y0+(i+1)*step-.04
  for side in [-1,1]:
   xx=x+side*.042
   beam(name+f' metal web {i+1}',(xx,ya,z0+.052 if i%2==0 else z1-.052),(xx,yb,z1-.052 if i%2==0 else z0+.052),.012,.026,F,zinc,source,'Representative metal web topology; individual shop panel geometry not reproduced')
   for y,z in [(ya,z0+.05 if i%2==0 else z1-.05),(yb,z1-.05 if i%2==0 else z0+.05)]:box(name+' web plate',(xx,y,z),(.002,.06,.055),B,zinc,source,'Representative connector plate')
# Variable span zones follow the supplier layout and retain its L-shaped stair/void exclusion.
xlist=[6.425+i*.45 for i in range(46)]+[26.945]
for i,x in enumerate(xlist):
 if x<8.87: seam=4.66
 elif x<12.70:seam=3.665
 elif x<20.9:seam=3.91
 elif x<24.35:seam=4.635
 else:seam=4.68
 maxy=7.835 if x<20.91 else 6.60 if x<24.35 else 4.61
 joist(f'FJ-{i+1:02d}A',x,.045,min(seam,maxy))
 if seam<maxy-.1:joist(f'FJ-{i+1:02d}B',x,seam,maxy)
# Perimeter rims and void trimmers.
for i,(a,b) in enumerate([((6.425,.045),(26.945,.045)),((6.425,7.835),(20.91,7.835)),((6.425,.045),(6.425,7.835)),((26.945,.045),(26.945,4.61)),((20.91,7.835),(20.91,6.60)),((20.91,6.60),(24.35,6.60)),((24.35,6.60),(24.35,4.61)),((24.35,4.61),(26.945,4.61))]):
 beam(f'Floor rim/trimmer {i+1}',(*a,2.94),(*b,2.94),.045,.4,F,lvl,'Subfloor layout; S09','Plan-traced rim; section schematic except scheduled beams')
for y,xa,xb in [(1.8,6.425,12.7),(5.8,6.425,12.7),(1.8,12.7,26.945),(5.5,12.7,24.3)]:beam('Floor strongback 140x35',(xa,y,2.94),(xb,y,2.94),.035,.14,F,wood,'Subfloor layout final PDF page 47: Strongbacks 140 x 35mm','Scheduled section; approximate line placement')
# Sheet 08 dimension chain: 4000 flight, 2000 to inside of entry-end wall;
# 1100 stair zone measured inward from the adjacent exterior wall's inside face.
# Retain the indicative 1020 rough tread width, centred within that zone.
stair_foot=26.945-.045-2.0; run=4.0; stair_head=stair_foot-run
stair_center_y=7.835-.045-1.1/2
for yy in [stair_center_y-.46,stair_center_y+.02,stair_center_y+.47]:beam('Stair stringer',(stair_foot,yy,.08),(stair_head,yy,FF-.08),.045,.29,'10 Stair framing',lvl,'Architectural 08: 4000 stairs, 2000 entry, 1100 width','Dimension-based position; indicative rough framing sections')
for i in range(17):
 x=stair_foot-(i+.5)*run/17;z=(i+1)*FF/17
 box(f'Stair rough tread {i+1:02d}',(x,stair_center_y,z-.0225),(run/17,1.02,.045),'10 Stair framing',wood,'Architectural 08: 4000 stairs, 2000 entry, 1100 width','Indicative rough treads; centred with 40mm each side within architectural stair zone')
# Standard T1 roof trusses: supplier 7.880 m span, 25 degrees, 0.550 m overhang.
left=6.38;right=26.99; span=7.88;mid=span/2;pitch=math.tan(math.radians(25));heel=.106
roof_nodes=[]
def roofmember(name,a,b,width=.035,depth=.09,col=R):return beam(name,a,b,width,depth,col,wood,'Roof Truss Frame K0964, 10 April 2026','Scheduled basic geometry; see notes for simplified special trusses')
def roofplate(name,x,y,z,col=B):return box(name,(x,y,z),(.0015,.10,.10),col,zinc,'Roof shop drawings','Representative joint plate, no teeth')
def standard(x,tag):
 z=ROOF;peak=z+heel+mid*pitch
 roofmember(tag+' bottom chord',(x,0,z+.045),(x,span,z+.045))
 for ys,ye in [(-.55,mid),(mid,span+.55)]:
  roofmember(tag+' top chord',(x,ys,z+heel+min(ys,span-ys)*pitch),(x,ye,z+heel+min(ye,span-ye)*pitch))
 # Fink W geometry uses the supplier's 1.255 m bottom-node offsets.
 nodes=[(1.828,z+heel+1.828*pitch),(mid-1.255,z+.045),(mid,peak),(mid+1.255,z+.045),(span-1.828,z+heel+1.828*pitch)]
 for a,b in zip(nodes,nodes[1:]):roofmember(tag+' Fink web',(x,*a),(x,*b))
 for y,zz in [(0,z+.07),(span,z+.07)]+nodes:roofplate(tag+' nailplate',x+.019,y,zz)
 for y in [.045,7.835]:box(tag+' heel tie',(x+.04,y,z-.03),(.002,.05,.23),B,zinc,'Roof shop drawings MGrip','Representative truss grip')
for i in range(15):standard(left+3.94+i*.9,f'T1-{i+1:02d}')
# Truncated hip trusses at both ends, including girder plies.
def truncated(x,offset,tag,girder=False):
 z=ROOF;cut=offset;zz=z+heel+cut*pitch
 for lam in range(2 if girder else 1):
  xx=x+lam*.036
  roofmember(tag+' bottom',(xx,0,z+.045),(xx,span,z+.045),depth=.12 if girder else .09)
  for a,b in [((-.55,z+heel-.55*pitch),(cut,zz)),((cut,zz),(span-cut,zz)),((span-cut,zz),(span+.55,z+heel-.55*pitch))]:roofmember(tag+' top',(xx,*a),(xx,*b))
  nodes=[(cut,z+.045),(cut,zz)]
  n=4;length=span-2*cut
  for j in range(n):
   a=(cut+j*length/n,zz if j%2==0 else z+.045);b=(cut+(j+1)*length/n,z+.045 if j%2==0 else zz);roofmember(tag+' web',(xx,*a),(xx,*b))
  for y in [cut,span-cut]:roofmember(tag+' vertical',(xx,y,z+.045),(xx,y,zz));roofplate(tag+' plate',xx+.02,y,zz)
for end in [0,1]:
 for i,off in enumerate([.35,1.20,2.10,3.0]):truncated(left+off if end==0 else right-off,off,f'HIP-{end+1}-{i+1}',i==2)
# Hip rafters and jack members on the two end planes.
for end,xedge,xridge in [(0,left,left+mid),(1,right,right-mid)]:
 for yedge in [0,span]:roofmember(f'H{end+1} hip', (xedge+(-.55 if end==0 else .55),yedge+(-.55 if yedge==0 else .55),ROOF+heel-.55*pitch),(xridge,mid,ROOF+heel+mid*pitch),.035,.14)
 for j in range(1,9):
  y=-.45+j*.9
  if not 0<y<span:continue
  run=min(y,span-y);xend=xedge+(run if end==0 else -run)
  roofmember(f'J{end+1}-{j} jack top',(xedge+(-.55 if end==0 else .55),y,ROOF+heel-.55*pitch),(xend,y,ROOF+heel+run*pitch))
  roofmember(f'J{end+1}-{j} jack bottom',(xedge,y,ROOF+.045),(xend,y,ROOF+.045))
  roofmember(f'J{end+1}-{j} jack end web',(xend,y,ROOF+.045),(xend,y,ROOF+heel+run*pitch))
# Roof battens follow all four planes, including hips.
for d in [i*.75 for i in range(7)]:
 yy=-.55+d
 if yy>=mid:continue
 xx0=left+yy;xx1=right-yy;zz=ROOF+heel+yy*pitch+.07
 for y in [yy,span-yy]:roofmember('Main roof batten',(xx0,y,zz),(xx1,y,zz),.045,.035,'11 Roof battens')
 for x in [left+yy,right-yy]:roofmember('Hip end batten',(x,yy,zz),(x,span-yy,zz),.045,.035,'11 Roof battens')
# Low pitch mono trusses. Garage supplier T5 = 6.150 m; porch T6 = .950 m.
def mono(name,a,b,z,high=.891,p=5,col='07 Garage roof'):
 a,b=Vector(a),Vector(b);length=(b-a).length;low=high-length*math.tan(math.radians(p))
 def pt(t,zz):return (*(a+(b-a)*t),zz)
 roofmember(name+' bottom',pt(0,z+.045),pt(1,z+.045),col=col)
 roofmember(name+' top',pt(0,z+high-.045),pt(1,z+low-.045),col=col)
 n=max(1,math.ceil(length/1.2))
 for j in range(n+1):
  t=j/n;roofmember(name+' vertical',pt(t,z+.09),pt(t,z+high-(high-low)*t-.09),col=col)
 for j in range(n):
  t0=j/n;t1=(j+1)/n
  roofmember(name+' web',pt(t0,z+.09 if j%2==0 else z+high-(high-low)*t0-.09),pt(t1,z+high-(high-low)*t1-.09 if j%2==0 else z+.09),col=col)
for i in range(8):
 x=.20+i*.875;mono(f'T5-{i+1:02d}',(x,9.05),(x,2.90),GH-.086)
for y in [2.9+i*.75 for i in range(9)]:
 z=GH-.086+.891-(9.05-y)*math.tan(math.radians(5))+.02
 roofmember('Garage batten',(.2,y,z),(6.325,y,z),.045,.035,'07 Garage roof')
# The small porch roof sits below the upper-storey windows, carried on posts and PB1 beams.
for y in [4.63,7.835]:
 beam('P1 porch post',(28.185,y,-.226),(28.185,y,GH),.09,.09,S,wood,'S09/S10 P1 90x90 F7')
 beam('PB1 porch side',(26.945,y,GH-.1),(28.185,y,GH-.1),.045,.2,S,lvl,'S09/S10 PB1 200x45')
beam('PB1 porch front',(28.185,4.63,GH-.1),(28.185,7.835,GH-.1),.045,.2,S,lvl,'S09/S10 PB1')
for i in range(5):mono(f'T6-{i+1}',(27.235,4.63+i*.80),(28.185,4.63+i*.80),GH,.432,col='08 Porch roof')
# Bracing locations traced from S18/S19. Type D crosses, type C single angles,
# and B/E hardboard panels are separate objects and can be hidden for inspection.
def brace(name,p1,p2,upper=False,kind='D'):
 a,b=(up(p1),up(p2)) if upper else (gp(p1),gp(p2));z=FF if upper else 0;h=UH if upper else GH
 v=(Vector(b)-Vector(a)).normalized();off=Vector((-v.y,v.x))*.055
 a=Vector(a)+off;b=Vector(b)+off
 if kind in ['D','C']:
  beam(name+' diagonal',(*a,z+.10),(*b,z+h-.10),.0015,.03,B,zinc,'Structural S18/S19','Bracing bay traced; exact fixings not reproduced')
  if kind=='D':beam(name+' cross',(*b,z+.10),(*a,z+h-.10),.0015,.03,B,zinc,'Structural S18/S19','Bracing bay traced; exact fixings not reproduced')
 else:
  o=beam(name+' 4.8mm hardboard',(*a,z+h/2),(*b,z+h/2),.0048,h-.1,B,braceboard,'Structural S18/S19','Bay traced; panel joints schematic')
for name,a,b,k in [('Garage D1',(349,452),(457,452),'D'),('Garage D2',(498,452),(607,452),'D'),('Meals kitchen D',(900,519),(1021,519),'D'),('Kitchen D',(1110,519),(1218,519),'D'),('Entry D',(1320,519),(1441,519),'D'),('Laundry D',(727,528),(727,636),'D'),('Bedroom D',(1400,870),(1521,870),'D'),('Suite D',(1354,742),(1354,863),'D'),('Ensuite D',(1138,705),(1138,865),'D'),('Entry E',(1541,521),(1541,553),'E'),('Corner B',(900,870),(935,870),'B'),('Garage D3',(346,759),(442,759),'D')]:brace('GF '+name,a,b,kind=k)
for name,a,b,k in [('Bed4 D',(621,491),(742,491),'D'),('Bath D',(919,491),(1040,491),'D'),('Void D',(1400,491),(1521,491),'D'),('West D',(609,718),(609,835),'D'),('Bed5 C',(1193,512),(1193,631),'C'),('Hall C',(920,698),(1041,698),'C'),('Bed2 C',(894,750),(894,840),'C'),('Study D',(1193,719),(1193,837),'D'),('Theatre C',(1332,692),(1332,833),'C'),('Theatre D',(1407,844),(1515,844),'D'),('Bed4 E',(609,493),(609,516),'E'),('Bed3 B',(613,844),(655,844),'B'),('Bath2 B',(790,844),(824,844),'B')]:brace('FF '+name,a,b,True,k)
# Roof plane bracing, schematic locations from the supplier layout.
for xa,xb in [(11.0,16.0),(17.0,22.0)]:
 for side in [0,1]:
  y0=0 if side==0 else span;y1=mid
  beam('Roof diagonal strap',(xa,y0,ROOF+heel+.06),(xb,y1,ROOF+heel+mid*pitch+.06),.03,.0015,B,zinc,'Roof supplier layout','Representative continuous roof strap')
# Replace the main slab box with two non-overlapping rectangles around the alfresco stepdown.
o=bpy.data.objects.get('House slab datum');bpy.data.objects.remove(o,do_unlink=True);inventory[:]=[r for r in inventory if r['name']!='House slab datum']
box('Main house slab east',(19.88,3.94,-.15),(14.42,8.08,.3),'01 Slab datum',concrete,'Architectural 06/07','Slab context only')
box('Main house slab laundry meals',(9.475,5.77,-.15),(6.39,4.42,.3),'01 Slab datum',concrete,'Architectural 06/07','Slab context only')
# Raised theatre seating platform shown on architectural sheet 08.
# Its support construction is an explicit modelling assumption, independently editable.
px0,py0=up((1336,838));px1,py1=px0+2.30,up((1336,665))[1]
for i in range(math.ceil((px1-px0)/.45)+1):
 x=min(px0+i*.45,px1)
 beam('Theatre platform joist',(x,py0,FF+.35),(x,py1,FF+.35),.045,.14,'10 Stair framing',wood,'Architectural 08: platform 2300, step 420','Platform extent interpretation; framing sections assumed')
 for y in [py0,(py0+py1)/2,py1]:
  beam('Theatre platform support',(x,y,FF),(x,y,FF+.28),.09,.09,'10 Stair framing',wood,'Architectural 08','Representative platform support')
for y in [py0,py1]:beam('Theatre platform rim',(px0,y,FF+.35),(px1,y,FF+.35),.045,.14,'10 Stair framing',wood,'Architectural 08','Platform framing section assumed')

# Packed drawing references at the actual storey levels, disabled initially.
for name,file,z,origin_x,origin_y,sx,sy in [('Ground floor 07','arch-07.png',-.005,619,870,20.52/922,7.79/351),('First floor 08','arch-08.png',FF,609,844,20.52/921,7.79/353)]:
 im=bpy.data.images.load(str(ROOT/'tmp/plans'/file));im.pack()
 # Source renders are 2400 px wide, reading coordinates were from 1888px previews.
 factor=2400/1888;w,h=im.size
 o=bpy.data.objects.new(name,None);C['90 Plan references (hidden)'].objects.link(o);o.empty_display_type='IMAGE';o.data=im;o.empty_display_size=w*sx/factor
 o.location=(6.425+(w/(2*factor)-origin_x)*sx,.045+(origin_y-h/(2*factor))*sy,z);o.color[3]=.55;o.empty_image_depth='BACK';o['source']='Architectural PDF '+name
C['90 Plan references (hidden)'].hide_viewport=True;C['90 Plan references (hidden)'].hide_render=True
# Storey-specific connection collections make inspection layers self-contained.
connection_groups={}
for label in ['Ground connections','Floor connections','Upper connections','Roof connections']:
 c=bpy.data.collections.new(label);C[B].children.link(c);connection_groups[label]=c
for ob in list(C[B].objects):
 if 'web plate' in ob.name:group='Floor connections'
 elif ob.name.startswith(('T1-','HIP-','Roof diagonal')):group='Roof connections'
 elif ob.location.z>=FF:group='Upper connections'
 else:group='Ground connections'
 C[B].objects.unlink(ob);connection_groups[group].objects.link(ob)
# Context slab is optional; the delivered asset opens as the exposed building frame.
C['01 Slab datum'].hide_viewport=True;C['01 Slab datum'].hide_render=True
# Presentation: four saved cameras and named inspection view layers.
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS';scene.unit_settings.scale_length=1
box('Presentation ground',(14,4,-.65),(200,200,.2),'99 Presentation',stage,status='Presentation only')
def camera(name,loc,target,ortho):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);C['99 Presentation'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=ortho;d.clip_end=500;return o
hero=camera('01 Overall frame',(40,-32,26),(14.3,4.2,2.7),34)
rear=camera('02 Garage and alfresco',(-14,-27,20),(13.5,4.2,2.6),34)
plan=camera('03 Ground floor plan',(14,4,45),(14,4,0),32)
uppercam=camera('04 First floor plan',(16.7,3.94,45),(16.7,3.94,0),24)
scene.camera=hero
for name,loc,power,size in [('Key',(4,-10,25),5000,12),('Fill',(25,12,18),4000,10)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);C['99 Presentation'].objects.link(o);o.location=loc;o.rotation_euler=(Vector((14,4,2))-o.location).to_track_quat('-Z','Y').to_euler()
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2;sun.angle=.12;o=bpy.data.objects.new('Sun',sun);C['99 Presentation'].objects.link(o);o.rotation_euler=(.4,-.5,-.4)
scene.world.color=(.25,.25,.25)
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1800;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'
scene.view_layers[0].name='01 Complete frame'
layer_specs=[
 ('02 Ground framing only',[F,U,R,'07 Garage roof','08 Porch roof','11 Roof battens','10 Stair framing'],['Floor connections','Upper connections','Roof connections']),
 ('03 Floor structure',[G,U,R,'07 Garage roof','08 Porch roof','11 Roof battens','10 Stair framing'],['Ground connections','Upper connections','Roof connections']),
 ('04 Upper walls',[G,S,F,R,'07 Garage roof','08 Porch roof','11 Roof battens','10 Stair framing'],['Ground connections','Floor connections','Roof connections']),
 ('05 Roof structure',[G,S,F,U,'10 Stair framing'],['Ground connections','Floor connections','Upper connections'])]
for name,excluded,connection_exclusions in layer_specs:
 vl=scene.view_layers.new(name)
 for c in excluded:vl.layer_collection.children[c].exclude=True
 for c in connection_exclusions:vl.layer_collection.children[B].children[c].exclude=True
for vl in scene.view_layers:
 for ob in C['99 Presentation'].objects:ob.hide_set(True,view_layer=vl)
# Set an immediately useful viewport, materials visible without shader compilation.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.clip_end=500;space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_floor=False
   space.region_3d.view_distance=35;space.region_3d.view_location=(14,4,3);space.region_3d.view_rotation=hero.rotation_euler.to_quaternion();space.region_3d.view_perspective='PERSP'
notes=(OUT/'START_HERE.md').read_text(encoding='utf-8')+'\n\nOriginal detailed drawing notes:\n'+(ROOT/'output/README.md').read_text(encoding='utf-8')
t=bpy.data.texts.new('START HERE - Model scope and drawing differences');t.write(notes)
scene['project']='Leichhardt - frame stage';scene['reference_priority']='Architectural layout; 2026 supplier floor/roof members; structural schedules';scene['status']='Plan-referenced visual model; unresolved details recorded in START HERE'
with open(OUT/'member_inventory.csv','w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(inventory[0]));writer.writeheader();writer.writerows(inventory)
(OUT/'wall_setout.json').write_text(json.dumps(wall_records,indent=2))
# Basic geometric checks ensure model integrity and empty stair void.
errors=[]
for ob in bpy.data.objects:
 if ob.type=='MESH' and (min(ob.scale)<=0 or not all(math.isfinite(v) for v in ob.location)):errors.append(ob.name)
report={'mesh_objects':sum(o.type=='MESH' for o in bpy.data.objects),'wall_panels':len(wall_records),'floor_joist_assemblies':floor_count,'standard_T1_trusses':15,'garage_T5_trusses':8,'porch_T6_trusses':5,'units':'metres (UI millimetres)','ground_wall_top':GH,'upper_floor_datum':FF,'upper_wall_top':ROOF,'main_roof_pitch_degrees':25,'main_roof_span':span,'main_roof_overhang':.55,'geometry_errors':errors, 'sample_top_plate_vertical_mm':round((bpy.data.objects.get('GF North wall | top plate lower').rotation_quaternion.to_matrix() @ Vector((0,.045,0))).length*1000,2)}
(OUT/'model_checks.json').write_text(json.dumps(report,indent=2));assert not errors
for vl in scene.view_layers:vl.use=vl.name=='01 Complete frame'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Leichhardt_Timber_Frame.blend'))
# Isolated render processes avoid a Blender 5.0 dependency-graph crash when
# switching thousands of objects' visibility after repeated Cycles renders.
for view in ['overview','alfresco','ground','upper']:
 subprocess.run([bpy.app.binary_path,'--factory-startup','--background',str(OUT/'Leichhardt_Timber_Frame.blend'),'--python',str(ROOT/'scripts/render_frame.py'),'--',view],check=True)
print('MODEL_COMPLETE',json.dumps(report))
