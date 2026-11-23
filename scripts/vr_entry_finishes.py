"""Finish the two corrected portals, with the scheduled leaves held open."""
for d in entry_report['doors']:
    tag=d['name']; x=d['hinge_edge_x']+.022+.003; y=d['wall_y']+.060
    width=d['nominal_leaf_width_mm']/1000; base=3.159+.003
    # Ninety-degree inward swing as shown on sheet 08. Static leaves keep the
    # directed room route clear and are hidden with the other wall finishes.
    vr_box(tag+' | open painted leaf',(x,y,base),(x+.038,y+width,base+2.340),opening_col,plaster)
    for level in (.25,1.17,2.09):
        vr_box(tag+' | hinge',(x-.004,y-.012,base+level-.035),
               (x+.004,y+.012,base+level+.035),opening_col,steel)
    for side in (-1,1):
        face=x if side<0 else x+.038; a,b=sorted((face,face+side*.028))
        vr_box(tag+' | handle rose',(a,y+width-.080,base+.960),
               (b,y+width-.040,base+1.000),opening_col,steel)
        a,b=sorted((face+side*.028,face+side*.036))
        vr_box(tag+' | lever',(a,y+width-.155,base+.972),
               (b,y+width-.055,base+.988),opening_col,steel)
    d['open_leaf_angle_degrees']=90
    d['minimum_clear_at_leaf_mm']=d['jamb_clear_width_mm']-41
    d['leaf_position']={'x':x,'y':y,'z':base}

bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
checks=[]
for d in entry_report['doors']:
    centre=d['centre_x']; y=d['wall_y']; clear=d['jamb_clear_width_mm']/1000
    # Multiple heights and offsets catch intrusions missed by a centre-only
    # capsule. Keep a small tolerance from the actual jamb faces.
    for z in (3.25,4.2,5.45):
        for x in (centre-clear/2+.010,centre,centre+clear/2-.010):
            hit=house.ray_cast(deps,Vector((x,y-.20,z)),Vector((0,1,0)),distance=.25)
            assert not hit[0], (d['name'],'portal intrusion',x,z,hit[4].name if hit[0] else None)
    # Cast upwards through the centre: the actual jamb head must be 2346 mm
    # above the finished deck, not the old 2311 mm opening.
    hit=house.ray_cast(deps,Vector((centre,y,3.2)),Vector((0,0,1)),distance=3)
    assert hit[0] and abs(hit[1].z-5.505)<.0001,(d['name'],'head',list(hit[1]),hit[4].name if hit[0] else None)
    checks.append({'door':d['name'],'portal_grid_clear':True,'measured_head_z':round(hit[1].z,4)})
for p in entry_report['partitions']:
    rec=next(r for r in walls if r['name']==p['wall']); x=rec['start'].x
    for y in (p['new_end_y']+.08,(p['new_end_y']+p['old_end_y'])/2):
        for z in (3.25,4.5,5.65):
            hit=house.ray_cast(deps,Vector((x+.09,y,z)),Vector((-1,0,0)),distance=.1)
            assert hit[0] and abs(hit[1].x-(x+.060))<.0001,(p['wall'],'lining gap',y,z)
    p['lining_continuity_verified']=True
entry_report['checks']=checks
(OUT/'upper-entry-coordination.json').write_text(json.dumps(entry_report,indent=2))
changes.append({'object':'Bedroom 5 and upper bathroom entries','action':'Sheet 08 door proportions, complete wall returns, finished jambs and open painted leaves; geometric portal and lining checks passed'})
