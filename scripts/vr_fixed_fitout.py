"""Lightweight fixed fitout from architectural sheets 15-19.

Written overall sizes govern; product shapes and undimensioned positions are
illustrative. This runs in the legacy shared namespace, so every symbol is ff_.
"""
ff_collection=bpy.data.collections.new('27 Fixed joinery and fixtures')
house.collection.children.link(ff_collection)
ff_report={'source_sheets':[7,8,15,16,17,18,19],'author':'Codex; informed by Claude architectural review',
 'scope':'Fixed fixtures and joinery; not fabrication, plumbing or architectural acceptance.',
 'items':[], 'unresolved':[
 'Kitchen absolute start and pantry/ref return require exterior-wall reconciliation. Ref width conflicts between plan and elevation; ref fitout is deferred.',
 'Shower recesses and recessed niches require coordinated wall/floor openings; not represented by surface-mounted fake niches.',
 'Basin, tap, WC and appliance product shapes and joinery finishes are illustrative; no product specification is supplied.',
 'Mirrors use separate material batches for static Unity reflection probes; no live planar reflection rendering.',
 'Wall tiling, electrical points, fridge water point, splashbacks across window reveals and sliding robe doors remain incomplete.'
 ]}
ff_white=vr_material('VR Fitout warm white cabinetry',(.81,.80,.76))
ff_stone=vr_material('VR Fitout honed pale stone',(.77,.76,.71))
ff_ceramic=vr_material('VR Fitout white ceramic',(.91,.92,.90))
ff_metal=vr_material('VR Fitout brushed nickel',(.55,.58,.58))
ff_dark=vr_material('VR Fitout charcoal appliance',(.048,.056,.059))
ff_mirror=vr_material('VR Fitout mirror silver',(.69,.74,.75))
ff_tile=vr_material('VR Fitout floor porcelain',(.67,.66,.63))
ff_glass=vr_material('VR Fitout clear shower glass',(.7,.85,.88))
ff_oak=vr_material('VR Fitout pale oak',(.66,.53,.37))
for ff_mat,ff_rough,ff_metallic in [(ff_stone,.35,0),(ff_ceramic,.16,0),(ff_metal,.28,.8),
 (ff_dark,.25,0),(ff_mirror,.16,.95),(ff_glass,.1,0)]:
    ff_bs=ff_mat.node_tree.nodes.get('Principled BSDF')
    ff_bs.inputs['Roughness'].default_value=ff_rough
    ff_bs.inputs['Metallic'].default_value=ff_metallic

def ff_basis(ff_origin,ff_u=(1,0),ff_v=(0,1)):
    return (Vector(ff_origin),Vector((*ff_u,0)),Vector((*ff_v,0)))

def ff_point(ff_basis_value,ff_xyz):
    return ff_basis_value[0]+ff_basis_value[1]*ff_xyz[0]+ff_basis_value[2]*ff_xyz[1]+Vector((0,0,ff_xyz[2]))

def ff_tag(ff_object,ff_sheet):
    ff_object['source']='Architectural sheets '+str(ff_sheet)
    ff_object['source_status']='Written overall dimensions; illustrative product shape and scaled absolute setout'
    return ff_object

def ff_box(ff_name,ff_lo,ff_hi,ff_basis_value,ff_material=ff_white,ff_bevel=False):
    ff_corners=[ff_point(ff_basis_value,(ff_x,ff_y,ff_z)) for ff_x in (ff_lo[0],ff_hi[0])
                for ff_y in (ff_lo[1],ff_hi[1]) for ff_z in (ff_lo[2],ff_hi[2])]
    assert min(ff_hi[ff_i]-ff_lo[ff_i] for ff_i in range(3))>0,ff_name
    ff_object=vr_mesh('Fitout | '+ff_name,ff_corners,
        [(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)],ff_collection,ff_material)
    ff_tag(ff_object,'15-19')
    if ff_bevel:
        ff_modifier=ff_object.modifiers.new('Small finished edge','BEVEL')
        ff_modifier.width=.0015;ff_modifier.segments=1
    return ff_object

def ff_tube(ff_name,ff_a,ff_b,ff_radius,ff_basis_value,ff_material=ff_metal,ff_sides=10):
    ff_start=ff_point(ff_basis_value,ff_a);ff_end=ff_point(ff_basis_value,ff_b)
    ff_axis=(ff_end-ff_start).normalized()
    ff_cross=ff_axis.cross(Vector((0,0,1)) if abs(ff_axis.z)<.9 else Vector((1,0,0))).normalized()
    ff_other=ff_axis.cross(ff_cross)
    ff_vertices=[ff_p+ff_radius*(math.cos(2*math.pi*ff_i/ff_sides)*ff_cross+math.sin(2*math.pi*ff_i/ff_sides)*ff_other)
        for ff_p in (ff_start,ff_end) for ff_i in range(ff_sides)]
    ff_faces=[tuple(range(ff_sides-1,-1,-1)),tuple(range(ff_sides,ff_sides*2))]
    ff_faces.extend((ff_i,(ff_i+1)%ff_sides,(ff_i+1)%ff_sides+ff_sides,ff_i+ff_sides) for ff_i in range(ff_sides))
    ff_object=vr_mesh('Fitout | '+ff_name,ff_vertices,ff_faces,ff_collection,ff_material)
    for ff_face in ff_object.data.polygons[2:]:ff_face.use_smooth=True
    return ff_tag(ff_object,'15-19')

