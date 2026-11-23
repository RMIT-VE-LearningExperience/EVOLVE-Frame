"""Independent mesh checks for the new046 details."""
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update();dc_deps=bpy.context.evaluated_depsgraph_get()
dc_new=[o for o in house.objects if o.type=='MESH' and o.name.startswith('Drainage | ')]
dc_struct=[o for o in house.objects if o.type=='MESH' and any(t in m.name.lower() for m in o.data.materials if m for t in ('pine','lvl','structural steel'))]
dc_boxes={o.name:detail_box_bounds(o) for o in dc_new+dc_struct};dc_cache={};dc_hits=[]
def dc_bvh(o):
    if o.name not in dc_cache:
        mesh=o.evaluated_get(dc_deps).to_mesh()
        vertices=[o.matrix_world@v.co for v in mesh.vertices]
        dc_cache[o.name]=BVHTree.FromPolygons(vertices,[tuple(p.vertices) for p in mesh.polygons],all_triangles=False,epsilon=.000001)
        o.evaluated_get(dc_deps).to_mesh_clear()
    return dc_cache[o.name]
dc_candidates=0
for a in dc_new:
    for b in dc_struct:
        hit=detail_intersection(dc_boxes[a.name],dc_boxes[b.name])
        if hit is None:continue
        dc_candidates+=1
        if dc_bvh(a).overlap(dc_bvh(b)):dc_hits.append([a.name,b.name])
dc_fixture_checks=[]
dc_niche_dimensions=[]
for name,uaxis,daxis,sign,width,floor in [('Ensuite niche',0,1,1,1.0,.003),('Upper bath niche',1,0,1,.9,3.162),('Bath2 niche',1,0,-1,.6,3.162)]:
    bb={part:vr_bounds(bpy.data.objects[name+' tiled '+part]) for part in ('back','left reveal','right reveal','sill','head')}
    opening_width=bb['right reveal'][uaxis][0]-bb['left reveal'][uaxis][1]
    opening_height=bb['head'][2][0]-bb['sill'][2][1]
    sill_height=bb['sill'][2][1]-floor
    face=0 if sign>0 else 1
    depth=sign*(bb['back'][daxis][face]-bb['left reveal'][daxis][face])
    measured=[opening_width,opening_height,sill_height,depth];expected=[width,.45,1.2,.06]
    assert all(abs(a-b)<.00002 for a,b in zip(measured,expected)),(name,measured)
    dc_niche_dimensions.append({'name':name,'mesh_mm':dict(zip(('width','height','sill_above_tile','clear_depth'),[round(v*1000,3) for v in measured])),'result':'PASS'})
dc_outlets=[]
for outlet in dr_report['open_outlets']:
    p=Vector(outlet['position'])
    hit=house.ray_cast(dc_deps,p+Vector((0,0,.030)),Vector((0,0,-1)),distance=.060)
    dc_outlets.append({'id':outlet['id'],'clear':not hit[0],'hit':hit[4].name if hit[0] else None})
    assert not hit[0],dc_outlets[-1]
# Fitting attachment probes are aimed from inside each room toward the finish.
for name,start,direction in [
 ('Powder paper holder',(20.635,7.70,.903),(0,1,0)),
 ('Ensuite WC paper holder',(19.275,.18,.903),(0,-1,0)),
 ('Bath2 paper holder',(11.355,.18,4.062),(0,-1,0)),
 ('Upper WC paper holder',(12.15,7.075,4.062),(1,0,0)),
 ('Bath2 towel rail',(12.75,1.6,4.362),(1,0,0)),
 ('Upper bath towel rail',(12.42,6.25,4.362),(-1,0,0)),
 ('Ensuite towel ring',(20.270,2.68,1.203),(1,0,0))]:
    # Start beyond the hardware, test an offset point on the mounting face.
    origin=Vector(start);origin.z+=.04
    hit=house.ray_cast(dc_deps,origin,Vector(direction),distance=.1)
    good=hit[0] and 'lining' in hit[4].name
    dc_fixture_checks.append({'name':name,'wall':hit[4].name if hit[0] else None,'pass':good})
    assert good,dc_fixture_checks[-1]
dc_report={'scope':'New drainage against retained timber/LVL/steel by actual triangle intersections; fitting mounting-face probes.',
 'drainage_objects':len(dc_new),'structural_objects':len(dc_struct),'candidate_pairs':dc_candidates,
 'structural_intersections':dc_hits,'fixture_mounts':dc_fixture_checks,'open_outlet_rays':dc_outlets,'niche_dimensions':dc_niche_dimensions,
 'result':'PASS' if not dc_hits else 'FAIL'}
(ad_out/'mesh-checks.json').write_text(json.dumps(dc_report,indent=2))
assert not dc_hits,dc_hits
print('ARCH046_MESH_CHECKS_PASS',len(dc_new),dc_candidates,flush=True)
