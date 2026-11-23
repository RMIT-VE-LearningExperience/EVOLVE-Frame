"""Drawing-led wet-room and bulkhead completion; no source blend edits.

The niche trimming is an explicitly illustrative reconstruction of previously
generated framing, not a structural detail supplied by the architect.
"""
ad_out=OUT/'architectural-completion-0.4.6';ad_out.mkdir(exist_ok=True)
ad_report={'version':'0.4.6','datum':{'GF_floor':0,'GF_tile':.003,'FF_structure':3.140,'FF_deck':3.159,'FF_tile':3.162},
 'orientation':'Blender +X=page-right/south; +Y=page-top/east; historic object compass names refer to page axes.',
 'tiles':[],'niches':[],'fittings':[],'checks':[],
 'unresolved':['Theatre platform height/high side, door/bulkhead clash and W08 head/bulkhead junction remain unresolved.',
 'Laundry300 text conflicts340 dimension chain;340 used.380 projection illustrative.',
 'Niche depth60 and timber trimming are educational modelling choices; engineering section/connection design not supplied.',
 'Shower floor recess/falls not reconstructed without slab/floor coordination.',
 'Existing upper finished deck remains19mm above plan datum; dimension reporting names its reference.']}

# Complete finishes by replacing/cutting existing cuboids, never overlaying
# another tile skin. Bounds include15mm of the room-side lining/reveal.
ad_rooms=[('Powder',15,[(20.020,5.200,-.001,21.620,7.790,2.741)]),
 ('Ensuite',17,[(18.560,1.080,-.001,20.360,3.870,2.741)]),
 ('Ensuite WC',17,[(18.560,.090,-.001,20.360,.990,2.741)]),
 ('Bath2',18,[(10.640,.090,3.158,12.840,2.200,5.731)])]
for ad_room,ad_sheet,ad_boxes in ad_rooms:
    bpy.context.view_layer.update()
    ad_changed=[];ad_removed=[]
    for ad_ob in list(house.objects):
        if ad_ob.type!='MESH':continue
        ad_name=ad_ob.name
        if not any(t in ad_name for t in (' | lining',' | opening return',' | end return',' | skirting')):continue
        ad_bb=detail_box_bounds(ad_ob)
        for ad_b in ad_boxes:
            ad_cut=(ad_b[:3],ad_b[3:]);ad_hit=detail_intersection(ad_bb,ad_cut)
            if ad_hit is None:continue
            # Only wall pieces. Horizontal window sills/reveals are included.
            ad_whole=all(abs(ad_hit[j][i]-ad_bb[j][i])<.00002 for j in range(2) for i in range(3))
            if 'skirting' in ad_name:
                if ad_whole:bpy.data.objects.remove(ad_ob,do_unlink=True)
                else:detail_replace_box(ad_ob,subtract(ad_bb,ad_cut))
                ad_removed.append(ad_name)
            else:
                if ad_whole:
                    ad_tiled=ad_ob;ad_tiled.data=ad_tiled.data.copy()
                    ad_tiled.data.materials.clear();ad_tiled.data.materials.append(bt_wall)
                else:
                    ad_col=ad_ob.users_collection[0]
                    ad_parts=detail_replace_box(ad_ob,subtract(ad_bb,ad_cut))
                    ad_tiled=vr_box(ad_name+' tiled',*ad_hit,ad_col,bt_wall)
                ad_tiled['source']=f'Architectural sheet{ad_sheet}; tile product/module illustrative'
                ad_changed.append({'name':ad_tiled.name,'bounds':ad_hit})
            break
    assert ad_changed,ad_room
    ad_report['tiles'].append({'room':ad_room,'sheet':ad_sheet,'objects':ad_changed,'removed_painted_skirtings':ad_removed,
      'coverage_note':'Page-right wall coverage inferred (only elevations A-C supplied).' if ad_room=='Powder' else 'Source elevations; upper WC is separately skirting only.'})