def ff_rings(ff_name,ff_centre,ff_profile,ff_basis_value,ff_material=ff_ceramic,ff_sides=32):
    # Elliptical closed section: profile entries are radius-u, radius-v, height.
    ff_vertices=[ff_point(ff_basis_value,(ff_centre[0]+ff_ru*math.cos(2*math.pi*ff_i/ff_sides),
        ff_centre[1]+ff_rv*math.sin(2*math.pi*ff_i/ff_sides),ff_centre[2]+ff_z))
        for ff_ru,ff_rv,ff_z in ff_profile for ff_i in range(ff_sides)]
    ff_faces=[]
    for ff_j in range(len(ff_profile)-1):
        ff_faces.extend((ff_j*ff_sides+ff_i,ff_j*ff_sides+(ff_i+1)%ff_sides,
            (ff_j+1)*ff_sides+(ff_i+1)%ff_sides,(ff_j+1)*ff_sides+ff_i) for ff_i in range(ff_sides))
    if ff_profile[0]!=ff_profile[-1]:
        ff_faces.extend([tuple(range(ff_sides-1,-1,-1)),tuple(range((len(ff_profile)-1)*ff_sides,len(ff_profile)*ff_sides))])
    ff_object=vr_mesh('Fitout | '+ff_name,ff_vertices,ff_faces,ff_collection,ff_material)
    for ff_face in (ff_object.data.polygons if ff_profile[0]==ff_profile[-1] else ff_object.data.polygons[:-2]):ff_face.use_smooth=True
    return ff_tag(ff_object,'15-19')

def ff_tap(ff_name,ff_u,ff_v,ff_z,ff_basis_value):
    ff_tube(ff_name+' stem',(ff_u,ff_v,ff_z),(ff_u,ff_v,ff_z+.22),.018,ff_basis_value)
    ff_tube(ff_name+' spout',(ff_u,ff_v,ff_z+.22),(ff_u,ff_v+.15,ff_z+.22),.013,ff_basis_value)
    ff_tube(ff_name+' outlet',(ff_u,ff_v+.15,ff_z+.22),(ff_u,ff_v+.15,ff_z+.19),.014,ff_basis_value)
    ff_box(ff_name+' lever',(ff_u+.018,ff_v-.02,ff_z+.13),(ff_u+.028,ff_v+.08,ff_z+.15),ff_basis_value,ff_metal)

def ff_sink_bowl(ff_name,ff_centre,ff_basis_value,ff_halfwidth=.205):
    # A rectangular rim closes the actual worktop cutout; elliptical inner walls
    # form the bowl. No open triangular gaps around an oval dropped into a box.
    ff_outline=[(1,0),(1,.5),(1,1),(.5,1),(0,1),(-.5,1),(-1,1),(-1,.5),
                (-1,0),(-1,-.5),(-1,-1),(-.5,-1),(0,-1),(.5,-1),(1,-1),(1,-.5)]
    ff_vertices=[]
    for ff_ring in range(4):
        for ff_a,ff_b in ff_outline:
            ff_angle=math.atan2(ff_b,ff_a)
            if ff_ring in (0,3):ff_x,ff_y,ff_z=ff_a*ff_halfwidth,ff_b*.22,(.001 if ff_ring==0 else -.145)
            else:ff_x,ff_y,ff_z=math.cos(ff_angle)*(ff_halfwidth-.025 if ff_ring==1 else ff_halfwidth-.075),math.sin(ff_angle)*(.19 if ff_ring==1 else .13),(.001 if ff_ring==1 else -.14)
            ff_vertices.append(ff_point(ff_basis_value,(ff_centre[0]+ff_x,ff_centre[1]+ff_y,ff_centre[2]+ff_z)))
    ff_faces=[]
    for ff_ring in range(4):
        ff_next=(ff_ring+1)%4
        for ff_i in range(16):ff_faces.append((ff_ring*16+ff_i,ff_ring*16+(ff_i+1)%16,ff_next*16+(ff_i+1)%16,ff_next*16+ff_i))
    # Inner floor and exterior bottom, leaving the top open.
    ff_faces.append(tuple(range(32,48)))
    ff_faces.append(tuple(range(63,47,-1)))
    # The inner floor seals at ring2; exterior bottom seals at ring3.
    # Remove their connecting side ring, which would duplicate the bottom volume.
    ff_faces=ff_faces[:32]+ff_faces[48:]
    ff_object=vr_mesh('Fitout | '+ff_name,ff_vertices,ff_faces,ff_collection,ff_metal)
    for ff_face in ff_object.data.polygons[16:32]:ff_face.use_smooth=True
    return ff_tag(ff_object,16)

