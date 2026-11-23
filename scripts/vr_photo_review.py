"""Corrections prompted by Claude's actual 0.4.0 photo review.

Provisional exterior height coordination is recorded; it is not architectural
acceptance. Keep the engineering post cores and the source learning model.
"""
photo_report={'review':'photo-review-0.4.0/claude-review.txt','changes':[], 'unresolved':[
 'Porch footprint follows retained P1 cores; written pier sizes470x590 used, absolute setout remains provisional.',
 'Porch parapet3.245 and garage parapet3.65 are temporarily coordinated above existing trusses. Plan heights/NGL and supplier truss datum require reconciliation.',
 'Theatre floor division remains unresolved; no platform height invented.' ]}
photo_ceiling=vr_material('VR Neutral white ceiling',(.88,.88,.87))
photo_junction=vr_material('VR Plaster junction returns',(.84,.835,.82))
photo_render=vr_material('VR Neutral porch render',(.79,.79,.77))
photo_brick=bpy.data.materials['ENV Brick veneer - colour unselected']
photo_col=bpy.data.collections.new('27 Architectural exterior finishes')
house.collection.children.link(photo_col)
for photo_ob in house.objects:
    if photo_ob.type=='MESH' and ('ceiling' in photo_ob.name.lower() or 'soffit' in photo_ob.name.lower()) and photo_ob.data.materials and photo_ob.data.materials[0]==plaster:
        photo_ob.data.materials[0]=photo_ceiling
    if photo_ob.type=='MESH' and '| end return' in photo_ob.name and photo_ob.data.materials and photo_ob.data.materials[0]==plaster:
        # A separate atlas batch gives slender exposed wall ends usable texels.
        # This replaces the material assignment; it adds no overlapping lining.
        photo_ob.data.materials[0]=photo_junction

def photo_box(name,lo,hi,material=photo_render,collection=photo_col):
    return vr_box('Photo revision | '+name,lo,hi,collection,material)

# Remove the exposed canopy roof/fascia before replacing it; no parallel shells.
for photo_ob in list(house.objects):
    if photo_ob.name.startswith('Entry canopy') or ('P1 porch post' in photo_ob.name and 'paint finish' in photo_ob.name):
        bpy.data.objects.remove(photo_ob,do_unlink=True)
photo_top=3.245;photo_soffit=2.468
# Hollow masonry piers keep the90 mm engineering posts inspectable.
for photo_i,photo_y in enumerate((4.630,7.835)):
    photo_x0,photo_x1=27.950,28.420;photo_y0,photo_y1=photo_y-.295,photo_y+.295
    photo_box(f'Porch pier{photo_i} front',(photo_x1-.11,photo_y0,-.06),(photo_x1,photo_y1,photo_top),photo_brick)
    photo_box(f'Porch pier{photo_i} back',(photo_x0,photo_y0,-.06),(photo_x0+.11,photo_y1,photo_top),photo_brick)
    photo_box(f'Porch pier{photo_i} side A',(photo_x0+.11,photo_y0,-.06),(photo_x1-.11,photo_y0+.11,photo_top),photo_brick)
    photo_box(f'Porch pier{photo_i} side B',(photo_x0+.11,photo_y1-.11,-.06),(photo_x1-.11,photo_y1,photo_top),photo_brick)
    photo_box(f'Porch pier{photo_i} cap',(photo_x0,photo_y0,photo_top),(photo_x1,photo_y1,photo_top+.010))
    # Rendered side return, terminating at the pier without overlapping it.
    photo_a,photo_b=(photo_y0,photo_y0+.23) if photo_i==0 else (photo_y1-.23,photo_y1)
    photo_box(f'Porch side return{photo_i}',(27.235,photo_a,-.06),(27.950,photo_b,photo_top))
    # Side beam below the concealed roof; clear the timber core.
    photo_inner=photo_y1 if photo_i==0 else photo_y0
    photo_inner_a,photo_inner_b=(photo_inner-.015,photo_inner) if photo_i==0 else (photo_inner,photo_inner+.015)
    photo_box(f'Porch beam inner{photo_i}',(27.235,photo_inner_a,photo_soffit),(27.950,photo_inner_b,photo_top))
    photo_box(f'Porch beam soffit{photo_i}',(27.235,min(photo_b,photo_inner_b),photo_soffit),(27.950,max(photo_a,photo_inner_a),photo_soffit+.015),photo_ceiling)
    photo_box(f'Porch side beam cap{photo_i}',(27.235,min(photo_b,photo_inner_b),photo_top-.015),(27.950,max(photo_a,photo_inner_a),photo_top))
