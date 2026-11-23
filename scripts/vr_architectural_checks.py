"""Measure generated wall faces and probe real portal meshes before export."""
bpy.context.view_layer.update();architectural_deps=bpy.context.evaluated_depsgraph_get()
dimension_checks=[];portal_checks=[];failures=[]
def plate_face(name,axis,side):
    plates=[ob for ob in house.objects if ob.type=='MESH' and ob.name.startswith(name+' |') and 'plate' in ob.name and 'anchor' not in ob.name]
    assert plates,name
    return (min if side==0 else max)(vr_bounds(ob)[axis][side] for ob in plates)
specs=[
 ('Powder width','Powder west','Powder east',0,1.600),
 ('Powder depth','Powder south','GF North wall',1,2.590),
 ('Entry depth','Entry bedroom division','GF North wall',1,3.110),
 ('Bed1 width','WIR bedroom division','GF East entry and bedroom',0,4.000),
 ('Bed1 depth','GF South family and suite','Entry bedroom division',1,4.500),
 ('WIR1 width','Ensuite WIR second skin','WIR bedroom division',0,2.270),
 ('WIR1 depth','GF South family and suite','Entry suite division',1,3.780),
 ('Ensuite width','Ensuite west','Ensuite WIR division',0,1.800),
 ('Ensuite depth','GF South family and suite','Entry suite division',1,3.780),
 ('Bed4 width','FF West wall','FF Bed 4 WC division',0,4.680),
 ('Bed4 depth','FF Bed 4 and robes','FF North wall',1,3.200),
 ('UpperWC width','FF Bed 4 WC division','FF WC bath division',0,1.000),
 ('UpperWC depth','FF WC south','FF North wall',1,2.110),
 ('Upperbath width','FF WC bath division','FF Bath robe division',0,2.000),
 ('Bed5 width','FF Bed 5 west','FF Bed 5 east',0,4.310),
 ('Bed5 depth','FF Bed 5 south','FF North wall',1,3.200),
 ('Bath2 width','FF Bath 2 west','FF Bath 2 east',0,2.200),
 ('Bath2 depth','FF South wall','FF Bath 2 bedroom wall',1,2.110),
 ('Bed2 width excluding robe','FF Bath 2 east','FF Bed 2 robe front',0,3.310),
 ('Bed2 depth','FF South wall','FF Bed 2 study hall',1,3.200),
 ('Study width','FF Bed 2 study division','FF Study retreat division',0,2.400),
 ('Study depth','FF South wall','FF Bed 2 study hall',1,3.200),
 ('Retreat width','FF Study retreat division','FF Theatre west',0,3.000),
 ('Theatre width','FF Theatre west','FF East wall',0,4.300),
 ('Theatre depth','FF South wall','FF Theatre north',1,4.500),
 ('Upper hall width','FF Bed 2 study hall','FF Bed 5 south',1,1.120),
]
for title,low,high,axis,expected in specs:
    actual=plate_face(high,axis,0)-plate_face(low,axis,1)
    ok=abs(actual-expected)<.001
    dimension_checks.append({'name':title,'drawing_mm':round(expected*1000),'mesh_mm':round(actual*1000,2),'pass':ok})
    if not ok:failures.append(title)
for rec in vr_wall_records:
    if rec['name'] not in {w['name'] for w in arch_report['walls']}:continue
    t=(rec['end']-rec['start']).normalized();n=Vector((-t.y,t.x,0))
    for tag,c,w,s,h in rec['openings']:
        floor=rec['z']+(.019 if rec['z']>1 else 0)
        if s>.001:continue
        obstruction=[]
        storage=any(word in tag.lower() for word in ('robe sliders','linen sliders'))
        # Shelving/support panels legitimately occupy a shallow cupboard. Check
        # its finished aperture, while retaining the deeper route test for doors.
        probe_depth=.130 if storage else .450
        for u in (-w/2+.080,0,w/2-.080):
            for z in (.15,1.10,2.20):
                centre=rec['start']+t*(c+u);centre.z=floor+z
                hit=house.ray_cast(architectural_deps,centre-n*(probe_depth/2),n,distance=probe_depth)
                if hit[0]:obstruction.append({'offset':round(u,3),'height':z,'object':hit[4].name})
        portal_checks.append({'wall':rec['name'],'opening':tag,'usage':'storage aperture' if storage else 'walk-through',
            'probe_depth_m':probe_depth,'rays':9,'obstructions':obstruction,'pass':not obstruction})
        if obstruction:failures.append(rec['name']+'/'+tag)
for ob in stairs.objects:
    bb=vr_bounds(ob)
    if bb[0][0]<stair_report['landing_edge_x']-.25 or bb[0][1]>stair_report['foot_x']+.05:
        failures.append('Stair member outside its flight: '+ob.name)
report={'status':'PASS' if not failures else 'FAIL','scope':'26 written frame-face spans,9 rays through each rebuilt opening, and staircase member extents. Does not certify furnishings, all external geometry, structural design, or unresolved theatre step/bulkhead coordination.',
 'dimensions':dimension_checks,'portals':portal_checks,'failures':failures}
(OUT/'architectural-geometry-checks.json').write_text(json.dumps(report,indent=2))
print('ARCHITECTURAL_GEOMETRY_CHECKS',report['status'],len(dimension_checks),len(portal_checks),failures,flush=True)
assert not failures,failures