def ff_pull(ff_name,ff_a,ff_b,ff_face,ff_basis_value):
    ff_tube(ff_name,ff_a,ff_b,.005,ff_basis_value)
    # Short posts attach the bar to the actual door face instead of floating.
    for ff_j,ff_end in enumerate((ff_a,ff_b)):
        ff_tube(ff_name+' mounting post '+str(ff_j+1),
            (ff_end[0],ff_face,ff_end[2]),ff_end,.004,ff_basis_value,ff_metal,6)

def ff_cabinet(ff_name,ff_u,ff_width,ff_depth,ff_z0,ff_z1,ff_basis_value,ff_drawers=0,ff_open=False):
    ff_box(ff_name+' left',(ff_u,0,ff_z0),(ff_u+.018,ff_depth,ff_z1),ff_basis_value)
    ff_box(ff_name+' right',(ff_u+ff_width-.018,0,ff_z0),(ff_u+ff_width,ff_depth,ff_z1),ff_basis_value)
    ff_box(ff_name+' back',(ff_u+.018,0,ff_z0),(ff_u+ff_width-.018,.009,ff_z1),ff_basis_value)
    ff_box(ff_name+' base',(ff_u+.018,.009,ff_z0),(ff_u+ff_width-.018,ff_depth,ff_z0+.018),ff_basis_value)
    if ff_open:
        ff_box(ff_name+' top',(ff_u+.018,.009,ff_z1-.018),(ff_u+ff_width-.018,ff_depth,ff_z1),ff_basis_value)
        for ff_height in (.45,.90,1.35,1.80):
            if ff_z0<ff_height<ff_z1-.02:ff_box(ff_name+' shelf',(ff_u+.018,.009,ff_height),(ff_u+ff_width-.018,ff_depth,ff_height+.018),ff_basis_value)
        return
    if ff_drawers:
        ff_count=ff_drawers;ff_delta=(ff_z1-ff_z0)/ff_count
        for ff_i in range(ff_count):
            ff_low=ff_z0+ff_i*ff_delta+.002;ff_high=ff_z0+(ff_i+1)*ff_delta-.002
            ff_box(ff_name+' drawer '+str(ff_i+1),(ff_u+.002,ff_depth,ff_low),(ff_u+ff_width-.002,ff_depth+.018,ff_high),ff_basis_value,ff_white,True)
            ff_pull(ff_name+' pull '+str(ff_i+1),(ff_u+ff_width/2-.09,ff_depth+.033,ff_high-.04),(ff_u+ff_width/2+.09,ff_depth+.033,ff_high-.04),ff_depth+.018,ff_basis_value)
    else:
        ff_count=2 if ff_width>.65 else 1
        for ff_i in range(ff_count):
            ff_left=ff_u+ff_i*ff_width/ff_count+.002;ff_right=ff_u+(ff_i+1)*ff_width/ff_count-.002
            ff_box(ff_name+' door '+str(ff_i+1),(ff_left,ff_depth,ff_z0+.002),(ff_right,ff_depth+.018,ff_z1-.002),ff_basis_value,ff_white,True)
            # Wall cupboards are gripped from below, base cupboards from above.
            # Tall doors use a reachable intermediate position. These offsets
            # are illustrative hardware choices, not dimensions on sheet 16.
            ff_handle_z=ff_z0+.15 if ff_z0>=1.5 else (1.10 if ff_z1-ff_z0>1.8 else ff_z1-.15)
            ff_handle_u=ff_left+.035 if ff_count==2 and ff_i==1 else ff_right-.035
            ff_pull(ff_name+' pull '+str(ff_i+1),(ff_handle_u,ff_depth+.032,ff_handle_z-.07),
                (ff_handle_u,ff_depth+.032,ff_handle_z+.07),ff_depth+.018,ff_basis_value)

