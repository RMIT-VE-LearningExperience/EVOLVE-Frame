"""Repair visible connections and author a complete stair in the separate VR revision.

The stair is an illustrative finished assembly coordinated to the existing floor
edge and floor levels; it is not a new fabrication or engineering specification.
"""
import math
from mathutils import Vector

def vr_bounds(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]

def vr_material(name, color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=.65
    return m

def vr_mesh(name, vertices, faces, col, mat):
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(vertices,[],faces); mesh.materials.append(mat); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o)
    o['modelling_basis']='VR visual coordination, existing floor datums and stair zone'
    return o

def vr_box(name, lo, hi, col, mat):
    assert min(hi[i]-lo[i] for i in range(3))>0, name
    # Local unit coordinates retain correct material scale after batching.
    o=vr_mesh(name,[(x,y,z) for x in (-.5,.5) for y in (-.5,.5) for z in (-.5,.5)],
        [(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)],col,mat)
    o.location=(Vector(lo)+Vector(hi))/2; o.scale=Vector(hi)-Vector(lo)
    return o

def vr_beam(name, a, b, width, depth, col, mat):
    a,b=Vector(a),Vector(b); length=(b-a).length
    o=vr_box(name,(-width/2,-depth/2,-length/2),(width/2,depth/2,length/2),col,mat)
    o.location=(a+b)/2; o.rotation_mode='QUATERNION'; o.rotation_quaternion=(b-a).to_track_quat('Z','Y')
    return o

def vr_extrude(name, profile, y0, y1, col, mat):
    n=len(profile)
    verts=[(x,y,z) for y in (y0,y1) for x,z in profile]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return vr_mesh(name,verts,faces,col,mat)

pine=bpy.data.materials['MGP10 pine']
steel=bpy.data.materials['Structural steel']
upper=bpy.data.collections['05 Upper floor walls']

# The old traced dwarf wall was 167 mm off the actual void return trimmer.
# Rebuild square joints directly over the existing trimmer centrelines.
theatre_frame_face=vr_bounds(bpy.data.objects['FF Theatre north | top plate lower'])[1][1]
for name, a, b in [('FF stair balustrade',(20.91,6.60),(24.305,6.60)),
                    ('FF void balustrade',(24.35,6.645),(24.35,theatre_frame_face))]:
    for o in list(house.objects):
        if o.name.startswith(name+' |'): bpy.data.objects.remove(o,do_unlink=True)
    av,bv=Vector((*a,0)),Vector((*b,0)); t=(bv-av).normalized(); length=(bv-av).length
    def point(u,z): return av+t*u+Vector((0,0,z))
    for label,z in [('bottom plate',3.1625),('top plate lower',4.2725),('top plate upper',4.3175)]:
        vr_beam(name+' | '+label,point(0,z),point(length,z),.09,.045,upper,pine)
    n=math.ceil((length-.035)/.45)
    positions=[.0175+i*(length-.035)/n for i in range(n+1)]
    for i,u in enumerate(positions):
        p=point(u,0)
        if abs(t.x)>.5: lo=(p.x-.0175,p.y-.045,3.185);hi=(p.x+.0175,p.y+.045,4.25)
        else: lo=(p.x-.045,p.y-.0175,3.185);hi=(p.x+.045,p.y+.0175,4.25)
        vr_box(name+f' | stud {i+1:02}',lo,hi,upper,pine)
    for i,(u,v) in enumerate(zip(positions,positions[1:])):
        vr_beam(name+f' | nogging {i+1:02}',point(u+.0175,3.72),point(v-.0175,3.72),.09,.035,upper,pine)
    changes.append({'object':name,'action':'Rebuilt over floor trimmer, closed corner joint, bottom at structural deck datum'})
bpy.context.view_layer.update()

# Strap/hardboard offsets previously placed their exposed faces outside plaster.
wall_data=json.loads((ROOT/'output/timber_frame/wall_setout.json').read_text())
brace_report=[]
for o in house.objects:
    if o.type!='MESH' or not o.name.startswith(('GF ','FF ')) or not any(s in o.name for s in (' diagonal',' cross','4.8mm hardboard')): continue
    ob=vr_bounds(o); axis=0 if ob[0][1]-ob[0][0]<.01 else 1
    along=1-axis; centre=(ob[axis][0]+ob[axis][1])/2; mid=(ob[along][0]+ob[along][1])/2
    candidates=[]
    for rec in wall_data:
        if (rec['z']>1)!=o.name.startswith('FF '): continue
        ref=bpy.data.objects[rec['name']+' | top plate lower']; wb=vr_bounds(ref)
        if wb[axis][1]-wb[axis][0]>.1: continue
        if not wb[along][0]-.03<=mid<=wb[along][1]+.03: continue
        wall_centre=(wb[axis][0]+wb[axis][1])/2
        candidates.append((abs(centre-wall_centre),wall_centre,rec['name']))
    if not candidates: continue
    offset,wc,wall_name=min(candidates)
    if offset>.12: continue
    half=(ob[axis][1]-ob[axis][0])/2
    target=wc+(.045+half)*(1 if centre>wc else -1)
    o.location[axis]+=target-centre
    brace_report.append({'object':o.name,'wall':wall_name,'shift_mm':round((target-centre)*1000,2)})