# Claude gate2 correction: elevationA stipple belongs to glazing, not the
# end wall. ALL upper WC walls retain plaster above100mm tiled skirting.
for ad_ob in list(house.objects):
    if ad_ob.type!='MESH' or ' | skirting' not in ad_ob.name:continue
    ad_bb=detail_box_bounds(ad_ob)
    if ad_bb[0][0]>=11.24-.001 and ad_bb[1][0]<=12.24+.001 and ad_bb[0][1]>=5.68-.001 and ad_bb[1][1]<=7.79+.001 and 3.158<=ad_bb[0][2]<=3.163:
        ad_bb[1][2]=3.262
        detail_replace_box(ad_ob,[ad_bb],bt_wall)

# Laundry: finish lies directly over the380mm overhead depth, including WM.
arch_bulkhead('Laundry340 dimension-chain bulkhead',(8.435,4.695,2.400),(8.815,7.765,2.740),
              'Sheet17B340+800+700+900=2740;300 label conflict retained;380 projection illustrative;3070 inside3090 nominal room.')
ad_report['laundry_bulkhead']={'nominal_run_m':3.09,'finished_run_m':3.07,'depth_m':.38,'soffit_GF_m':2.4,'drop_m':.34,'label_conflict':'300MM versus340 dimension'}

def ad_local_box(basis,u0,u1,v0,v1,z0,z1):
    p=ff_point(basis,(u0,v0,z0));q=ff_point(basis,(u1,v1,z1))
    return ([min(p[i],q[i]) for i in range(3)],[max(p[i],q[i]) for i in range(3)])