def ff_vanity(ff_name,ff_origin,ff_u,ff_v,ff_width,ff_bottom=0,ff_double=False,ff_sheet=15):
    ff_b=ff_basis(ff_origin,ff_u,ff_v)
    ff_cabinet(ff_name,0,ff_width,.575,ff_bottom,.8,ff_b)
    ff_box(ff_name+' stone',(0,0,.8),(ff_width,.6,.82),ff_b,ff_stone,True)
    ff_box(ff_name+' mirror backing',(.02,0,1.02),(ff_width-.02,.01,2.12),ff_b,ff_white)
    ff_room_mirror=ff_mirror.copy();ff_room_mirror.name='VR Fitout mirror '+ff_name
    ff_box(ff_name+' mirror',(.03,.01,1.03),(ff_width-.03,.014,2.11),ff_b,ff_room_mirror)
    for ff_c in ([ff_width*.25,ff_width*.75] if ff_double else [ff_width/2]):
        ff_rings(ff_name+' basin',(ff_c,.34,.82),[(.17,.12,0),(.23,.17,.08),(.205,.145,.08),(.13,.08,.015)],ff_b)
        ff_tap(ff_name+' mixer',ff_c,.12,.82,ff_b)
    ff_report['items'].append({'name':ff_name,'sheet':ff_sheet,'width_m':ff_width,'depth_m':.6,'cabinet_top_m':.8,
        'floor_clearance_m':ff_bottom,'origin':ff_origin,'basis':'Written nominal width/depth; absolute position and vessel-basin product form illustrative.'})

def ff_toilet(ff_name,ff_origin,ff_direction,ff_sheet):
    ff_v=Vector((*ff_direction,0));ff_u=Vector((ff_v.y,-ff_v.x,0))
    ff_b=ff_basis(ff_origin,ff_u.xy,ff_v.xy)
    ff_rings(ff_name+' pedestal and open pan',(0,.39,0),[(.11,.14,.005),(.125,.16,.15),(.18,.24,.36),(.19,.26,.405),(.145,.20,.405),(.08,.10,.22)],ff_b)
    ff_rings(ff_name+' seat',(0,.39,0),[(.192,.262,.412),(.192,.262,.432),(.145,.2,.432),(.145,.2,.412),(.192,.262,.412)],ff_b)
    ff_box(ff_name+' cistern',(-.185,.015,.37),(.185,.18,.80),ff_b,ff_ceramic,True)
    ff_box(ff_name+' cistern lid',(-.19,.01,.80),(.19,.185,.82),ff_b,ff_ceramic,True)
    ff_tube(ff_name+' flush',(0,.10,.821),(0,.10,.825),.024,ff_b)
    ff_report['items'].append({'name':ff_name,'sheet':ff_sheet,'origin':ff_origin,'direction':ff_direction,
        'basis':'WC location from drawn plan; 380 x 650 mm nominal product envelope, not a selected product.'})

def ff_tiles(ff_name,ff_lo,ff_hi,ff_floor):
    ff_b=ff_basis((0,0,ff_floor))
    # One continuous finish prevents individual tile lightmap islands and open
    # joints exposing the oak deck. The mobile material draws the narrow grout.
    ff_box(ff_name+' tiled floor',(ff_lo[0],ff_lo[1],0),
        (ff_hi[0],ff_hi[1],.003),ff_b,ff_tile)

