"""Coordinate W07 with the rebuilt ensuite, keeping the written1800 gap to W06."""
sw_rec=next(r for r in vr_wall_records if r['name']=='GF South family and suite')
# Sheet17 depicts W07 centred in the1800 ensuite enclosure. The1510 envelope
# leaves145 at each frame-side edge; position is scaled, width is scheduled.
sw_w07_centre=(18.560+20.360)/2
sw_w06_centre=sw_w07_centre-.755-1.800-1.530
sw_targets={'W07 ensuite':sw_w07_centre,'W06 family':sw_w06_centre}
sw_moves=[];sw_edges=[]
for sw_op in sw_rec['openings']:
    sw_tag,sw_c,sw_w,sw_s,sw_h=sw_op
    if sw_tag not in sw_targets:continue
    sw_old=sw_rec['a'][0]+sw_c;sw_new=sw_targets[sw_tag]
    sw_edges.extend(((sw_old-sw_w/2,sw_new-sw_w/2),(sw_old+sw_w/2,sw_new+sw_w/2)))
    sw_op[1]=sw_new-sw_rec['a'][0]
    bpy.data.objects['OPENING | '+sw_tag].location.x+=sw_new-sw_old
    sw_moves.append({'window':sw_tag,'old_centre_x':sw_old,'new_centre_x':sw_new,
        'position_basis':'Sheet17 centred W07 within ensuite; written1800 separation to W06 on07. Absolute facade registration remains scaled.'})
bpy.context.view_layer.update()
for sw_ob in house.objects:
    if sw_ob.type!='MESH' or sw_ob.get('associated_frame')!=sw_rec['name']:continue
    if not any(abs((sw_ob.matrix_world@v.co).x-old)<.0001 for v in sw_ob.data.vertices for old,new in sw_edges):continue
    sw_ob.data=sw_ob.data.copy();sw_inv=sw_ob.matrix_world.inverted()
    for sw_v in sw_ob.data.vertices:
        sw_p=sw_ob.matrix_world@sw_v.co
        sw_match=next((new for old,new in sw_edges if abs(sw_p.x-old)<.0001),None)
        if sw_match is not None:sw_p.x=sw_match;sw_v.co=sw_inv@sw_p
for sw_ob in list(house.objects):
    if sw_ob.type=='MESH' and sw_ob.name.startswith(sw_rec['name']+' |') and not sw_ob.get('associated_frame'):
        bpy.data.objects.remove(sw_ob,do_unlink=True)
arch_env['wall'](sw_rec['name'],sw_rec['a'][:2],sw_rec['b'][:2],0,2.74,
                bpy.data.collections['02 Ground floor walls'],sw_rec['openings'])
bpy.context.view_layer.update()
(OUT/'south-window-registration.json').write_text(json.dumps(sw_moves,indent=2))
changes.append({'object':'W06/W07 registration','action':'Kept1510x1260 W07 within corrected ensuite; preserved written1800 gap to3060-wide W06. Frame and skins regenerated together.'})
