"""Add provisional enclosure and learning assemblies without changing source frame geometry."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/enclosure';OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='Leichhardt_Timber_Frame_Stairs_Corrected.blend'
scene.name='01 Building - enclosure'
def signature(o):
 return {'matrix':[list(r) for r in o.matrix_world], 'vertices':[list(v.co) for v in o.data.vertices], 'polygons':[list(p.vertices) for p in o.data.polygons]}
original={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'}
config={'source':bpy.data.filepath,'frame_geometry_locked_for_review':True,
 'brick_leaf_mm':110,'cavity_mm':40,'upper_foam_mm':100,'plasterboard_mm':10,'floor_panel_mm':19,
 'roof_pitch_degrees':25,'roof_overhang_mm':550,'roof_sheet_display_mm':1,
 'visual_colours_only':True,'roof_profile':'schematic ribs; product unselected',
 'deferred':['full floor decking','garage and porch roof covering','D05 corner glazing','audit corrections']}
if (OUT/'ENCLOSURE_CONFIG.json').exists():
 previous=json.loads((OUT/'ENCLOSURE_CONFIG.json').read_text())
 for key in ['brick_leaf_mm','cavity_mm','upper_foam_mm','roof_pitch_degrees','roof_overhang_mm']:
  config[key]=previous.get(key,config[key])
(OUT/'ENCLOSURE_CONFIG.json').write_text(json.dumps(config,indent=2))
def collection(name,parent=None,owner=scene):
 c=bpy.data.collections.new(name);(parent or owner.collection).children.link(c);return c
groups={name:collection(name) for name in ['20 Main roof covering','21 Main roof sarking','22 Fascia and gutters','23 Ground brick veneer','24 Upper foam render','25 Wall wrap','26 Windows and doors','29 Enclosure cameras']}
parts={}
for name,c in groups.items():
 if name!='29 Enclosure cameras':parts[name]={s:collection(s,c) for s in ['Retained','Cutaway removal']}
def part(group,cut=False):return parts[group]['Cutaway removal' if cut else 'Retained']
def mat(name,color,metallic=0,roughness=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness;bs.inputs['Metallic'].default_value=metallic;return m
metal=mat('ENV Metal roof - colour unselected',(.095,.13,.15),.72,.36)
render=mat('ENV Foam render - colour unselected',(.77,.76,.69),0,.83)
brick=mat('ENV Brick veneer - colour unselected',(.35,.17,.10),0,.92)
wrap=mat('ENV Wall membrane - illustrative',(.16,.34,.32),0,.8)
sarking=mat('ENV Roof sarking - illustrative',(.48,.56,.6),.5,.5)
aluminium=mat('ENV Aluminium frames - illustrative',(.06,.075,.08),.7,.3)
glass=mat('ENV Glazing proxy',(.24,.48,.58),.12,.16)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.35
plaster=mat('ENV Plasterboard 10 mm',(.8,.79,.74),0,.95)
board=mat('ENV Floor board 19 mm',(.47,.30,.13),0,.86)
insulation=mat('ENV Insulation - no performance specification',(.64,.63,.32),0,1)
labelmat=mat('ENV Label ink',(.78,.84,.86),0,.8)
studybase=mat('ENV Assembly plinth',(.07,.10,.13),.1,.8)
wood=bpy.data.materials['MGP10 pine']
# Brick texture is illustrative, scaled in world coordinates to avoid panel stretching.
nt=brick.node_tree;bs=nt.nodes.get('Principled BSDF');geo=nt.nodes.new('ShaderNodeNewGeometry')
sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0])
add=nt.nodes.new('ShaderNodeMath');add.operation='ADD';nt.links.new(sep.outputs['X'],add.inputs[0]);nt.links.new(sep.outputs['Y'],add.inputs[1])
combine=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(add.outputs[0],combine.inputs['X']);nt.links.new(sep.outputs['Z'],combine.inputs['Y'])
tex=nt.nodes.new('ShaderNodeTexBrick');tex.inputs['Scale'].default_value=1;tex.inputs['Brick Width'].default_value=.23;tex.inputs['Row Height'].default_value=.086;tex.inputs['Mortar Size'].default_value=.008
tex.inputs['Color1'].default_value=(.33,.145,.08,1);tex.inputs['Color2'].default_value=(.47,.25,.15,1);tex.inputs['Mortar'].default_value=(.25,.245,.22,1)
nt.links.new(combine.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.25;bump.inputs['Distance'].default_value=.006;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
unit=bpy.data.meshes.new('ENV unit cube');unit.from_pydata([(-.5,-.5,-.5),(-.5,-.5,.5),(-.5,.5,-.5),(-.5,.5,.5),(.5,-.5,-.5),(.5,-.5,.5),(.5,.5,-.5),(.5,.5,.5)],[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);unit.update()
meshes={};new=[]
def box(name,loc,dims,col,material,source='Assembly study; see material register',basis='Illustrative component; final specification pending'):
 assert min(dims)>0
 if material.name not in meshes:
  m=unit.copy();m.materials.append(material);meshes[material.name]=m
 o=bpy.data.objects.new(name,meshes[material.name]);col.objects.link(o);o.location=loc;o.scale=dims
 o['source']=source;o['specification_status']=basis;new.append(o);return o
def beam(name,a,b,w,d,col,material):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,d,(b-a).length),col,material);o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y');return o
def surface(name,vertices,col,material,thick=.001):
 m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],[list(range(len(vertices)))]);m.update();m.materials.append(material)
 o=bpy.data.objects.new(name,m);col.objects.link(o);o['source']='Architectural 12; existing frame envelope';o['specification_status']='Provisional fit to current frame; sheet profile/gauge unselected';new.append(o)
 mod=o.modifiers.new('Visual layer thickness','SOLIDIFY');mod.thickness=thick;return o
# New skins track current top-plate endpoints, with opening coordinates from the baseline setout.
walls=json.loads((ROOT/'output/timber_frame/wall_setout.json').read_text())
outward={'GF North wall':(0,1),'GF East entry and bedroom':(1,0),'GF South family and suite':(0,-1),
 'GF Laundry west':(-1,0),'GF Laundry nook':(0,-1),'GF Nook return':(1,0),
 'Garage rear':(0,1),'Garage outer end':(-1,0),'Garage south':(0,-1),'Garage east upstand':(1,0),
 'FF North wall':(0,1),'FF South wall':(0,-1),'FF West wall':(-1,0),'FF East wall':(1,0)}
# The laundry shared wall is internal to the garage; no brick veneer there.
outward.pop('GF Laundry west')
openings_count=0
for rec in walls:
 name=rec['name']
 if name not in outward:continue
 ref=bpy.data.objects[name+' | top plate lower'];a=ref.matrix_world@Vector((0,0,-.5));b=ref.matrix_world@Vector((0,0,.5));a.z=rec['z'];b.z=rec['z']
 t=(b-a).normalized();L=(b-a).length;n=Vector((*outward[name],0));z=rec['z'];h=rec['h'];upper=z>1
 if name in ['GF North wall','GF East entry and bedroom','GF South family and suite']:h=3.14
 cut=(n.y<-.5) or name=='FF East wall'
 ops=rec['openings'];intervals=[(c-w/2,c+w/2,s,s+hh,tag) for tag,c,w,s,hh in ops]
 layers=[('25 Wall wrap',wrap,.001,.047)]
 skin=config['upper_foam_mm']/1000 if upper else config['brick_leaf_mm']/1000
 offset=.045+skin/2+(0 if upper else config['cavity_mm']/1000)
 layers.append(('24 Upper foam render',render,skin,offset) if upper else ('23 Ground brick veneer',brick,skin,offset))
 for group,material,thick,offset in layers:
  extension=offset+thick/2
  col=part(group,cut);cuts=sorted(set([-extension,L+extension]+[max(0,min(L,u)) for op in intervals for u in op[:2]]))
  for l,r in zip(cuts,cuts[1:]):
   mid=(l+r)/2;opening=next((op for op in intervals if op[0]<mid<op[1]),None)
   spans=[(0,h)] if opening is None else [(0,opening[2]),(opening[3],h)]
   for lo,hi in spans:
    if hi-lo<.002:continue
    ob=box(f'{name} | {group[3:]}',a+t*mid+n*offset+Vector((0,0,(lo+hi)/2)),(r-l,thick,hi-lo),col,material,
       'Architectural 07/08/11/12; current frame openings','Provisional fit. Audited positions unchanged; see Chris review list')
    ob.rotation_euler.z=math.atan2(t.y,t.x);ob['associated_frame']=name
 # Opening assets are grouped under named movable roots.
 for tag,c,w,s,hh in ops:
  openings_count+=1;col=part('26 Windows and doors',cut);root=bpy.data.objects.new('OPENING | '+tag,None);col.objects.link(root);root.empty_display_type='PLAIN_AXES';root.empty_display_size=.15
  root.location=a+t*c+n*.09+Vector((0,0,s));root.rotation_euler.z=math.atan2(t.y,t.x)
  root['source']='Architectural 11; CURRENT frame position';root['associated_frame']=name;root['status']='Provisional opening proxy'
  if tag.startswith('W04'):root['status']='HOLD FOR CHRIS: W04 sill is 514 mm above schedule; frame and proxy remain unchanged'
  def child(label,loc,dims,matl):
   ob=box(tag+' | '+label,(0,0,0),dims,col,matl,'Architectural 11','Illustrative frame/glazing sections; nominal opening, not manufacture sizes');ob.parent=root;ob.location=loc;return ob
  fw=.045
  child('left jamb',(-w/2+fw/2,0,hh/2),(fw,.06,hh),aluminium)
  child('right jamb',(w/2-fw/2,0,hh/2),(fw,.06,hh),aluminium)
  child('head',(0,0,hh-fw/2),(w,.06,fw),aluminium)
  child('sill',(0,0,fw/2),(w,.06,fw),aluminium)
  glazed=tag.startswith('W') or tag.startswith('D04')
  if glazed:
   panels=max(1,round(w/.95))
   for j in range(panels):
    pw=(w-2*fw)/panels;x=-w/2+fw+(j+.5)*pw
    child('glass',(x,0,hh/2),(pw-.015,.006,hh-2*fw),glass)
    if j>0:child('mullion',(x-pw/2,0,hh/2),(.035,.06,hh-2*fw),aluminium)
  else:
   child('door leaf',(0,.015,hh/2),(w-2*fw,.035,hh-2*fw),metal if tag.startswith('D03') else board)
   if tag.startswith('D03'):
    for j in range(1,6):child('section joint',(0,-.005,j*hh/6),(w-2*fw,.01,.014),aluminium)
   if tag.startswith('D01'):child('double-door meeting stile',(0,-.01,hh/2),(.012,.01,hh-2*fw),aluminium)
# Main hipped roof: four planes follow the unaltered roof envelope.
left,right=6.38,26.99;span=7.88;half=span/2;oh=config['roof_overhang_mm']/1000;k=math.tan(math.radians(config['roof_pitch_degrees']));base=5.73+.106
def rz(y,offset):return base+min(y,span-y)*k+offset
for group,material,offset in [('21 Main roof sarking',sarking,.091),('20 Main roof covering',metal,.113)]:
 ridge0=(left+half,half,rz(half,offset));ridge1=(right-half,half,rz(half,offset))
 faces=[('Near slope',[(left-oh,-oh,rz(-oh,offset)),(right+oh,-oh,rz(-oh,offset)),ridge1,ridge0],True),
        ('Far slope',[(right+oh,span+oh,rz(span+oh,offset)),(left-oh,span+oh,rz(span+oh,offset)),ridge0,ridge1],False),
        ('Garage hip',[(left-oh,span+oh,rz(span+oh,offset)),(left-oh,-oh,rz(-oh,offset)),ridge0],False),
        ('Entry hip',[(right+oh,-oh,rz(-oh,offset)),(right+oh,span+oh,rz(span+oh,offset)),ridge1],True)]
 for name,verts,cut in faces:surface(group[3:]+' | '+name,verts,part(group,cut),material)
for i in range(1,math.ceil((right-left+2*oh)/.30)):
 x=left-oh+i*.30;limit=min(half,x-left,right-x)
 if limit<=-oh:continue
 for far in [False,True]:
  y0,y1=(span+oh,span-limit) if far else (-oh,limit)
  beam('Main roof | schematic sheet rib',(x,y0,rz(y0,.127)),(x,y1,rz(y1,.127)),.018,.012,part('20 Main roof covering',not far),metal)
for x,sign in [(left,1),(right,-1)]:
 for i in range(1,math.ceil((span+2*oh)/.30)):
  y=-oh+i*.30;d=min(y,span-y)
  if d<=-oh:continue
  beam('Hip roof | schematic sheet rib',(x-sign*oh,y,base-oh*k+.127),(x+sign*d,y,base+d*k+.127),.018,.012,part('20 Main roof covering',sign<0),metal)
edges=[((left-oh,-oh),(right+oh,-oh),True),((right+oh,span+oh),(left-oh,span+oh),False),((left-oh,span+oh),(left-oh,-oh),False),((right+oh,-oh),(right+oh,span+oh),True)]
eavez=base-oh*k+.10
for a,b,cut in edges:
 col=part('22 Fascia and gutters',cut);t=(Vector(b)-Vector(a)).normalized();n=Vector((t.y,-t.x))
 beam('Fascia | main roof',(*a,eavez-.075),(*b,eavez-.075),.025,.16,col,metal)
 for label,out,z,w,d in [('gutter base',.07,eavez-.12,.14,.008),('gutter outer lip',.14,eavez-.065,.008,.11)]:
  aa=Vector(a)+n*out;bb=Vector(b)+n*out;beam(label,(*aa,z),(*bb,z),w,d,col,metal)
# Flashings remain schematic strips.
beam('Main ridge cap',(left+half,half,rz(half,.135)),(right-half,half,rz(half,.135)),.16,.015,part('20 Main roof covering'),metal)
for x,y,ridge,cut in [(left-oh,-oh,left+half,True),(left-oh,span+oh,left+half,False),(right+oh,-oh,right-half,True),(right+oh,span+oh,right-half,False)]:
 beam('Hip flashing',(x,y,eavez+.035),(ridge,half,rz(half,.135)),.12,.012,part('20 Main roof covering',cut),metal)
def camera(name,loc,target,scale,col,owner=scene):
 d=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,d);col.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;d.clip_end=500;return ob
hero=camera('ENV Camera - enclosure',(40,-32,25),(14.3,4.2,2.6),34,groups['29 Enclosure cameras'])
scene.camera=hero
for vl in scene.view_layers:
 for name in groups:vl.layer_collection.children[name].exclude=True
for name in ['06 Enclosure - cutaway','07 Enclosure - assembled','08 Enclosure - wrap stage']:
 vl=scene.view_layers.new(name)
 for group in groups:
  node=vl.layer_collection.children[group]
  if name=='08 Enclosure - wrap stage' and group not in ['21 Main roof sarking','25 Wall wrap','29 Enclosure cameras']:node.exclude=True
  if name=='06 Enclosure - cutaway' and group!='29 Enclosure cameras':node.children[parts[group]['Cutaway removal'].name].exclude=True
 for ob in bpy.data.collections['99 Presentation'].objects:ob.hide_set(True,view_layer=vl)
 for ob in groups['29 Enclosure cameras'].objects:ob.hide_set(True,view_layer=vl)
 vl.use=name=='06 Enclosure - cutaway'
for vl in scene.view_layers:
 if not vl.name.startswith(('06 ','07 ','08 ')):vl.use=False
bpy.context.window.view_layer=scene.view_layers['06 Enclosure - cutaway']
scene.render.resolution_x=1800;scene.render.resolution_y=1100;scene.cycles.samples=32
# Separate assembly scene, with its own geometry and labels.
study=bpy.data.scenes.new('02 Assembly studies');sc=collection('Assembly examples',owner=study)
def textobj(body,loc,size=.18):
 d=bpy.data.curves.new(body,'FONT');d.body=body;d.size=size;d.extrude=.001;d.materials.append(labelmat)
 ob=bpy.data.objects.new(body,d);sc.objects.link(ob);ob.location=loc;ob.rotation_euler.x=math.pi/2;return ob
def studypanel(x,upper=False):
 # Layers explode toward the back of the sample; timber retains its actual 90 mm section.
 box('Study plasterboard 10 mm',(x-.7,0,1.6),(.7,.01,2.2),sc,plaster,'Architectural 12','Specified 10 mm; partial cutaway panel in exploded position')
 for xx in [x-1.0,x-.5,x,x+.5,x+1.0]:box('Study wall stud',(xx,.48,1.6),(.045,.09,2.2),sc,wood)
 for zz in [.52,1.6,2.68]:box('Study timber plate/nogging',(x,.48,zz),(2.1,.09,.045),sc,wood)
 for xx in [x-.75,x-.25,x+.25,x+.75]:box('Study insulation',(xx,.48,1.1),(.42,.07,1.02),sc,insulation)
 box('Study wall wrap',(x+.55,.90,1.6),(1.0,.001,2.2),sc,wrap)
 box('Study external skin',(x,1.30,1.6),(2.1,.10 if upper else .11,2.2),sc,render if upper else brick,
     'Architectural 12','100 mm foam specified' if upper else '110 mm leaf assumed; 40 mm cavity assumed')
for x,title in [(1.5,'01 / BRICK VENEER'),(6.5,'02 / FOAM + RENDER'),(11.5,'03 / METAL ROOF'),(16.5,'04 / FLOOR')]:
 box('Assembly plinth',(x,.6,.12),(4.5,3.7,.24),sc,studybase)
 textobj(title,(x-2.1,-1.31,.12),.25)
studypanel(1.5);studypanel(6.5,True)
textobj('10 mm lining / 90 mm frame\nWrap / cavity / brick*',( -.6,-1.31,-.46),.17)
textobj('10 mm lining / 90 mm frame\nWrap / 100 mm foam + render',(4.4,-1.31,-.46),.17)
# Roof sample: timber rafters, battens, raised membrane and metal plane.
for xx in [10.5,11.0,11.5,12.0,12.5]:beam('Study rafter',(xx,-.1,.7),(xx,1.9,.7+2*k),.045,.14,sc,wood)
for yy in [0,.65,1.3,1.9]:beam('Study roof batten',(10.4,yy,.8+(yy+.1)*k),(12.6,yy,.8+(yy+.1)*k),.045,.035,sc,wood)
for material,raisez,title,xmin in [(sarking,.28,'Sarking',10.95),(metal,.58,'Metal roof',11.5)]:
 surface('Study '+title,[(xmin,-.1,.8+raisez),(12.6,-.1,.8+raisez),(12.6,1.9,.8+2*k+raisez),(xmin,1.9,.8+2*k+raisez)],sc,material)
for xx in [11.55+i*.30 for i in range(4)]:beam('Study roof rib',(xx,-.1,1.395),(xx,1.9,1.395+2*k),.018,.012,sc,metal)
textobj('Timber / battens / sarking\nSelected Colorbond; profile TBC',(9.4,-1.31,-.46),.17)
# Floor sample depicts supplier depth without changing the house floor datum.
for xx in [15.5,16.0,16.5,17.0,17.5]:
 for zz in [.7225,1.0905]:beam('Study floor chord',(xx,-.1,zz),(xx,1.9,zz),.09,.045,sc,wood)
 for i in range(4):beam('Study metal web',(xx,-.1+i*.5,.75 if i%2==0 else 1.06),(xx,.4+i*.5,1.06 if i%2==0 else .75),.012,.026,sc,aluminium)
box('Study ceiling 10 mm',(16.5,.9,.40),(2.2,2.0,.01),sc,plaster)
for yy in [.35,1.35]:box('Study floor panel 19 mm',(15.95,yy,1.37),(1.1,.9,.019),sc,board,'Supplier floor layout page 47','Specified thickness; 1100 x 900 cropped sample of 3600 x 900 panel product')
textobj('413 mm supplier joist / 19 mm board\nHouse floor depth awaits Chris',(14.4,-1.31,-.46),.17)
textobj('LEICHHARDT / ENCLOSURE ASSEMBLIES',(-.6,1.8,3.65),.43)
textobj('Exploded cutaway examples | colours and products unselected',(-.6,1.8,3.18),.22)
textobj('* Brick leaf and cavity split illustrative. Insulation performance unselected.',(-.6,-1.31,-.88),.18)
study.camera=camera('ENV Camera - assemblies',(9,-26,16),(9,.6,1.1),21,sc,study)
study.world=scene.world.copy();study.render.engine='CYCLES';study.cycles.samples=32;study.cycles.use_denoising=True
study.render.resolution_x=2200;study.render.resolution_y=1000;study.render.resolution_percentage=100;study.view_settings.view_transform='AgX'
for name,loc,power,size in [('Study key',(6,-5,12),3000,10),('Study fill',(15,5,10),2000,8)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);sc.objects.link(o);o.location=loc;o.rotation_euler=(Vector((9,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
sun=bpy.data.lights.new('Study sun','SUN');sun.energy=1.3;o=bpy.data.objects.new('Study sun',sun);sc.objects.link(o);o.rotation_euler=(.4,-.4,-.3)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.color_type='MATERIAL';sp.region_3d.view_location=(14,4,3);sp.region_3d.view_distance=35;sp.region_3d.view_rotation=hero.rotation_euler.to_quaternion()
notes=(OUT/'ENCLOSURE_NOTES.md').read_text(encoding='utf-8');t=bpy.data.texts.new('START HERE - Enclosure preparation');t.write(notes)
scene['enclosure_status']='PROVISIONAL study - frame positions await Chris';study['scope']='Detached teaching assemblies; no final product selection'
bpy.context.view_layer.update()
assert all(signature(bpy.data.objects[name])==value for name,value in original.items()),'Source frame geometry changed'
bad=[o.name for o in new if not all(math.isfinite(v) for row in o.matrix_world for v in row) or min(o.scale)<=0]
assert not bad
checks={'source_meshes_unchanged':len(original),'new_components':len(new),'opening_proxies':openings_count,
        'main_scene':scene.name,'assembly_scene':study.name,'invalid_new_transforms':bad,
        'deferred':config['deferred'],'status':'PASS: source geometry preservation and new geometry checks'}
(OUT/'ENCLOSURE_CHECKS.json').write_text(json.dumps(checks,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Leichhardt_Enclosure_Study.blend'))
print(json.dumps(checks,indent=2))