def ff_shower(ff_name,ff_lo,ff_hi,ff_floor,ff_sheet,ff_glass_west=False):
    ff_b=ff_basis((0,0,ff_floor));ff_x0,ff_y0=ff_lo;ff_x1,ff_y1=ff_hi
    ff_box(ff_name+' drain',(ff_x0+.08,ff_y1-.075,.003),(ff_x1-.08,ff_y1-.035,.005),ff_b,ff_metal)
    ff_mid=(ff_x0+ff_x1)/2
    # Sheets18/19 show the hinged door in a SIDE screen, not the front.
    # A700 nominal leaf leaves a200/600 fixed side panel respectively.
    ff_front0=19.475 if ff_sheet==17 else ff_x0
    ff_box(ff_name+' front glass',(ff_front0+.003,ff_y0,.009),(ff_x1-.003,ff_y0+.008,1.996),ff_b,ff_glass)
    ff_box(ff_name+' threshold',(ff_front0,ff_y0-.004,.003),(ff_x1,ff_y0+.012,.009),ff_b,ff_metal)
    ff_box(ff_name+' front top trim',(ff_front0,ff_y0,1.996),(ff_x1,ff_y0+.008,2.006),ff_b,ff_metal)
    if ff_sheet!=17:
        ff_side=ff_x0 if ff_sheet==19 else ff_x1-.008
        ff_split=ff_y1-.700
        ff_box(ff_name+' fixed side glass',(ff_side,ff_y0+.008,.009),(ff_side+.008,ff_split-.003,1.996),ff_b,ff_glass)
        ff_box(ff_name+' hinged side glass',(ff_side,ff_split+.003,.009),(ff_side+.008,ff_y1-.003,1.996),ff_b,ff_glass)
        ff_box(ff_name+' side top trim',(ff_side,ff_y0+.008,1.996),(ff_side+.008,ff_y1,2.006),ff_b,ff_metal)
        ff_face=ff_x0 if ff_sheet==19 else ff_x1
        ff_grip=ff_face+(-.025 if ff_sheet==19 else .025)
        ff_pull_y=ff_split+.065
        ff_tube(ff_name+' door pull',(ff_grip,ff_pull_y,.95),(ff_grip,ff_pull_y,1.15),.007,ff_b)
        for ff_z in (.95,1.15):
            ff_tube(ff_name+' pull mounting post',(ff_face,ff_pull_y,ff_z),(ff_grip,ff_pull_y,ff_z),.005,ff_b)
        for ff_z in (.35,1.65):
            ff_box(ff_name+' door hinge',(ff_side-.010,ff_y1-.045,ff_z),(ff_side+.018,ff_y1,ff_z+.065),ff_b,ff_metal)
    else:
        # The900 nib forms the west half of the ensuite's south boundary.
        ff_pull(ff_name+' door pull',(ff_front0+.065,ff_y0-.025,.95),
            (ff_front0+.065,ff_y0-.025,1.15),ff_y0,ff_b)
        for ff_z in (.35,1.65):
            ff_box(ff_name+' door hinge',(ff_x1-.045,ff_y0-.010,ff_z),(ff_x1,ff_y0+.018,ff_z+.065),ff_b,ff_metal)
    if ff_sheet==17:
        # Sheet17: west-wall rose; mixer on the north wall550 from west.
        ff_rose_y=(ff_y0+ff_y1)/2
        ff_tube(ff_name+' riser',(ff_x0+.045,ff_rose_y,1.0),(ff_x0+.045,ff_rose_y,1.80),.009,ff_b)
        ff_tube(ff_name+' rose arm',(ff_x0+.045,ff_rose_y,1.80),(ff_x0+.22,ff_rose_y,1.80),.012,ff_b)
        ff_box(ff_name+' rose',(ff_x0+.14,ff_rose_y-.07,1.78),(ff_x0+.28,ff_rose_y+.07,1.80),ff_b,ff_metal)
        ff_mixer_x=ff_x0+.550;ff_mixer_z=1.0
        for ff_z in (1.1,1.7):ff_tube(ff_name+' riser mount',(ff_x0+.012,ff_rose_y,ff_z),(ff_x0+.045,ff_rose_y,ff_z),.012,ff_b)
    else:
        ff_tube(ff_name+' riser',(ff_mid,ff_y1-.045,1.05),(ff_mid,ff_y1-.045,1.80),.009,ff_b)
        ff_tube(ff_name+' rose arm',(ff_mid,ff_y1-.045,1.80),(ff_mid,ff_y1-.22,1.80),.012,ff_b)
        ff_box(ff_name+' rose',(ff_mid-.07,ff_y1-.28,1.78),(ff_mid+.07,ff_y1-.14,1.80),ff_b,ff_metal)
        ff_mixer_x=ff_x1-.650 if ff_sheet==19 else ff_x0+.650;ff_mixer_z=1.05
        for ff_z in (1.15,1.7):ff_tube(ff_name+' riser mount',(ff_mid,ff_y1-.012,ff_z),(ff_mid,ff_y1-.045,ff_z),.012,ff_b)
    ff_tube(ff_name+' mixer',(ff_mixer_x,ff_y1-.012,ff_mixer_z),(ff_mixer_x,ff_y1-.060,ff_mixer_z),.035,ff_b)
    ff_box(ff_name+' mixer lever',(ff_mixer_x-.010,ff_y1-.070,ff_mixer_z),
        (ff_mixer_x+.010,ff_y1-.050,ff_mixer_z+.075),ff_b,ff_metal)
    ff_report['items'].append({'name':ff_name,'sheet':ff_sheet,'bounds_xy':[ff_lo,ff_hi],'screen_height_m':2,
        'mixer_position':[ff_mixer_x,ff_y1,ff_floor+ff_mixer_z],
        'door_side':'south beside nib' if ff_sheet==17 else ('west' if ff_sheet==19 else 'east'),
        'basis':'Sheets17-19 door swings, mixer offsets/heights; closed screen with mounted hardware. Product shapes illustrative. Recessed base/niche not yet coordinated.'})

