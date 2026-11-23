"""Register window chains and the full-height C2(F) jamb against sheets07/08.

Keep scheduled sizes and W10's original traced position. Align C2 between W10's
east edge and W03's west edge, within the independently scaled S09/07 range.
Written3720/3240/3960 window chains then set W05/W04/W02. Absolute registration
is scaled, not a dimensioned engineering setout; connection details remain
illustrative and are explicitly reported separately from aperture ray checks.
"""
powder_rec=next(r for r in vr_wall_records if r['name']=='FF North wall')
powder_op=next(o for o in powder_rec['openings'] if o[0]=='W10 stair')
powder_upper_east=powder_rec['a'][0]+powder_op[1]+powder_op[2]/2
powder_column_x=powder_upper_east+.0445
powder_upper_shift=0.0
powder_prefix='C2 full height stair A'
powder_old_x=bpy.data.objects[powder_prefix+' baseplate'].location.x
for ob in house.objects:
    if ob.name.startswith(powder_prefix+' '):ob.location.x+=powder_column_x-powder_old_x

# Sheet07's3960 is from W03 EAST jamb to W02 WEST jamb. Inspection of the
# actual dimension extension lines is essential; it is not centre-to-centre.
powder_lower_rec=next(r for r in vr_wall_records if r['name']=='GF North wall')
powder_w03_left=powder_column_x+.0445
powder_w04_right=powder_w03_left-3.240
powder_w05_right=powder_w04_right-1.510-3.720
powder_targets={'W03 powder':powder_w03_left+.405,
 'W04 kitchen':powder_w04_right-.755,
 'W05 meals':powder_w05_right-1.355,
 'W02 entry':powder_w03_left+.810+3.960+.405}
powder_edge_moves=[];powder_window_moves=[]
for op in powder_lower_rec['openings']:
    tag,c,w,s,h=op
    if tag not in powder_targets:continue
    old_c=powder_lower_rec['a'][0]+c;new_c=powder_targets[tag];shift=new_c-old_c
    powder_edge_moves.extend([(old_c-w/2,new_c-w/2),(old_c+w/2,new_c+w/2)])
    op[1]=new_c-powder_lower_rec['a'][0]
    if tag.startswith('W04'):op[3]=.905
    bpy.data.objects['OPENING | '+tag].location.x+=shift
    powder_window_moves.append({'window':tag,'old_centre_x':old_c,'new_centre_x':new_c,
                                'shift_mm':round(shift*1000,1)})
powder_skins=[]
bpy.context.view_layer.update()
for ob in house.objects:
    if ob.type!='MESH' or ob.get('associated_frame')!='GF North wall':continue
    points=[ob.matrix_world@v.co for v in ob.data.vertices]
    if not any(abs(p.x-old)<.0001 for p in points for old,new in powder_edge_moves):continue
    ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
    for vertex in ob.data.vertices:
        p=ob.matrix_world@vertex.co
        move=next((new for old,new in powder_edge_moves if abs(p.x-old)<.0001),None)
        if move is not None:p.x=move;vertex.co=inv@p
    powder_skins.append(ob.name)
for ob in list(house.objects):
    if ob.type=='MESH' and ob.name.startswith('GF North wall |') and not ob.get('associated_frame'):
        bpy.data.objects.remove(ob,do_unlink=True)
arch_env['wall'](powder_lower_rec['name'],powder_lower_rec['a'][:2],powder_lower_rec['b'][:2],
    0,2.74,bpy.data.collections['02 Ground floor walls'],powder_lower_rec['openings'])
bpy.context.view_layer.update()

# The existing ST1 horizontal member now meets the relocated column's east
# face. Its far support and the 1B2/stair trimmer positions stay fixed.
powder_column_right=powder_column_x+.0445
powder_beam_ends=[]
for i in range(1,5):
    ob=bpy.data.objects[f'ST1 150x100x6 RHS profile {i}'];ob.data=ob.data.copy()
    inv=ob.matrix_world.inverted();old_left=vr_bounds(ob)[0][0]
    for vertex in ob.data.vertices:
        p=ob.matrix_world@vertex.co
        if abs(p.x-old_left)<.0001:p.x=powder_column_right;vertex.co=inv@p
    powder_beam_ends.append(ob.name)
# End the transverse timber member at the face of ST1 instead of embedding
# it into the RHS. The retained floor trimmer meets the same steel face.
for name in ('1B2 300x45','Floor rim/trimmer 5'):
    ob=bpy.data.objects[name];ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
    for vertex in ob.data.vertices:
        p=ob.matrix_world@vertex.co
        if p.y>7.785:p.y=7.785;vertex.co=inv@p
    ob.data.update()
