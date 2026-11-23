"""Sheet 19 upper-bathroom tile finish, replacing existing lining materials.

No duplicate wall skins, aperture infills or changes to structural members.
Tile size and colour are illustrative; the sheet specifies full-height coverage.
"""
bt_wall=vr_material('VR Bathroom wall porcelain',(.80,.79,.76))
bt_report={'source_sheet':19,'room':'Upper bathroom at the end of the tour',
 'wall_coverage':'Full height on all room faces, with existing window/door openings retained.',
 'floor_module_mm':[600,600],'wall_module_mm':[600,300],'grout_mm':2.5,
 'finish_selection':'Illustrative matte warm-neutral porcelain; no tile product/size schedule supplied.',
 'floor_surface':'Continuous 3 mm finish; material joints do not expose the substrate.',
 'wall_objects':[],'removed_skirtings':[],
 'unresolved':['Recessed shower niche and falls/set-down remain separate coordination items.',
 'Existing upper floor/ceiling datums retained pending whole-model coordination.']}

def bt_in_range(lo,hi,a,b,eps=.0002):
    return lo>=a-eps and hi<=b+eps

for bt_ob in list(house.objects):
    if bt_ob.type!='MESH':continue
    bt_bb=vr_bounds(bt_ob)
    bt_x0,bt_x1=bt_bb[0];bt_y0,bt_y1=bt_bb[1];bt_z0,bt_z1=bt_bb[2]
    if bt_z0<3.158 or bt_z1>5.731:continue
    # Remove only the bath-facing painted skirting, leaving adjacent rooms intact.
    bt_inside=(bt_in_range(bt_x0,bt_x1,12.345,14.315) and bt_in_range(bt_y0,bt_y1,5.205,7.775)) or \
              (bt_in_range(bt_x0,bt_x1,12.345,13.315) and bt_in_range(bt_y0,bt_y1,4.605,7.775))
    if ' | skirting' in bt_ob.name and bt_inside:
        bt_report['removed_skirtings'].append(bt_ob.name)
        bpy.data.objects.remove(bt_ob,do_unlink=True);continue
    if not any(s in bt_ob.name for s in (' | lining',' | opening return',' | end return')):continue
    bt_face=None
    if bt_ob.name.startswith('FF North wall') and bt_in_range(bt_x0,bt_x1,12.345,14.315):bt_face='north including window reveals'
    elif bt_ob.name.startswith('FF WC bath division') and bt_in_range(bt_x0,bt_x1,12.335,12.345):bt_face='west'
    elif bt_ob.name.startswith('FF Bath robe division') and bt_in_range(bt_x0,bt_x1,14.315,14.325):bt_face='east'
    elif bt_ob.name.startswith('FF Bath hall | lining') and bt_in_range(bt_x0,bt_x1,12.345,13.315) and bt_in_range(bt_y0,bt_y1,4.595,4.605):bt_face='entry'
    elif bt_ob.name.startswith('FF Linen north') and bt_in_range(bt_x0,bt_x1,13.315,14.315) and bt_y0>=5.094:bt_face='south return'
    elif bt_ob.name.startswith('FF Linen west') and bt_in_range(bt_x0,bt_x1,13.315,13.325) and bt_y0>=4.604:bt_face='entry return'
    if bt_face:
        bt_ob.data=bt_ob.data.copy();bt_ob.data.materials.clear();bt_ob.data.materials.append(bt_wall)
        bt_report['wall_objects'].append({'name':bt_ob.name,'face':bt_face,'bounds':bt_bb})

assert len({v['face'] for v in bt_report['wall_objects']})==6,'Missing bathroom wall tile zone'
assert len(bt_report['removed_skirtings'])>=7,'Bath painted skirting removal incomplete'
bt_floors=[o for o in house.objects if o.name.startswith('Fitout | Upper bathroom') and o.name.endswith('tiled floor')]
assert len(bt_floors)==2,'Bathroom entry and main floor must both remain'
for bt_ob in bt_floors:
    bt_bb=vr_bounds(bt_ob)
    assert abs(bt_bb[2][1]-3.162)<.0001,'Inconsistent bathroom finish height'
assert not any(o.name.startswith('Fitout | Upper bathroom') and ' tile.' in o.name for o in house.objects)
bt_report['checks']='PASS: six wall zones, retained apertures, no duplicate wall skin, continuous level floor.'
(OUT/'bathroom-tiling.json').write_text(json.dumps(bt_report,indent=2))
changes.append({'object':'Upper bathroom tiling','action':'Full-height tiled finishes replace plaster materials; painted skirting removed. All wet-room floor blocks replaced by continuous surfaces with narrow material grout.'})
print('BATHROOM_TILING_PASS',len(bt_report['wall_objects']),len(bt_report['removed_skirtings']),flush=True)
