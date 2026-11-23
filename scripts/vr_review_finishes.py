"""Close visible contact defects and refine specified finishes in the VR model."""

# A full-height downstairs powder wall intersected steps 13/14. Trim it below
# the stair stringers and finish the stair underside, preserving the stair rises.
stair_head=stair_report['landing_edge_x'];stair_foot=stair_report['foot_x']
stair_rise=stair_report['rise_m'];stair_going=stair_report['going_m']
def soffit_bottom(x): return (stair_foot-x)*stair_rise/stair_going-.265
cut_col=bpy.data.collections.new('VR temporary cutters');house.collection.children.link(cut_col)
cutter=vr_extrude('Stair underside clearance cutter',[(20.8,soffit_bottom(20.8)-.001),
    (24.9,soffit_bottom(24.9)-.001),(24.9,4),(20.8,4)],6.60,7.785,cut_col,plaster)
bm=bmesh.new();bm.from_mesh(cutter.data)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cutter.data);bm.free()
bpy.context.view_layer.update()
trimmed=[]
for o in list(house.objects):
    if o.type!='MESH' or not o.name.startswith('Powder east |'):continue
    bb=vr_bounds(o)
    if bb[1][1]<=6.60 or bb[2][1]<=soffit_bottom(bb[0][1])-.001:continue
    if o.data.users>1:o.data=o.data.copy()
    mod=o.modifiers.new('Fit beneath stair','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.modifier_apply(modifier=mod.name)
    trimmed.append(o.name)
    if not o.data.vertices:bpy.data.objects.remove(o,do_unlink=True)
bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.collections.remove(cut_col)
vr_extrude('Finished stair underside',[(stair_head,soffit_bottom(stair_head)),(stair_head,soffit_bottom(stair_head)+.012),
    (stair_foot-.253*stair_going/stair_rise,0),(stair_foot-.265*stair_going/stair_rise,0)],6.73,7.775,linings,plaster)
vr_box('Stair underside landing closure',(stair_head-.018,6.73,soffit_bottom(stair_head)),
       (stair_head,7.775,16*stair_rise),linings,plaster)

# P1 remains the scheduled 90 mm treated-pine core. Thin painted finish faces
# hide with the walls, so structural mode still reveals the original timber.
for post in [o for o in house.objects if o.name.startswith('P1 porch post')]:
    bb=vr_bounds(post);x0,x1=bb[0];a,b=bb[1];d=.003
    for i,lo,hi in [(0,(x0-d,a-d,0),(x1+d,a,2.525)),(1,(x0-d,b,0),(x1+d,b+d,2.525)),
                   (2,(x0-d,a,0),(x0,b,2.525)),(3,(x1,a,0),(x1+d,b,2.525))]:
        vr_box(post.name+f' paint finish {i}',lo,hi,linings,plaster)

# S09/S10 C3 is a 200 x 100 RHS portal support near the meals window.
# Keep the steel and its bearing; removable lining provides the finished view.
for prefix in ('C3 portal north',):
    members=[o for o in house.objects if o.name.startswith(prefix+' profile ')]
    bs=[vr_bounds(o) for o in members];x0=min(b[0][0] for b in bs)-.005;x1=max(b[0][1] for b in bs)+.005
    a=min(b[1][0] for b in bs)-.005;b=max(b[1][1] for b in bs)+.005;d=.010
    for i,lo,hi in [(0,(x0-d,a-d,0),(x1+d,a,2.73)),(1,(x0-d,b,0),(x1+d,b+d,2.73)),
                   (2,(x0-d,a,0),(x0,b,2.73)),(3,(x1,a,0),(x1+d,b,2.73))]:
        solid(prefix+f' finished lining {i}',(lo,hi),linings,plaster)

# Replace the single flat double-door proxy with two leaves and slim pulls.
bronze=vr_material('VR Door bronze hardware',(.12,.105,.085))
bronze.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.75
bronze.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.32
entry=bpy.data.objects['OPENING | D01 double entry']
old_leaf=next(o for o in entry.children if 'door leaf' in o.name)
w,depth,h=old_leaf.scale; centre=old_leaf.location.copy()
def entry_part(name,lo,hi,mat):
    o=vr_box(name,lo,hi,opening_col,mat);o.parent=entry;return o
for i,sign in enumerate((-1,1)):
    a,b=(-w/2,-.002) if sign<0 else (.002,w/2)
    entry_part(f'D01 finished timber leaf {i+1}',(a,centre.y-depth/2,centre.z-h/2),
               (b,centre.y+depth/2,centre.z+h/2),doorwood)
    x=sign*.065
    entry_part(f'D01 bronze pull {i+1}',(x-.009,-.084,.83),(x+.009,-.066,1.28),bronze)
    for z in (.86,1.25):
        entry_part(f'D01 pull fixing {i+1}',(x-.006,-.066,z-.006),
                   (x+.006,centre.y-depth/2,z+.006),bronze)
bpy.data.objects.remove(old_leaf,do_unlink=True)

# The masonry projects beyond the simplified slab. Build just the missing
# bearing strips, subtracting the existing slabs and prior strips to avoid
# doubled solids. These remain when the wall finish is hidden.
plinths=group('13 Ground bearing plinths');foundation=vr_material('VR Foundation concrete',(.64,.62,.58))
occupied=[([6.38,0,-.22],[26.99,7.88,0]),([0,2.46,-.22],[6.38,9.37,0]),
    ([26.99,4.18,-.26],[32.21,6.48,0]),([26.99,6.48,-.26],[28.45,8.015,0]),
    ([12.5,-5,-.26],[19.5,-.2,0])]
strips=[]
for ob in list(house.objects):
    if ob.type!='MESH' or not any(c.name in ('Retained','Cutaway removal','23 Ground brick veneer') or c.name.startswith(('Retained.','Cutaway removal.')) for c in ob.users_collection):continue
    if not ob.data.materials or not any('Brick veneer' in m.name for m in ob.data.materials if m):continue
    bb=vr_bounds(ob)
    if abs(bb[2][0])>.003:continue
    pieces=[([bb[0][0],bb[1][0],-.22],[bb[0][1],bb[1][1],0])]
    for other in occupied:pieces=[p for box in pieces for p in subtract(box,other)]
    for bounds in pieces:
        solid('Masonry bearing plinth',bounds,plinths,foundation);occupied.append(bounds);strips.append(bounds)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
# The previously visible stripe must now resolve to the stair surface.
eye=Vector((20.45,7.2,4.809));f=(Vector((23,7.2,2.5))-eye).normalized();r=f.cross(Vector((0,0,1))).normalized();u=r.cross(f)
for py in (775,790,803):
    direction=(f+u*((1-2*py/1000)*math.tan(math.radians(30)))).normalized()
    hit=house.ray_cast(deps,eye,direction,distance=10)
    assert hit[0] and hit[4].name.startswith('Stair finished tread'),('Stair obstruction remains',py,hit[4].name if hit[0] else None)
report={'stair_wall_members_trimmed':trimmed,'stair_obstruction_ray_checks':'PASS',
 'ground_grade_m':-.06,'masonry_bearing_strips':len(strips),'canopy_post_core':'P1 90 x 90 F7 H3 treated pine; S09/S10',
 'canopy_finish':'Illustrative warm white paint, removable in structural view',
 'meals_column':'C3 portal north, 200 x 100 x 6 RHS retained; S09/S10. Removable 10 mm illustrative lining.',
 'entry_door':'Scheduled timber; split double leaves, satin finish and illustrative bronze pulls'}
(OUT/'finish-contact-coordination.json').write_text(json.dumps(report,indent=2))
changes.append({'object':'Exterior contacts and visible finishes','action':report})