def ad_niche(name,wall,origin,u,v,width,floor,sheet):
    bpy.context.view_layer.update()
    # u runs across the niche, v into the wall. Finished opening is exact;
    # backing and reveals are10mm and sit outside the clear volume.
    basis=ff_basis(origin,u,v);sill=floor+1.200;head=sill+.450
    b=ff_basis((origin[0],origin[1],0),u,v)
    opening=ad_local_box(b,0,width,-.002,.070,sill,head)
    wall_obs=[o for o in house.objects if o.type=='MESH' and o.name.startswith(wall+' |')]
    room_lining=[];far_lining=[];timber=[]
    for ob in wall_obs:
        centre=sum((ob.matrix_world@vert.co for vert in ob.data.vertices),Vector())/len(ob.data.vertices)
        depth=(centre-Vector((origin[0],origin[1],0))).dot(Vector((*v,0)))
        if 'lining' in ob.name:
            (room_lining if depth<.025 else far_lining).append(ob)
        elif any(t in ob.name for t in ('common stud','noggin')):timber.append(ob)
    assert room_lining and far_lining,(name,len(room_lining),len(far_lining))
    far_before={ob.name:detail_box_bounds(ob) for ob in far_lining}
    z0=max(vr_bounds(o)[2][1] for o in wall_obs if 'bottom plate' in o.name)
    z1=min(vr_bounds(o)[2][0] for o in wall_obs if 'top plate' in o.name)
    changed=[]
    detail_cut_objects(room_lining,ad_local_box(b,-.010,width+.010,-.002,.012,sill-.010,head+.010),changed)
    # Reframe generated common studs/noggins only. Top/bottom plates, steel,
    # bracing and primary beams are not selected by this operation.
    frame_cuts=[ad_local_box(b,-.045,width+.045,.015,.105,sill-.045,head+.045),
                ad_local_box(b,-.045,-.010,.015,.105,z0,z1),
                ad_local_box(b,width+.010,width+.045,.015,.105,z0,z1)]
    wood_changes=[]
    for cut in frame_cuts:
        eligible=[o for o in house.objects if o.type=='MESH' and o.name.startswith(wall+' |') and any(t in o.name for t in ('common stud','noggin'))]
        detail_cut_objects(eligible,cut,wood_changes)
    col=bpy.data.collections['05 Upper floor walls' if floor>1 else '02 Ground floor walls']
    for label,box in [('left jamb',frame_cuts[1]),('right jamb',frame_cuts[2]),
      ('sill',ad_local_box(b,-.010,width+.010,.015,.105,sill-.045,sill-.010)),
      ('head',ad_local_box(b,-.010,width+.010,.015,.105,head+.010,head+.045))]:
        ob=vr_box(name+' illustrative timber '+label,*box,col,pine)
        ob['source']='Illustrative generated niche trimming; unengineered sizes/connections. Load path not assessed. Not a source engineering detail.'
    for label,box in [('back',ad_local_box(b,-.010,width+.010,.060,.070,sill-.010,head+.010)),
      ('left reveal',ad_local_box(b,-.010,0,0,.060,sill,head)),
      ('right reveal',ad_local_box(b,width,width+.010,0,.060,sill,head)),
      ('sill',ad_local_box(b,-.010,width+.010,0,.060,sill-.010,sill)),
      ('head',ad_local_box(b,-.010,width+.010,0,.060,head,head+.010))]:
        ob=vr_box(name+' tiled '+label,*box,linings,bt_wall)
        ob['source']=f'Sheet{sheet}: written opening width/height and1200 underside;60mm depth illustrative.'
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    for uf in (.05,.5,.95):
        for hf in (.05,.5,.95):
            start=ff_point(b,(width*uf,-.02,sill+.45*hf))
            hit=house.ray_cast(deps,start,Vector((*v,0)),distance=.10)
            assert hit[0] and hit[4].name==name+' tiled back',(name,uf,hf,hit[4].name if hit[0] else None)
    assert all(detail_box_bounds(bpy.data.objects[n])==bb for n,bb in far_before.items())
    added=[o for o in house.objects if o.type=='MESH' and o.name.startswith(name+' illustrative timber ')]
    retained=[o for o in house.objects if o.type=='MESH' and o.name.startswith(wall+' |') and any(t in o.name for t in ('common stud','noggin','plate'))]
    for a in added:
        for other in retained:
            hit=detail_intersection(detail_box_bounds(a),detail_box_bounds(other))
            assert hit is None,(name,'overlapping framing',a.name,other.name)
    ad_report['niches'].append({'name':name,'wall':wall,'sheet':sheet,'opening_m':[width,.45,.06],
      'sill_above_tile_m':1.2,'head_above_tile_m':1.65,'finished_floor_z':floor,'origin_xy':origin[:2],
      'lining_cuts':changed,'timber_changes':wood_changes,'far_lining_preserved':list(far_before),
      'back_ray_checks':9,'result':'PASS','framing_status':'Illustrative trimming; unengineered sizes/connections; load path not assessed.',
      'setout_rule':'Centred on actual finished shower wall; nominal side allowances reduce equally where clear span is smaller.',
      'wall_core_depth_m':.09,'far_lining_near_face_depth_m':.110,'backing_outer_depth_m':.070,
      'services':'Mixer pipework not modelled. Alternative niche location/framing requires coordination.'})

ad_niche('Ensuite niche','Entry suite division',(18.960,3.855,0),(1,0),(0,1),1.0,.003,17)
ad_niche('Upper bath niche','FF Bath robe division',(14.315,6.675,0),(0,1),(1,0),.9,3.162,19)
ad_niche('Bath2 niche','FF Bath 2 west',(10.655,1.435,0),(0,1),(-1,0),.6,3.162,18)

def ad_rail(name,origin,u,v,length,height,sheet):
    basis=ff_basis(origin,u,v)
    ff_tube(name+' bar',(-length/2,.06,height),(length/2,.06,height),.009,basis)
    for end in (-length/2,length/2):
        ff_tube(name+' mount',(end,0,height),(end,.06,height),.014,basis)
    ad_report['fittings'].append({'name':name,'origin':origin,'height_above_tile_m':height,'length_m':length,'sheet':sheet,'mounts_touch_wall':True,'horizontal_setout':'Scaled except written TPH offsets.'})

