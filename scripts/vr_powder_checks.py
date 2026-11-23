"""Check finished window apertures and the coordinated pier before export."""
bpy.context.view_layer.update();powder_deps=bpy.context.evaluated_depsgraph_get()
powder_checks=[];powder_glazing_samples=[]
for label in ('W03 powder','W10 stair'):
    opening=bpy.data.objects['OPENING | '+label]
    glass=next(o for o in opening.children if 'glass' in o.name)
    bb=vr_bounds(glass)
    # Verify glazing from both room and outside; a new column, stud or skin
    # intrusion on either side must fail the build, not merely change framing.
    for fx in (.08,.25,.5,.75,.92):
        for fz in (.08,.5,.92):
            x=bb[0][0]+fx*(bb[0][1]-bb[0][0]);z=bb[2][0]+fz*(bb[2][1]-bb[2][0])
            for y,direction in ((7.60,1),(8.20,-1)):
                hit=house.ray_cast(powder_deps,Vector((x,y,z)),Vector((0,direction,0)),distance=.7)
                assert hit[0] and hit[4]==glass,(label,'blocked glazing',x,z,hit[4].name if hit[0] else None)
                powder_glazing_samples.append({'window':label,'position':{'x':-x,'y':z,'z':-y},'direction':{'x':0,'y':0,'z':-direction}})
    powder_checks.append({'window':label,'clear_glazing_rays':30})
for z in (.1,.3,1,2.5,2.75,2.95,3.10,3.16,3.4,4,5.5,5.7):
    for direction in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0)):
        hit=house.ray_cast(powder_deps,Vector((powder_column_x,7.835,z)),Vector(direction),distance=.06)
        assert hit[0] and hit[4].name.startswith(powder_prefix+' profile '),('Timber inside steel pier',z,hit[4].name if hit[0] else None)
for name in powder_beam_ends:
    assert abs(vr_bounds(bpy.data.objects[name])[0][0]-powder_column_right)<.00001
# The newly extended steel envelope must not pass through timber or a joist web.
for ob in house.objects:
    if ob.type!='MESH' or ob.name in powder_beam_ends:continue
    if not (ob.name.startswith('FJ-33B ') or any(m and m.name in ('MGP10 pine','LVL beams') for m in ob.data.materials)):continue
    # Edited diagonal webs have a conservative transformed local bounding box.
    # Measure their actual world vertices at the trimmed plane.
    points=[ob.matrix_world@v.co for v in ob.data.vertices]
    bb=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
    overlap=[min(bb[i][1],hi)-max(bb[i][0],lo) for i,(lo,hi) in enumerate(((powder_column_right,powder_old_x),(7.785,7.885),(2.945,3.095)))]
    assert min(overlap)<.00001,('Extended ST1 overlap',ob.name,overlap)
powder_report.update({'result':'PASS','window_checks':powder_checks,'column_internal_clearance_rays':48,
    'glazing_samples':powder_glazing_samples,
    'head_connection':'ST1 meets post east face; 1B2, stair trimmer and adjacent joist butt against its inner face. Redundant timber rim replaced by steel with 45 mm bearing pack above.',
    'extended_head_overlap_check':'PASS'})
(OUT/'powder-window-coordination.json').write_text(json.dumps(powder_report,indent=2))
changes.append({'object':'Powder/stair window and C2(F) pier','action':powder_report})