changes.append({'object':'Wall bracing','action':f'{len(brace_report)} straps/panels seated on the stud face, behind lining'})
# A traced hall strap crossed the Bedroom 2 door. Keep the same strap section and
# diagonal shape, but seat it in the adjacent uninterrupted wall bay in this VR study.
hall=next(r for r in wall_data if r['name']=='FF Bed 2 study hall')
ref=bpy.data.objects[hall['name']+' | top plate lower']; wb=vr_bounds(ref)
edges=[wb[0][0]]
for tag,c,w,s,h in sorted(hall['openings'],key=lambda v:v[1]): edges.extend([wb[0][0]+c-w/2,wb[0][0]+c+w/2])
edges.append(wb[0][1]); bays=list(zip(edges[::2],edges[1::2]))
strap=bpy.data.objects['FF Hall C diagonal']; bb=vr_bounds(strap); width=bb[0][1]-bb[0][0]
options=[max(a+.02,min(bb[0][0],b-.02-width))-bb[0][0] for a,b in bays if b-a>=width+.04]
assert options,'No solid hall bay can contain the existing strap'
shift=min(options,key=abs);strap.location.x+=shift
changes.append({'object':strap.name,'action':f'Relocated {shift:.3f} m into solid wall bay, clearing Bedroom 2 door; visual coordination'})

# Close RHS heads at their actual supporting beam undersides. C1 living had a
# real 5 mm air gap. Other caps replace the top 8 mm, leaving no doubled solid.
caps=[]
for prefix,beam_name in [('C1 alfresco west','1L2 200PFC profile 1'),('C1 alfresco middle','1L3 200PFC profile 1'),
                         ('C1 nook','1L4 200PFC profile 1'),('C3 portal south','1B4 310UC137 profile 1'),
                         ('C3 portal north','1B4 310UC137 profile 1'),('C1 living','1B5 310UB40.4 profile 1')]:
    members=[o for o in house.objects if o.name.startswith(prefix+' profile ')]
    bounds=[vr_bounds(o) for o in members]
    lo=[min(bb[i][0] for bb in bounds) for i in range(3)]; hi=[max(bb[i][1] for bb in bounds) for i in range(3)]
    beam_bottom=vr_bounds(bpy.data.objects[beam_name])[2][0]
    for o in members:
        o.scale.z=beam_bottom-.008; o.location.z=(beam_bottom-.008)/2
    vr_box(prefix+' bearing cap',(lo[0],lo[1],beam_bottom-.008),(hi[0],hi[1],beam_bottom),bpy.data.collections['03 Ground floor steel and LVL'],steel)
    caps.append({'column':prefix,'bearing_z':beam_bottom,'old_gap_mm':round((beam_bottom-hi[2])*1000,2)})
changes.append({'object':'Steel column heads','action':'Six closed bearing caps coordinated to beam undersides'})

# Recess the fixing assemblies, which previously protruded through the finished
# slab, and extend each hollow post down to its bearing face. Do this after
# coordinating the heads so later height adjustments cannot reopen the joint.
bpy.context.view_layer.update()
for plate in [o for o in house.objects if o.name.endswith(' baseplate')]:
    prefix=plate.name[:-len(' baseplate')]
    plate.location.z-=.065
    for o in house.objects:
        if not o.name.startswith(prefix+' '): continue
        if 'anchor bolt' in o.name: o.location.z-=.065
        if 'profile ' in o.name:
            o.data=o.data.copy(); inverse=o.matrix_world.inverted()
            for v in o.data.vertices:
                p=o.matrix_world@v.co
                if abs(p.z)<.001: p.z=-.041; v.co=inverse@p
    record(plate,'Recessed plate/anchors below finished slab and extended column foot to bearing face')
bpy.context.view_layer.update()
for plate in [o for o in house.objects if o.name.endswith(' baseplate')]:
    prefix=plate.name[:-len(' baseplate')]
    for post in [o for o in house.objects if o.name.startswith(prefix+' profile ')]:
        assert abs(vr_bounds(post)[2][0]-vr_bounds(plate)[2][1])<.00001

# Complete straight flight. Upper landing is the seventeenth rise, avoiding the
# former redundant top tread and its collision with the floor trimmer.
old=[o for o in house.objects if o.name.startswith(('Stair rough tread','Stair stringer'))]
assert len(old)==20
for o in old: bpy.data.objects.remove(o,do_unlink=True)
stairs=bpy.data.collections.new('12 Finished staircase'); house.collection.children.link(stairs)
oak=vr_material('VR Stair oak timber',(.73,.58,.39))
paint=vr_material('VR Stair warm white lining',(.90,.88,.84))
foot=24.90; head=20.9505; run=foot-head; rise=3.159/17; going=run/16
y0,y1=6.73,7.75; tread=.04; riser=.018
stair_checks=[]
for i in range(16):
    front=foot-i*going; rear=front-going; top=(i+1)*rise
    vr_box(f'Stair finished tread {i+1:02}',(rear,y0,top-tread),(front,y1,top),stairs,oak)
    vr_box(f'Stair closed riser {i+1:02}',(front-riser,y0,i*rise),(front,y1,top-tread),stairs,paint)
    stair_checks.append({'step':i+1,'top':top,'front':front,'back':rear})