bpy.context.view_layer.update()

# Replace the short timber rim segment now occupied by the extended ST1.
# A 45 mm pack above the steel preserves the original deck support datum.
powder_rim=bpy.data.objects['Floor rim/trimmer 2'];powder_rim_bounds=vr_bounds(powder_rim)
powder_rim.data=powder_rim.data.copy();powder_inverse=powder_rim.matrix_world.inverted()
for vertex in powder_rim.data.vertices:
    p=powder_rim.matrix_world@vertex.co
    if p.x>powder_column_x-.0445:p.x=powder_column_x-.0445;vertex.co=powder_inverse@p
vr_box('C2 pier floor bearing pack',(powder_column_right,powder_rim_bounds[1][0],3.095),
    (powder_rim_bounds[0][1],powder_rim_bounds[1][1],3.14),powder_rim.users_collection[0],bpy.data.materials['LVL beams'])
# The adjacent joist also terminates at the head face. Move its end block
# with that face, retaining its depth instead of crushing it to a sliver.
for ob in house.objects:
    if ob.type!='MESH' or not ob.name.startswith('FJ-33B '):continue
    bb=vr_bounds(ob)
    if bb[1][1]<=7.785:continue
    if 'end block' in ob.name and bb[1][0]>7.7:
        ob.location.y-=bb[1][1]-7.785;continue
    ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
    for vertex in ob.data.vertices:
        p=ob.matrix_world@vertex.co
        if p.y>7.785:p.y=7.785;vertex.co=inv@p

# Reserve the solid post footprint through timber plates, jambs and the rim.
# The post replaces that timber volume; no duplicate structure fills its tube.
powder_cut_col=bpy.data.collections.new('Temporary column clearance');house.collection.children.link(powder_cut_col)
powder_cut=vr_box('C2 clearance',(powder_column_x-.0445,7.7900,-.041),
    (powder_column_right,7.8800,5.73),powder_cut_col,steel)
bpy.context.view_layer.update();powder_trimmed=[]
for ob in list(house.objects):
    if ob.type!='MESH' or ob==powder_cut:continue
    if not any(m and (m.name=='MGP10 pine' or m.name=='LVL beams') for m in ob.data.materials):continue
    bb=vr_bounds(ob)
    if any(bb[i][1]<=v or bb[i][0]>=w for i,(v,w) in enumerate(((powder_column_x-.0445,powder_column_right),(7.7900,7.8800),(-.041,5.73)))):continue
    # A replaced jamb is removed as a member, not left as a millimetre sliver
    # around the steel. The 90 mm timber pocket leaves 0.5 mm each side of RHS.
    remainder=bb[0][1]-bb[0][0]-max(0,min(bb[0][1],powder_column_right)-max(bb[0][0],powder_column_x-.0445))
    if ('king stud' in ob.name or 'jack stud' in ob.name) and remainder<.012:
        powder_trimmed.append(ob.name+' replaced by steel pier')
        bpy.data.objects.remove(ob,do_unlink=True);continue
    if ob.data.users>1:ob.data=ob.data.copy()
    modifier=ob.modifiers.new('Reserve full-height steel pier','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=powder_cut
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=modifier.name)
    powder_trimmed.append(ob.name)
    if not ob.data.vertices:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(powder_cut,do_unlink=True);bpy.data.collections.remove(powder_cut_col)
bpy.context.view_layer.update()
powder_report={'basis':'Written window chains on architectural07, scheduled sizes on11, scaled column/jamb alignment on07/08 and S09. C2(F) full height confirmed by engineering schedule. Absolute jamb registration and steel connections remain illustrative, not a dimensioned engineering setout.',
    'column_old_x':powder_old_x,'column_new_x':powder_column_x,
    'column_shift_mm':round((powder_column_x-powder_old_x)*1000,1),
    'upper_window_shift_mm':0,'powder_window_size_mm':[810,2120],
    'upper_window_size_mm':[850,1800],'powder_window_position_unchanged':False,
    'window_moves':powder_window_moves,'written_window_gaps_m':[3.720,3.240,3.960],
    'registration_status':'SCALED: C2 centre within20.69..20.73 range; W10 original position retained. Requires drawing coordination for construction.',
    'stair_layout_unchanged':True,'updated_facade_and_wrap_panels':powder_skins,
    'connected_head_members':powder_beam_ends,'timber_clearance_trims':powder_trimmed}