# Kitchen, sheet 16. The 330 mm pipe stack precedes the 6890 mm run.
ff_kitchen=ff_basis((13.04,7.775,0),(1,0),(0,-1))
ff_modules=[(.9,2,'Drawer A'),(.9,0,'Cooktop'),(.9,2,'Drawer B'),(.6,0,'Bin'),(.89,0,'Sink'),(.6,0,'Dishwasher'),(.9,2,'Drawer C'),(1.1,0,'Tall pantry')]
ff_cursor=.02
for ff_width,ff_drawers,ff_label in ff_modules:
    if ff_label=='Dishwasher':
        ff_cursor+=.02
        ff_box('Kitchen dishwasher',(ff_cursor,.03,.03),(ff_cursor+ff_width-.008,.60,.86),ff_kitchen,ff_metal,True)
        ff_box('Dishwasher controls',(ff_cursor+.02,.60,.79),(ff_cursor+ff_width-.028,.605,.845),ff_kitchen,ff_dark)
    else:
        ff_cabinet('Kitchen '+ff_label,ff_cursor,ff_width,.58,.10,2.4 if ff_label=='Tall pantry' else .865,ff_kitchen,ff_drawers)
        ff_box('Kitchen '+ff_label+' plinth',(ff_cursor,.025,0),(ff_cursor+ff_width,.55,.10),ff_kitchen,ff_white)
    if ff_label=='Cooktop':
        ff_box('Kitchen cooktop',(ff_cursor+.02,.07,.905),(ff_cursor+ff_width-.02,.54,.916),ff_kitchen,ff_dark,True)
        for ff_cx in (ff_cursor+.23,ff_cursor+.66):
            for ff_cy in (.20,.43):
                ff_rings('Cooktop ring',(ff_cx,ff_cy,.917),[(.075,.075,0),(.075,.075,.002),(.07,.07,.002),(.07,.07,0)],ff_kitchen,ff_metal,16)
    if ff_label=='Sink':ff_sink_start=ff_cursor
    if ff_label=='Tall pantry':ff_bench_end=ff_cursor
    ff_cursor+=ff_width
    if ff_label=='Dishwasher':ff_cursor+=.02
ff_box('Kitchen rear stone left',(0,0,.865),(ff_sink_start,.6,.905),ff_kitchen,ff_stone,True)
ff_box('Kitchen rear stone right',(ff_sink_start+.89,0,.865),(ff_bench_end,.6,.905),ff_kitchen,ff_stone,True)
ff_box('Kitchen sink stone back',(ff_sink_start,0,.865),(ff_sink_start+.89,.10,.905),ff_kitchen,ff_stone)
ff_box('Kitchen sink stone front',(ff_sink_start,.54,.865),(ff_sink_start+.89,.6,.905),ff_kitchen,ff_stone)
ff_box('Kitchen sink stone left',(ff_sink_start,.1,.865),(ff_sink_start+.035,.54,.905),ff_kitchen,ff_stone)
ff_box('Kitchen sink stone right',(ff_sink_start+.855,.1,.865),(ff_sink_start+.89,.54,.905),ff_kitchen,ff_stone)
for ff_sink_u in (ff_sink_start+.24,ff_sink_start+.65):
    ff_sink_bowl('Kitchen sink bowl',(ff_sink_u,.32,.905),ff_kitchen)
ff_tap('Kitchen sink mixer',ff_sink_start+.445,.06,.905,ff_kitchen)
ff_cursor=.02
for ff_i,ff_width in enumerate((.9,.9,.9,1.01,1.01,1.01)):
    ff_cabinet('Kitchen overhead '+str(ff_i+1),ff_cursor,ff_width,.38,1.6,2.4,ff_kitchen)
    if ff_i==1:ff_box('Concealed rangehood',(ff_cursor+.02,.06,1.575),(ff_cursor+ff_width-.02,.36,1.60),ff_kitchen,ff_metal)
    ff_cursor+=ff_width
ff_island=ff_basis((13.74,5.11,0),(1,0),(0,1))
ff_island_cabinets=ff_basis((13.74,5.47,0),(1,0),(0,1))
ff_box('Island 3200 stone top',(0,0,.865),(3.2,1,.905),ff_island,ff_stone,True)
ff_box('Island west waterfall',(0,0,0),(.04,1,.865),ff_island,ff_stone,True)
ff_box('Island east waterfall',(3.16,0,0),(3.2,1,.865),ff_island,ff_stone,True)
ff_cursor=.06
for ff_i,ff_width in enumerate((.60,.84,.8,.84)):
    ff_cabinet('Island bank '+str(ff_i+1),ff_cursor,ff_width,.59,.10,.865,ff_island_cabinets,0 if ff_i==0 else 3)
    if ff_i==0:
        ff_box('Island microwave',(ff_cursor+.02,.61,.49),(ff_cursor+.58,.625,.80),ff_island_cabinets,ff_dark,True)
        ff_box('Microwave display',(ff_cursor+.44,.625,.62),(ff_cursor+.55,.628,.75),ff_island_cabinets,ff_metal)
    ff_cursor+=ff_width
ff_box('Island rear panel',(.04,.342,.10),(3.16,.36,.865),ff_island,ff_white)
ff_box('Island plinth',(.04,.39,0),(3.16,.91,.10),ff_island,ff_white)
ff_report['items'].append({'name':'Kitchen rear run/island','sheet':16,'rear_run_nominal_m':6.89,
 'rear_modules_m':[ff_m[0] for ff_m in ff_modules],'island_m':[3.2,1,.905],'stone_edge_m':.04,
 'rear_depth_m':.6,'clear_aisle_m':1.065,'basis':'Written cabinet module sizes; absolute run and island positions scaled from the plan. 15 mm wall lining reduces the nominal aisle.'})

