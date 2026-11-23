"""Plan bulkheads and stair enclosure finish, after the legacy finish passes."""
bulkhead_report=[]
def arch_bulkhead(name,lo,hi,basis):
    # Hollow 10 mm plaster shells, deduplicated against other lining pieces.
    # Reserve all actual wall cores so finishes never fill the wall framing.
    boxes=[([lo[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]+.010]),
           ([lo[0],lo[1],lo[2]+.010],[lo[0]+.010,hi[1],hi[2]]),
           ([hi[0]-.010,lo[1],lo[2]+.010],[hi[0],hi[1],hi[2]]),
           ([lo[0]+.010,lo[1],lo[2]+.010],[hi[0]-.010,lo[1]+.010,hi[2]]),
           ([lo[0]+.010,hi[1]-.010,lo[2]+.010],[hi[0]-.010,hi[1],hi[2]])]
    for j,box in enumerate(boxes):
        pieces=[box]
        for core in cores:pieces=[p for b in pieces for p in subtract(b,core)]
        for piece in pieces:solid(name+f' face {j}',piece,linings,plaster)
    bulkhead_report.append({'name':name,'min':lo,'max':hi,'basis':basis})

arch_bulkhead('Kitchen 340 mm dropped ceiling',(13.040,5.110,2.400),(19.930,7.775,2.740),
             'Sheets07/12/16: 6890 kitchen run, 2680 zone; soffit2400. Interior ceiling edge follows kitchen hatch.')
arch_bulkhead('Nook 450 mm deep bulkhead',(6.485,2.475,2.400),(8.435,2.925,2.740),
             'Sheet07: 1950 nook, 450 deep, 340 drop; coordinate end against corrected nook wall in next exterior pass.')
arch_bulkhead('Corridor entry bulkhead',(21.620,3.960,2.400),(21.710,5.110,2.740),
             'Sheet07 leader at powder/entry junction, 340 drop.')
arch_bulkhead('Family recess bulkhead',(17.970,.690,2.400),(18.470,3.360,2.740),
             'Sheet07: 500 recess between unequal boxed returns; 2670 length. Hatch and leader are on family side.')
arch_bulkhead('Ensuite vanity bulkhead',(18.575,1.080,2.400),(19.160,2.880,2.740),
             'Sheet17 plan/elevationD: bulkhead over1800 vanity, 600 cabinet depth. Sheet07/17 side discrepancy remains logged.')
arch_bulkhead('Upper hall retreat bulkhead',(19.420,3.380,5.390),(19.510,4.500,5.730),
             'Sheet08: 1120 hall, 340 drop at retreat junction.')

arch_bulkhead('Theatre west perimeter bulkhead',(22.615,.600,5.390),(23.020,4.080,5.730),
             'Sheet08: 420 band from wall frame, lining deducted; soffitFF+2250.')
arch_bulkhead('Theatre south perimeter bulkhead',(23.035,.105,5.390),(26.885,.600,5.730),
             'Sheet08: 510 band including wall finish convention.')
arch_bulkhead('Theatre window perimeter bulkhead',(26.400,.600,5.390),(26.885,4.080,5.730),
             'Sheet08 hatch: approximately500 deep, not explicitly dimensioned; retain as provisional.')
# Retain a temporary head/swing recess at the door: the source door2340 and
# bulkhead soffit2250 conflict. This is openly recorded, not accepted geometry.
arch_bulkhead('Theatre entry perimeter bulkhead',(24.040,4.080,5.390),(26.885,4.575,5.730),
             'Sheet08: 510 band. Door bay temporarily omitted pending the documented door/bulkhead height conflict.')