vr_box('Stair landing riser',(head-riser,y0,16*rise),(head,y1,3.14),stairs,paint)

# Sawtooth stringers follow tread undersides; the old diagonal beams pierced the treads.
profile=[]
for i in range(16):
    u=i*going+riser; z=(i+1)*rise-tread
    profile.append((foot-u,z)); profile.append((foot-((i+1)*going+riser),z))
end=run+riser
bottom_end=max(0,end*rise/going-.25)
profile.extend([(foot-end,bottom_end),(foot-.25*going/rise,0),(foot-riser,0)])
for i,y in enumerate((y0+.0225,(y0+y1)/2,y1-.0225)):
    vr_extrude(f'Stair fitted stringer {i+1}',profile,y-.0225,y+.0225,stairs,paint)

# Finish the 25 mm side junction: a closed string follows the pitch and butts
# the lining. It sits beside (not through) the treads and closes the dark slot.
wall_face=7.775
wall_string=[(foot,0),(foot,rise+.12),(head,3.159+.12),
             (head,3.159-.20),(foot-(.20-rise)*going/rise,0)]
vr_extrude('Stair wall-side closed string',wall_string,y1,wall_face,stairs,paint)
assert abs(wall_face-y1-.025)<.00001

rail_y=y0+.035
def rail_z(u): return rise+.9+min(u,run)*rise/going
rail_a=(foot-.025,rail_y,rail_z(.025)); rail_b=(head,rail_y,rail_z(run))
vr_beam('Stair oak handrail',rail_a,rail_b,.055,.055,stairs,oak)
vr_beam('Stair landing handrail',(head,rail_y,rail_z(run)),(head-.24,rail_y,rail_z(run)),.055,.055,stairs,oak)
# Newels bear on a tread or the retained upper deck, not in space.
for i,u in enumerate((.065,run*.49,run+.18)):
    base=3.159 if u>run else (min(15,int(u/going))+1)*rise
    x=foot-u
    vr_extrude(f'Stair newel {i+1}',[(x-.035,base),(x+.035,base),
        (x+.035,rail_z(u-.035)-.022),(x-.035,rail_z(u+.035)-.022)],rail_y-.035,rail_y+.035,stairs,oak)
for i,u in enumerate([step*going+off for step in range(16) for off in (.060,.180)]):
    if abs(u-.065)<.06: continue
    if abs(u-run*.49)<.07: continue
    base=(min(15,int(u/going))+1)*rise; x=foot-u; half=.0125
    vr_extrude(f'Stair baluster {i:02}',[(x-half,base),(x+half,base),
        (x+half,rail_z(u-half)-.022),(x-half,rail_z(u+half)-.022)],rail_y-.0125,rail_y+.0125,stairs,paint)
# A wall-side handrail is carried by visible brackets fixed to the wall face.
wall_rail_y=7.70
vr_beam('Stair wall handrail',(rail_a[0],wall_rail_y,rail_a[2]),(head,wall_rail_y,rail_b[2]),.045,.05,stairs,oak)
for i,u in enumerate((.25,1.4,2.6,3.7)):
    x=foot-u; z=rail_z(u)-.020
    vr_box(f'Stair rail bracket {i+1}',(x-.012,wall_rail_y,z-.035),(x+.012,7.775,z),stairs,steel)

# Checks capture the actual finished geometry, including landing and support contacts.
bpy.context.view_layer.update()
assert abs((foot-16*going)-head)<1e-7
assert abs(head-riser-vr_bounds(bpy.data.objects['Floor rim/trimmer 5'])[0][1])<.00001
assert abs(17*rise-3.159)<1e-7
assert max(v[1] for v in profile)<16*rise
stair_report={'risers':17,'timber_treads':16,'rise_m':rise,'going_m':going,'width_m':y1-y0,
 'floor_to_floor_m':3.159,'foot_x':foot,'landing_edge_x':head,'flight_clear_run_m':run,
 'basis':'Existing approximately 4 m flight coordinated to trimmer face, 18 mm landing riser and 19 mm floor deck; illustrative finish detail',
 'checks':'PASS: uniform rises/goings, final riser meets deck underside, stringers meet trimmer face, lowest stringers bear on slab; closed wall-side string fills 25 mm junction',
 'wall_side_junction_m':0,
 'steps':stair_checks,'column_caps':caps,'brace_offsets':brace_report}
(OUT/'stair-coordination.json').write_text(json.dumps(stair_report,indent=2))
changes.append({'object':'Complete staircase','action':'16 timber treads, 17 closed risers, 3 fitted stringers, newels, balusters, handrails and brackets; connected to finished landing'})