# Wet rooms: scale only the end allowance to keep finished lining clear.
ff_vanity('Powder vanity',(20.035,5.215,0),(0,1),(1,0),1.3,.25,False,15)
ff_vanity('Ensuite double vanity',(18.575,1.095,0),(0,1),(1,0),1.77,0,True,17)
ff_vanity('Upper bath vanity',(14.315,5.245,3.159),(0,1),(-1,0),1.2,0,False,19)
ff_vanity('Bath 2 vanity',(12.825,.105,3.159),(0,1),(-1,0),1.1,0,False,18)
ff_toilet('Powder WC',(20.035,7.34,0),(1,0),15)
ff_toilet('Ensuite WC',(18.575,.54,0),(1,0),17)
ff_toilet('Upper WC',(11.74,7.775,3.159),(0,-1),19)
ff_toilet('Bath 2 WC',(10.655,.54,3.159),(1,0),18)
for ff_name,ff_lo,ff_hi,ff_floor in [('Powder',(20.035,5.215),(21.605,7.775),0),
 ('Ensuite',(18.575,1.095),(20.345,3.855),0),('Ensuite WC',(18.575,.105),(20.345,.975),0),
 ('Upper WC',(11.255,5.695),(12.225,7.775),3.159),('Upper bathroom',(12.345,5.205),(14.315,7.775),3.159),
 ('Upper bathroom entry',(12.345,4.605),(13.315,5.205),3.159),('Bathroom 2',(10.655,.105),(12.825,2.185),3.159)]:
    ff_tiles(ff_name,ff_lo,ff_hi,ff_floor)
ff_shower('Ensuite shower',(18.575,2.985),(20.345,3.855),0,17)
ff_shower('Upper bath shower',(13.415,6.475),(14.315,7.775),3.159,19,True)
ff_shower('Bath 2 shower',(10.655,1.285),(11.555,2.185),3.159,18)

# Laundry, sheet17: actual 3090 run sits inside the traced room with a 30 mm allowance.
ff_laundry=ff_basis((8.815,7.765,0),(0,-1),(-1,0))
for ff_i,ff_z in enumerate((.02,.94)):
    ff_box(('Washer' if ff_i==0 else 'Dryer')+' case',(.04,.01,ff_z),(.76,.61,ff_z+.84),ff_laundry,ff_white,True)
    # Front-loading drum is vertical: rotate a short cylinder toward the aisle.
    ff_tube('Laundry drum rim '+str(ff_i),(.4,.611,ff_z+.42),(.4,.625,ff_z+.42),.245,ff_laundry,ff_metal,20)
    ff_tube('Laundry drum glazing '+str(ff_i),(.4,.626,ff_z+.42),(.4,.630,ff_z+.42),.212,ff_laundry,ff_dark,20)
    ff_box('Laundry controls '+str(ff_i),(.08,.612,ff_z+.71),(.70,.621,ff_z+.78),ff_laundry,ff_dark)
ff_cursor=.82
for ff_i,ff_width in enumerate((.8,.725,.725)):
    ff_cabinet('Laundry base '+str(ff_i+1),ff_cursor,ff_width,.58,.10,.88,ff_laundry)
    ff_cabinet('Laundry overhead '+str(ff_i+1),ff_cursor,ff_width,.38,1.60,2.40,ff_laundry)
    ff_cursor+=ff_width
ff_box('Laundry stone left',(.82,0,.88),(.92,.6,.90),ff_laundry,ff_stone,True)
ff_box('Laundry stone right',(1.52,0,.88),(3.07,.6,.90),ff_laundry,ff_stone,True)
ff_box('Laundry stone back',(.92,0,.88),(1.52,.1,.90),ff_laundry,ff_stone)
ff_box('Laundry stone front',(.92,.54,.88),(1.52,.6,.90),ff_laundry,ff_stone)
ff_sink_bowl('Laundry trough',(1.22,.32,.90),ff_laundry,.30)
ff_tap('Laundry mixer',1.22,.08,.90,ff_laundry)
ff_linen=ff_basis((6.485,4.675,0),(0,1),(1,0))
for ff_i in range(2):ff_cabinet('Laundry linen '+str(ff_i),ff_i*1.59,1.47,.50,0,2.4,ff_linen,ff_open=True)
ff_report['items'].append({'name':'Laundry','sheet':17,'nominal_run_m':3.09,'model_run_m':3.07,
 'basis':'3090 nominal run with lining/end allowance; stacked appliances illustrative; west linen shown open. Laundry walls/bulkhead require full reconciliation.'})

