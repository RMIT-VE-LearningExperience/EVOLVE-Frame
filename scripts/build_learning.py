"""Detached teaching junctions, staged views and batched web exports. Never edit the house."""
import bpy, math, json, hashlib
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/learning'; OUT.mkdir(parents=True,exist_ok=True)
WEB=ROOT/'student-web/public/models'; WEB.mkdir(parents=True,exist_ok=True)
assert Path(bpy.data.filepath).name=='Leichhardt_Enclosure_Study.blend'
house=bpy.data.scenes['01 Building - enclosure']
def sig(o):
 return hashlib.sha256(repr(([list(r) for r in o.matrix_world],[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
original={o.name:sig(o) for o in bpy.data.objects if o.type=='MESH'}
def material(name,color,metallic=0):
 m=bpy.data.materials.new('LEARN '+name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.6;p.inputs['Metallic'].default_value=metallic;return m
mats={k:material(k,c,m) for k,c,m in [('timber',(.55,.34,.15),0),('brick',(.46,.20,.11),0),('foam',(.8,.80,.74),0),('wrap',(.08,.45,.39),0),('flashing',(.93,.59,.12),.4),('metal',(.17,.24,.28),.6),('glass',(.20,.48,.63),.25),('lining',(.78,.81,.83),0),('floor',(.5,.36,.18),0),('water',(.08,.65,.85),.2)]}
unit=bpy.data.meshes.new('LEARN unit cube');unit.from_pydata([(-.5,-.5,-.5),(-.5,-.5,.5),(-.5,.5,-.5),(-.5,.5,.5),(.5,-.5,-.5),(.5,-.5,.5),(.5,.5,-.5),(.5,.5,.5)],[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);unit.update()
templates={};scenes={};parts={};active=None
def make_scene(key,title):
 global active
 s=bpy.data.scenes.new(title);s.world=house.world.copy();s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
 s.render.resolution_x=1500;s.render.resolution_y=1300;s.render.resolution_percentage=100
 s['status']='Illustrative detached teaching detail. No construction dimensions or compliance approval.'
 s['web_key']=key;s.frame_start=1;s.frame_end=100
 scenes[key]=s;parts[key]={};active=key;return s
def part(key,label,mat,ex=(0,0,0),note='Illustrative relationship; product and installation detail to be confirmed.'):
 c=bpy.data.collections.new(label);scenes[active].collection.children.link(c)
 c['key']=key;c['label']=label;c['note']=note;c['explode']=list(ex);c['material']=mat;parts[active][key]=c;return c
def box(c,loc,dims,name=None):
 mat=mats[c['material']]
 if mat.name not in templates:
  me=unit.copy();me.materials.append(mat);templates[mat.name]=me
 o=bpy.data.objects.new(name or c['label'],templates[mat.name]);c.objects.link(o);o.location=loc;o.scale=dims
 o['part']=c['key'];o['label']=c['label'];o['note']=c['note'];o['explode']=list(c['explode']);return o
def beam(c,a,b,w,d):
 a,b=Vector(a),Vector(b);o=box(c,(a+b)/2,(w,d,(b-a).length));o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y');return o
def sheet(c,x0,x1,profile):
 verts=[(x,y,z) for x in [x0,x1] for y,z in profile];n=len(profile)
 faces=[(i,i+1,n+i+1,n+i) for i in range(n-1)]
 me=bpy.data.meshes.new(c['label']);me.from_pydata(verts,[],faces);me.materials.append(mats[c['material']]);me.update()
 o=bpy.data.objects.new(c['label'],me);c.objects.link(o);o['part']=c['key'];o['label']=c['label'];o['note']=c['note'];o['explode']=list(c['explode'])
 mod=o.modifiers.new('Illustrative sheet thickness','SOLIDIFY');mod.thickness=.003;return o
def wall_frame(c,z0,z1,width=2.1):
 for x in [-width/2,0,width/2]:box(c,(x,0,(z0+z1)/2),(.045,.09,z1-z0))
 for z in [z0+.023,z1-.023]:box(c,(0,0,z),(width+.045,.09,.045))
def lighting(s):
 c=bpy.data.collections.new(s.name+' | presentation');s.collection.children.link(c)
 d=bpy.data.cameras.new(s.name+' camera');o=bpy.data.objects.new(d.name,d);c.objects.link(o)
 o.location=(4,-6,3.7);target=Vector((0,-.1,1.35));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=4.7;s.camera=o
 for loc,power,size in [((1,-5,7),1000,5),((-3,2,5),1200,4)]:
  d=bpy.data.lights.new('Junction softbox','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);c.objects.link(o);o.location=loc;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 s.timeline_markers.new('ASSEMBLED - illustrative',frame=1);s.timeline_markers.new('EXPLODED - not installation gaps',frame=100)
def animate(key):
 for c in parts[key].values():
  for o in c.objects:
   start=o.location.copy();o.keyframe_insert(data_path='location',frame=1);o.location=start+Vector(o['explode']);o.keyframe_insert(data_path='location',frame=100);o.location=start
 scenes[key].frame_set(1)

# Window sample is NOT W04: dimensions are solely for teaching composition.
make_scene('window','03 Junction - window')
c=part('frame','01 Timber rough opening','timber',note='Generic rough opening, not an engineered lintel or a scheduled house window.')
for x in [-1.05,-.65,.65,1.05]:box(c,(x,0,1.25),(.045,.09,2.5))
for z in [.025,.735,1.965,2.475]:box(c,(0,0,z),(2.145,.09,.045 if z!=1.965 else .09))
for x in [-.32,.32]:
 box(c,(x,0,.38),(.045,.09,.665));box(c,(x,0,2.23),(.045,.09,.44))
c=part('wrap','02 Wall wrap around opening','wrap',(0,-.28,0),'Generic drainage layer. Opening integration and membrane selection follow the selected wall/window system.')
for x in [-.89,.89]:box(c,(x,-.048,1.25),(.32,.003,2.5))
box(c,(0,-.048,.33),(1.46,.003,.66));box(c,(0,-.048,2.28),(1.46,.003,.44))
c=part('sill','03 Sill flashing with upstand','flashing',(0,-.55,-.10),'Conceptual outward drainage and upstand. End dams, laps and dimensions require a system-specific detail.')
sheet(c,-.75,.75,[(-.035,.85),(-.035,.735),(-.24,.705),(-.24,.675)])
for x in [-.75,.75]:box(c,(x,-.14,.758),(.003,.21,.065),'Sill end upstand - illustrative')
c=part('jamb','04 Jamb flashing','flashing',(.15,-.65,0),'Show jamb flashing overlapping sill flashing. Final folds, laps and fixing-fin arrangement are product-specific.')
for x in [-.665,.665]:box(c,(x,-.1,1.32),(.14,.004,1.23))
c=part('window','05 Window and glazing','metal',(0,-.9,0),'Generic aluminium window proxy. Fixings, packers, clearances, drainage slots and glass specification are not designed.')
for x in [-.595,.595]:box(c,(x,-.13,1.32),(.05,.065,1.12))
for z in [.785,1.855]:box(c,(0,-.13,z),(1.24,.065,.05))
glasspart=part('glass','06 Glazing','glass',(0,-.95,0));box(glasspart,(0,-.13,1.32),(1.14,.008,1.02))
c=part('head','07 Head flashing','flashing',(0,-.5,.22),'Conceptual head flashing beneath the upper wrap, projecting outwards. Extension, fall and end treatment require confirmation.')
sheet(c,-.77,.77,[(-.04,2.15),(-.04,1.955),(-.24,1.93),(-.24,1.9)])
c=part('brick','08 Brick veneer cutaway','brick',(0,-1.18,0),'110 mm brick leaf and 40 mm nominal cavity are model assumptions. Partial skin exposes the opening layers.')
box(c,(-.95,-.145,1.3),(.19,.11,2.4));box(c,(0,-.145,.3),(2.1,.11,.6));box(c,(.4,-.145,2.34),(1.3,.11,.3))
c=part('lining','09 Internal lining cutaway','lining',(0,.38,0),'10 mm plasterboard is noted on architectural sheet 12. Seals and reveal finish remain schematic.');box(c,(-.92,.055,1.25),(.3,.01,2.5))
lighting(scenes['window']);animate('window')

make_scene('eaves','04 Junction - wall to roof')
c=part('frame','01 Wall and roof timber','timber',note='Generic eaves slice, not a supplier truss or an approved bearing/connection detail.');wall_frame(c,0,2.3)
k=math.tan(math.radians(25))
for x in [-1.05,0,1.05]:beam(c,(x,-.65,2.32),(x,1.0,2.32+1.65*k),.045,.14)
c=part('wrap','02 Wall wrap','wrap',(0,-.22,0));box(c,(0,-.048,1.1),(2.1,.003,2.2))
c=part('cladding','03 Upper foam/render cutaway','foam',(0,-.5,0),'100 mm foam with rendered finish follows architectural notes. Approved system, top termination and fixings remain unselected.');box(c,(-.65,-.095,1.12),(.8,.1,2.24))
c=part('battens','04 Roof battens','timber',(0,0,.22),'Batten sections and spacings here are illustrative, not a fixing schedule.')
for y in [-.6,0,.6,1]:box(c,(0,y,2.41+(y+.65)*k),(2.15,.045,.035))
c=part('sarking','05 Roof sarking','wrap',(0,0,.48),'Secondary drainage layer shown toward the eaves. Final support, laps, ventilation and gutter termination require the chosen roof-system detail.')
sheet(c,-.85,1.05,[(-.70,2.415), (1.0,2.415+1.7*k)])
c=part('roof','06 Metal roof cutaway','metal',(0,0,.76),'25 degree main pitch from the drawings. Profile, gauge and eaves projection are schematic.')
sheet(c,-.3,1.05,[(-.73,2.445), (1.0,2.445+1.73*k)])
for x in [-.25,.05,.35,.65,.95]:beam(c,(x,-.73,2.46),(x,1.0,2.46+1.73*k),.014,.012)
c=part('fascia','07 Fascia','metal',(0,-.45,0),'Fascia profile and fixing detail are unselected.');box(c,(0,-.66,2.25),(2.15,.025,.18))
c=part('gutter','08 Open gutter channel','metal',(0,-.82,0),'Conceptual collection channel only. Capacity, fall, outlets, overflow provision and downpipes are not designed.')
box(c,(0,-.79,2.13),(2.15,.20,.008))
for y in [-.89,-.69]:box(c,(0,y,2.205),(2.15,.008,.15))
c=part('soffit','09 Soffit cutaway','lining',(0,0,-.28),'Soffit lining shown as a relationship study. Product, thickness and roof ventilation design require confirmation.');box(c,(-.65,-.33,2.12),(.8,.62,.008))
lighting(scenes['eaves']);scenes['eaves'].camera.data.ortho_scale=5.8
scenes['eaves'].camera.rotation_euler=(Vector((0,-.1,1.85))-scenes['eaves'].camera.location).to_track_quat('-Z','Y').to_euler()
animate('eaves')

make_scene('floor-edge','05 Junction - floor edge')
c=part('frame','01 Upper and lower wall frame','timber',note='Detached floor-edge sample. The house floor datum remains unchanged.');wall_frame(c,0,1.0);wall_frame(c,1.413,2.55)
c=part('joists','02 Floor-edge structural zone','timber',(.0,.30,0),'413 mm supplier zone is used ONLY in this sample. Architecture shows 400 mm. Chris must resolve the conflict before fitting the house deck.')
box(c,(0,0,1.2065),(2.145,.09,.413))
for x in [-.8,0,.8]:
 for z in [1.0225,1.3905]:box(c,(x,.6,z),(.09,1.1,.045))
c=part('deck','03 Floor sheeting cutaway','floor',(0,0,.25),'19 mm panel thickness from supplier layout page 47. Sample size and edge support are illustrative.');box(c,(-.55,.5,1.4225),(1,1.1,.019))
c=part('wrap','04 Wall wrap across transition','wrap',(0,-.27,0),'Continuity is a design question at this transition. Final laps, air barrier and drainage path need coordinated wall-system details.');box(c,(0,-.048,1.25),(2.1,.003,2.5))
c=part('brick','05 Lower brick veneer cutaway','brick',(0,-.9,0),'110 mm brick leaf / 40 mm cavity split is assumed. Masonry support and movement allowances are not resolved.');box(c,(-.5,-.145,.56),(1.1,.11,1.12))
c=part('transition','06 Transition flashing concept','flashing',(0,-.52,0),'A conceptual outward-draining flashing beneath the upper system. Do not use these folds or dimensions for installation.')
sheet(c,-1.05,1.05,[(-.04,1.43),(-.04,1.24),(-.23,1.20),(-.23,1.16)])
c=part('foam','07 Upper foam/render cutaway','foam',(0,-.7,.12),'100 mm foam noted in the architecture. A compatible termination, movement joint, drainage and fixing system remain to be selected.');box(c,(.45,-.095,1.98),(1.2,.1,1.08))
c=part('lining','08 Ceiling and wall lining','lining',(0,.45,-.1),'10 mm plasterboard from architectural sheet 12. Junction and service coordination not completed.');box(c,(-.7,.4,.975),(.7,.8,.01))
lighting(scenes['floor-edge']);animate('floor-edge')

# Add a four-step presentation sequence without touching model geometry.
bpy.context.window.scene=house
stage_roots={'roof':['20 Main roof covering','22 Fascia and gutters'],'wrap':['21 Main roof sarking','25 Wall wrap'],'cladding':['23 Ground brick veneer','24 Upper foam render','26 Windows and doors']}
all_roots=sum(stage_roots.values(),[])
for number,label,shown in [(1,'Frame',[]),(2,'Wrap',stage_roots['wrap']),(3,'Cladding',stage_roots['wrap']+stage_roots['cladding']),(4,'Roof',all_roots)]:
 vl=house.view_layers.new(f'LEARN {number:02d} - {label}')
 for name in all_roots:vl.layer_collection.children[name].exclude=name not in shown
 vl.use=False
house['learning_sequence']='Frame > Wrap > Cladding > Roof is a teaching reveal order, not a prescribed site programme.'

# Batched meshes keep the web viewer light. No original objects are edited or exported with private file metadata.
manifest={'status':'Provisional teaching model; not a construction specification','models':{},'source_meshes_preserved':len(original)}
def export_batches(key,source,classified):
 bpy.context.window.scene=source;source.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
 batches={}
 for o,meta in classified:
  if o.type!='MESH':continue
  ev=o.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles()
  for mi in set(p.material_index for p in mesh.polygons):
   source_material=mesh.materials[mi] if mi<len(mesh.materials) and mesh.materials[mi] else mats['timber']
   batchkey=(meta['key'],source_material.name,meta.get('cut',False))
   batch=batches.setdefault(batchkey,{'vertices':[],'faces':[],'meta':meta,'material':source_material})
   offset=len(batch['vertices']);batch['vertices'].extend([tuple(round(v,6) for v in (o.matrix_world@vert.co)) for vert in mesh.vertices])
   batch['faces'].extend([tuple(offset+i for i in tri.vertices) for tri in mesh.loop_triangles if tri.material_index==mi])
  ev.to_mesh_clear()
 export=bpy.data.scenes.new('TEMP WEB '+key);bpy.context.window.scene=export
 for (label,matname,cut),batch in batches.items():
  me=bpy.data.meshes.new(label);me.from_pydata(batch['vertices'],[],batch['faces']);me.update()
  # Web materials use diffuse values; procedural brick/wood nodes remain in Blender only.
  src=batch['material'];simple=material_cache.get(src.name)
  if not simple:
   simple=material('Web '+src.name,tuple(src.diffuse_color[:3]),.25 if 'metal' in src.name.lower() else 0);material_cache[src.name]=simple
  me.materials.append(simple);o=bpy.data.objects.new(label+(' cut' if cut else ''),me);export.collection.objects.link(o)
  for k,v in batch['meta'].items():o[k]=v
 bpy.ops.export_scene.gltf(filepath=str(WEB/(key+'.glb')),export_format='GLB',use_active_scene=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_apply=True)
 manifest['models'][key]={'file':key+'.glb','batches':len(batches),'triangles':sum(len(b['faces']) for b in batches.values()),'bytes':(WEB/(key+'.glb')).stat().st_size,'parts':list({b['meta']['key']:b['meta'] for b in batches.values()}.values())}
 bpy.context.window.scene=source;bpy.data.scenes.remove(export)
material_cache={}
classified=[]
def descend(col,top,cut=False):
 cut=cut or col.name.startswith('Cutaway removal')
 for o in col.objects:
  if o.type=='MESH':classified.append((o,{'key':top.name,'label':top.name[3:],'stage':0 if int(top.name[:2])<20 else 1 if top.name[:2] in ['21','25'] else 2 if top.name[:2] in ['23','24','26'] else 3,'cut':cut,'note':'Current saved model. Audited discrepancies remain unresolved.','explode':[0,0,0]}))
 for child in col.children:descend(child,top,cut)
for col in house.collection.children:
 if col.name[:2].isdigit() and 2<=int(col.name[:2])<=26:descend(col,col)
export_batches('building',house,classified)
for key,s in scenes.items():
 export_batches(key,s,[(o,{'key':c['key'],'label':c['label'],'note':c['note'],'explode':list(c['explode']),'stage':0,'cut':False}) for c in parts[key].values() for o in c.objects])
lighting_names=[s.name for s in scenes.values()]
bpy.context.window.scene=house;house.frame_set(1);bpy.context.view_layer.update()
assert all(sig(bpy.data.objects[n])==h for n,h in original.items()),'Original mesh changed'
manifest['checks']={'source_geometry':'unchanged','junction_count':len(scenes),'building_batches':manifest['models']['building']['batches'],'web_materials':'Simplified colours, not product selections'}
(WEB/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'LEARNING_CHECKS.json').write_text(json.dumps(manifest['checks'],indent=2),encoding='utf-8')
notes=ROOT/'output/learning/LEARNING_GUIDE.md'
if notes.exists():t=bpy.data.texts.new('START HERE - Learning junctions');t.write(notes.read_text(encoding='utf-8'))
bpy.context.window.view_layer=house.view_layers['06 Enclosure - cutaway']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Leichhardt_Learning_Experience.blend'))
print('LEARNING COMPLETE',json.dumps(manifest['checks']))