for photo_name,photo_lo,photo_hi in [
 ('Porch front beam outer',(28.405,4.925,photo_soffit),(28.420,7.540,photo_top)),
 ('Porch front beam inner',(27.950,4.925,photo_soffit),(27.965,7.540,photo_top)),
 ('Porch front beam soffit',(27.965,4.925,photo_soffit),(28.405,7.540,photo_soffit+.015)),
 ('Porch front beam cap',(27.950,4.925,photo_top-.015),(28.420,7.540,photo_top))]:
    photo_box(photo_name,photo_lo,photo_hi)
photo_box('Porch central soffit',(27.235,4.925,photo_soffit),(27.950,7.540,photo_soffit+.01),photo_ceiling,roof_trim)
# Covering remains above T6; it is recessed inside the perimeter, not an eave.
photo_roof_z=lambda x:3.205+(27.235-x)*math.tan(math.radians(5))
vr_extrude('Entry concealed roof',[(27.235,photo_roof_z(27.235)),(28.405,photo_roof_z(28.405)),
 (28.405,photo_roof_z(28.405)+.012),(27.235,photo_roof_z(27.235)+.012)],4.925,7.540,roof_cover,roof_metal)
photo_report['changes'].append('Porch now has hollow470x590 masonry piers, rendered side returns/front beam, soffit and concealed roof; P1 timber cores retained.')

# Garage brick parapets continue exactly above the existing veneer footprints.
photo_garage_skins=[o for o in house.objects if o.name.startswith('Garage ') and 'Ground brick veneer' in o.name]
photo_garage_bounds={}
for photo_ob in photo_garage_skins:
    photo_key=photo_ob.name.split(' | ')[0];photo_bb=vr_bounds(photo_ob)
    if photo_key not in photo_garage_bounds:photo_garage_bounds[photo_key]=[list(v) for v in photo_bb]
    else:
        for photo_axis in range(3):
            photo_garage_bounds[photo_key][photo_axis][0]=min(photo_garage_bounds[photo_key][photo_axis][0],photo_bb[photo_axis][0])
            photo_garage_bounds[photo_key][photo_axis][1]=max(photo_garage_bounds[photo_key][photo_axis][1],photo_bb[photo_axis][1])
for photo_ob in list(house.objects):
    if photo_ob.name.startswith(('Garage metal roof','Garage standing seam','Garage gutter')) or (photo_ob.name.startswith('Garage ') and photo_ob.name.endswith(' fascia')):
        bpy.data.objects.remove(photo_ob,do_unlink=True)
photo_gboxes=[]
for photo_key,photo_bb in photo_garage_bounds.items():
    photo_pieces=[([photo_bb[0][0],photo_bb[1][0],2.740],[photo_bb[0][1],photo_bb[1][1],3.630])]
    # The upper house projects over the old garage wall. Trim the new upstand
    # at the actual outside render plane, not the garage's lower-wall extent.
    photo_house_cut=([6.280,-.100,3.140],[27.090,7.980,8.000])
    photo_pieces=[p for b in photo_pieces for p in subtract(b,photo_house_cut)]
    for photo_prior in photo_gboxes:photo_pieces=[p for b in photo_pieces for p in subtract(b,photo_prior)]
    for photo_piece in photo_pieces:
        photo_box(photo_key+' parapet',*photo_piece,photo_brick);photo_gboxes.append(photo_piece)
        if abs(photo_piece[1][2]-3.630)<.00001:
            photo_box(photo_key+' parapet cap',(photo_piece[0][0],photo_piece[0][1],3.630),(photo_piece[1][0],photo_piece[1][1],3.650),roof_metal)