def ff_hanging(ff_name,ff_origin,ff_u,ff_v,ff_width,ff_depth,ff_height=1.65,ff_bays=1):
    ff_b=ff_basis(ff_origin,ff_u,ff_v)
    ff_box(ff_name+' shelf',(0,0,ff_height),(ff_width,ff_depth,ff_height+.018),ff_b)
    ff_tube(ff_name+' rail',(.02,ff_depth*.60,ff_height-.065),(ff_width-.02,ff_depth*.60,ff_height-.065),.012,ff_b)
    for ff_i in range(ff_bays+1):
        ff_x=min(ff_width-.018,ff_i*ff_width/ff_bays)
        ff_box(ff_name+' support '+str(ff_i),(ff_x,0,0),(ff_x+.018,ff_depth,ff_height),ff_b)
    ff_report['items'].append({'name':ff_name,'width_m':ff_width,'depth_m':ff_depth,'shelf_height_m':ff_height,
        'basis':'Sheets15/18/19 written shelf heights; end allowances for finished wall lining.'})

ff_towers=ff_basis((20.555,3.855,0),(0,-1),(1,0))
for ff_i in range(2):
    ff_cabinet('WIR1 drawer tower '+str(ff_i),ff_i*.623,.607,.6,0,1.0,ff_towers,4)
    ff_cabinet('WIR1 open tower '+str(ff_i),ff_i*.623,.607,.6,1.0,2.016,ff_towers,ff_open=True)
ff_hanging('WIR1 south',(20.555,.105,0),(1,0),(0,1),2.24,.60,2.016,2)
ff_hanging('WIR1 east',(22.795,.705,0),(0,1),(-1,0),2.30,.60,2.016,2)
ff_hanging('WIR1 west south',(20.555,.705,0),(0,1),(1,0),.66,.60,2.016)
ff_hanging('Bedroom2 robe',(16.915,.105,3.159),(0,1),(-1,0),3.17,.555,1.65,3)
ff_hanging('Bedroom5 robe',(14.435,5.205,3.159),(0,1),(1,0),2.57,.555,1.65,2)
ff_upper_linen=ff_basis((13.435,5.085,3.159),(1,0),(0,-1))
for ff_z in (.45,.9,1.35,1.8):ff_box('Upper linen shelf',(0,0,ff_z),(1.57,.465,ff_z+.018),ff_upper_linen)
# WIR3/4 U-shaped shelves leave the opposite access edge open.
ff_hanging('WIR3 back',(6.485,4.485,3.159),(1,0),(0,-1),2.27,.35)
ff_hanging('WIR3 left',(6.485,3.395,3.159),(0,1),(1,0),.74,.45)
ff_hanging('WIR3 right',(8.755,3.395,3.159),(0,1),(-1,0),.74,.45)
ff_hanging('WIR4 back',(8.875,3.395,3.159),(1,0),(0,1),2.26,.35)
ff_hanging('WIR4 left',(8.875,3.745,3.159),(0,1),(1,0),.74,.45)
ff_hanging('WIR4 right',(11.135,3.745,3.159),(0,1),(-1,0),.74,.45)

bpy.context.view_layer.update()
ff_deps=bpy.context.evaluated_depsgraph_get();ff_triangles=0
for ff_ob in ff_collection.objects:
    ff_eval=ff_ob.evaluated_get(ff_deps);ff_mesh=ff_eval.to_mesh()
    ff_mesh.calc_loop_triangles();ff_triangles+=len(ff_mesh.loop_triangles);ff_eval.to_mesh_clear()
assert ff_triangles<20000,('Fitout triangle budget exceeded',ff_triangles)
ff_report['objects']=len(ff_collection.objects);ff_report['triangles']=ff_triangles
ff_handle_check=[]
for ff_ob in ff_collection.objects:
    if ' pull ' not in ff_ob.name or 'mounting post' in ff_ob.name:continue
    if not ff_ob.name.startswith(('Fitout | Kitchen','Fitout | Laundry overhead')):continue
    ff_bb=vr_bounds(ff_ob)
    ff_handle_check.append({'object':ff_ob.name,'height_mm':[round(v*1000) for v in ff_bb[2]],
        'centre_height_mm':round(sum(ff_bb[2])*500)})
(OUT/'cabinet-handle-coordination.json').write_text(json.dumps({
    'source_sheet':16,'basis':'Written cabinet extents; handle heights, grip dimensions and offsets are illustrative.',
    'change':'Upper cupboard handles moved to lower meeting edges; pantry handles lowered; paired doors mirrored; all cabinet bars attached by short mounting posts.',
    'measurements':ff_handle_check,'units':'mm above the model finished floor',
    'unchanged':'Base-door handles remain near the top; drawer pulls remain horizontal and centred.'},indent=2))
(OUT/'fixed-fitout-coordination.json').write_text(json.dumps(ff_report,indent=2))
changes.append({'object':'Fixed joinery and fixtures','action':f'{len(ff_collection.objects)} lightweight parts / {ff_triangles} triangles; source15-19; unresolved details remain listed.'})
print('FIXED_FITOUT',len(ff_collection.objects),ff_triangles,flush=True)