# Continue the lined full-height ground-floor stair wall through the floor
# edge up to the retained upper dwarf wall. Rails are mounted to real faces.
solid('Stair enclosure floor-zone face',([21.710,6.650,2.740],[24.305,6.660,3.159]),linings,plaster)
solid('Stair enclosure outer floor-zone face',([21.710,6.540,2.740],[24.305,6.550,3.159]),linings,plaster)
vr_extrude('Stair inner closed string',wall_string,6.660,6.730,stairs,paint)
arch_stair_foot=stair_report['foot_x'];arch_stair_head=stair_report['landing_edge_x']
arch_stair_run=stair_report['flight_clear_run_m']
arch_stair_rise=stair_report['rise_m'];arch_stair_going=stair_report['going_m']
def arch_rail_z(u):return arch_stair_rise+1.0+min(u,arch_stair_run)*arch_stair_rise/arch_stair_going
vr_beam('Stair inner wall handrail',(arch_stair_foot-.025,6.735,arch_rail_z(.025)),
        (arch_stair_head,6.735,arch_rail_z(arch_stair_run)),.045,.050,stairs,oak)
for i,u in enumerate((.25,1.4,2.6,3.7)):
    x=arch_stair_foot-u;z=arch_rail_z(u)-.020
    vr_box(f'Stair inner wall rail bracket {i+1}',(x-.012,6.660,z-.035),(x+.012,6.735,z),stairs,steel)
# Correct the existing external-wall rail from900 to the specified1000 height.
for ob in house.objects:
    if ob.name=='Stair wall handrail' or ob.name.startswith('Stair rail bracket '):ob.location.z+=.100

# The old platform was built420 mm high from a horizontal plan dimension.
# Remove that unsupported structure. Sheet08 separately labels the hatched
# ceiling border340 DROP DOWN BULKHEAD and a2300 PLATFORM / STEP DOWN floor
# division. 420 and510 are horizontal band widths, not a platform height.
removed_platform=[]
for ob in list(house.objects):
    if ob.name.startswith(('Theatre platform','Theatre raised skirting')):
        removed_platform.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
arch_report['platform']={'footprint_frame_m':[22.600,.090,24.900,4.590],
 'height_m':None,'state':'UNRESOLVED: unsupported420mm rise removed; no replacement height invented.',
 'evidence':'Sheet08: 2300 PLATFORM dimension and separate STEP DOWN arrow. Ceiling hatch is separately340mm DROP DOWN BULKHEAD.',
 'high_side':'Unresolved: platform label and step-down arrow need coordination; no raised side assumed.',
 'removed_objects':len(removed_platform)}
arch_report['ensuite_recess']={'family_recess_depth_m':.500,'family_recess_length_m':2.670,
 'north_box_clear_m':[.410,.420],'south_box_clear_m':[.410,.510],
 'cavity_slider_centre_y_m':1.950,'cavity_slider_centre_basis':'Scaled sheet17; pocket detailing remains provisional.',
 'bulkhead_note':'Family-side hatch on07 and vanity-side hatch/elevation on17 both represented; coordination remains open.'}
arch_report['bulkheads']=bulkhead_report
arch_report['stair_enclosure']='Full-height ground-floor wall, continuous floor-band lining, retained1200 dwarf wall above; no open pickets.'
stair_report['enclosure']=arch_report['stair_enclosure']
stair_report['handrail_height_above_pitch_m']=1.0
stair_report['open_picket_design_removed']=True
(OUT/'stair-coordination.json').write_text(json.dumps(stair_report,indent=2))
arch_opening_report=json.loads((OUT/'opening-coordination.json').read_text())
arch_opening_report['theatre_platform_finished']=False
arch_opening_report['theatre_platform_status']=arch_report['platform']
(OUT/'opening-coordination.json').write_text(json.dumps(arch_opening_report,indent=2))
bpy.context.view_layer.update()
(OUT/'architectural-wall-setout.json').write_text(json.dumps(arch_report,indent=2))
changes.append({'object':'Architectural ceiling/stair finishes','action':f'{len(bulkhead_report)} bulkhead zones added; stair enclosure and1m wall handrails; unsupported theatre platform height removed and remains unresolved.'})