photo_garage_metal=roof_metal.copy();photo_garage_metal.name='VR Garage metal roof'
for photo_name,photo_x0,photo_x1,photo_y0,photo_y1 in [('main',.110,6.279,2.425,9.405),('rear return',6.279,6.508,7.980,9.405)]:
    photo_roof=garage_panel('Garage concealed metal roof '+photo_name,photo_x0,photo_x1,photo_y0,photo_y1,garage_z,lambda y:garage_z(y)+.012,roof_metal)
    photo_roof.data.materials[0]=photo_garage_metal
# Capping is only created above pieces which retain their full height.
photo_report['garage_house_clearance']='New parapet/roof trimmed at upper house outside planeX6.280 and north edgeY7.980; lower garage wall geometry retained.'
photo_report['changes'].append('Garage exposed fascia/eaves replaced by brick parapet and thin metal cap; covering recessed inside veneer.')

# Existing section joints were behind a single opaque leaf. Replace the leaf
# with separate panels and keep the joints in the recessed gaps.
photo_leaf=bpy.data.objects['D03 garage | door leaf'];photo_bb=vr_bounds(photo_leaf)
photo_door_mat=vr_material('VR Garage door neutral metal',(.48,.49,.49))
photo_door_col=photo_leaf.users_collection[0]
photo_step=(photo_bb[2][1]-photo_bb[2][0])/6
for photo_i in range(6):
    photo_low=photo_bb[2][0]+photo_i*photo_step;photo_high=photo_low+photo_step
    photo_box(f'Garage door panel{photo_i+1}',(photo_bb[0][0],photo_bb[1][0],photo_low+.003),
      (photo_bb[0][1],photo_bb[1][1],photo_high-.003),photo_door_mat,photo_door_col)
for photo_ob in list(house.objects):
    if photo_ob.name.startswith('D03 garage | section joint'):bpy.data.objects.remove(photo_ob,do_unlink=True)
for photo_i in range(1,6):
    photo_z=photo_bb[2][0]+photo_i*photo_step
    photo_box(f'Garage door recessed joint{photo_i}',(photo_bb[0][0]+.005,photo_bb[1][0],photo_z-.003),
        (photo_bb[0][1],photo_bb[1][1],photo_z+.003),steel,photo_door_col)
bpy.data.objects.remove(photo_leaf,do_unlink=True)
photo_report['changes'].append('Single garage door slab replaced with six neutral metal panels and five recessed joints.')

# Rails return into the wall rather than ending abruptly beside the stair.
for photo_y,photo_wall in ((6.735,6.660),(7.700,7.775)):
    for photo_u in (.025,arch_stair_run):
        photo_x=arch_stair_foot-photo_u;photo_z=arch_rail_z(photo_u)
        vr_beam('Stair handrail wall return',(photo_x,photo_y,photo_z),(photo_x,photo_wall,photo_z),.045,.050,stairs,oak)
photo_report['changes'].append('Handrail ends return to their wall; open robe towers receive tops at their existing specified2016mm height.')
photo_report['brick_module_m']=[.240,.086]
photo_report['brick_scale_decision']='Retain correctly dimensioned230x76 bricks with10mm joints; Claude visual overscale claim not substantiated by world-space UVs.'
photo_report['bedroom5_strip']='Ray audit hit existing FF Bed5 west lining; no duplicate plaster infill added. Revisit lighting after bake.'
bpy.context.view_layer.update()
photo_intrusions=[]
for photo_ob in house.objects:
    if photo_ob.type!='MESH' or not photo_ob.name.startswith(('Photo revision | Garage','Garage concealed metal roof')):continue
    photo_bb=vr_bounds(photo_ob)
    if all(min(photo_bb[i][1],(26.885,7.775,5.700)[i])-max(photo_bb[i][0],(6.495,.105,3.159)[i])>1e-5 for i in range(3)):
        photo_intrusions.append(photo_ob.name)
assert not photo_intrusions,photo_intrusions
photo_report['new_garage_parts_upper_interior_aabb_check']={'result':'PASS','intrusions':photo_intrusions,'scope':'New garage parts against finished upper-storey interior volume.'}
assert all(bpy.data.objects.get(f'Photo revision | Porch pier{i} cap') for i in range(2))
photo_report['porch_pier_caps']=2
(OUT/'photo-revision.json').write_text(json.dumps(photo_report,indent=2))
changes.append({'object':'Claude photo review response','action':photo_report['changes'],'unresolved':photo_report['unresolved']})