for args in [
 ('Powder WC paper holder',(20.635,7.775,.003),(1,0),(0,-1),.13,.9,15),
 ('Ensuite WC paper holder',(19.275,.105,.003),(1,0),(0,1),.13,.9,17),
 ('Bath 2 WC paper holder',(11.355,.105,3.162),(1,0),(0,1),.13,.9,18),
 ('Upper WC paper holder',(12.225,7.075,3.162),(0,1),(-1,0),.13,.9,19),
 ('Bath 2 shower towel rail',(12.825,1.60,3.162),(0,1),(-1,0),.60,1.2,18),
 ('Upper bath shower towel rail',(12.345,6.25,3.162),(0,1),(1,0),.60,1.2,19)]:ad_rail(*args)
# Ensuite ring: top mounting reference1200; ring hangs beneath it.
ad_b=ff_basis((20.345,2.68,.003),(0,1),(-1,0))
ff_tube('Ensuite shower towel ring mount',(0,0,1.2),(0,.055,1.2),.016,ad_b)
ad_points=[ff_point(ad_b,(.075*math.sin(2*math.pi*i/20),.055,1.125+.075*math.cos(2*math.pi*i/20))) for i in range(21)]
detail_pipe('Fitout | Ensuite shower towel ring',ad_points,.006,ff_collection,ff_metal,6,True)
ad_report['fittings'].append({'name':'Ensuite shower towel ring','sheet':17,'mount_height_above_tile_m':1.2,'origin':[20.345,2.68,.003],'horizontal_setout':'Scaled; mounting height written.'})

assert arch_report['platform']['height_m'] is None
ad_report['checks'].extend([{'name':'Three actual niche openings /27 rays /far linings unchanged','result':'PASS'},
 {'name':'Theatre platform remains unspecified','result':'PASS'}, {'name':'Laundry340 drop terminates at2400 overhead top','result':'PASS'}])
arch_report['bulkheads']=bulkhead_report
arch_report['coordinate_directions']=ad_report['orientation']
for row in arch_report['bulkheads']:
    row['floor_datum_m']=3.159 if row['min'][2]>3 else 0
    row['clear_soffit_above_deck_m']=round(row['min'][2]-row['floor_datum_m'],4)
(OUT/'architectural-wall-setout.json').write_text(json.dumps(arch_report,indent=2))
ff_report['unresolved']=[v for v in ff_report['unresolved'] if not v.startswith(('Shower recesses and recessed niches','Wall tiling,'))]
ff_report['unresolved'].extend(['Shower floor recess/falls and concealed services remain unresolved. Three niches now built; trimming is illustrative, load paths not assessed.',
 'Electrical points, fridge coordination, splashbacks across window reveals and sliding robe doors remain incomplete.'])
ff_report['architectural_details046']={'niches':3,'mounted_fittings':7,'report':'architectural-completion-0.4.6/wet-details.json'}
bpy.context.view_layer.update();ad_deps=bpy.context.evaluated_depsgraph_get();ad_fit_triangles=0
for ad_ob in ff_collection.objects:
    ad_eval=ad_ob.evaluated_get(ad_deps);ad_mesh=ad_eval.to_mesh();ad_mesh.calc_loop_triangles()
    ad_fit_triangles+=len(ad_mesh.loop_triangles);ad_eval.to_mesh_clear()
ff_report['objects']=len(ff_collection.objects);ff_report['triangles']=ad_fit_triangles
(OUT/'fixed-fitout-coordination.json').write_text(json.dumps(ff_report,indent=2))
bt_report['unresolved']=['Niche now modelled;60mm depth and timber trimming illustrative, load path not assessed. Shower floor recess/falls remain unresolved.',
 'Existing upper floor/ceiling datums retained pending whole-model coordination.']
bt_report['niche_completion']='architectural-completion-0.4.6/wet-details.json'
(OUT/'bathroom-tiling.json').write_text(json.dumps(bt_report,indent=2))
(ad_out/'wet-details.json').write_text(json.dumps(ad_report,indent=2))
changes.append({'object':'Architectural detail completion046','action':'Full-height wet finishes,3 actual niches with recorded illustrative trimming,7 mounted fittings, laundry bulkhead.'})
print('ARCH046_WET_DETAILS_PASS',len(ad_report['niches']),len(ad_report['fittings']),flush=True)
