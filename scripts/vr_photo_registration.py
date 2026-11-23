"""Photo 0.4.5: coordinate structural/envelope geometry before lining it."""
p45_report={'source_sheets':[7,12,16,17,18,19], 'changes':[], 'checks':[],
 'limitations':['Finish colours and hardware product shapes are illustrative.',
 'D01 horizontal centre is scaled within the written3110 entry; scheduled width retained.',
 'Floor-zone rim continuation is an illustrative closure of the existing framing system, not an engineered connection design.']}
p45_rec=next(r for r in vr_wall_records if r['name']=='GF East entry and bedroom')
p45_edges=[]
for p45_op in p45_rec['openings']:
    if p45_op[0]!='D01 double entry':continue
    p45_old=p45_rec['a'][1]+p45_op[1];p45_new=(4.680+7.790)/2
    p45_edges=[(p45_old-p45_op[2]/2,p45_new-p45_op[2]/2),(p45_old+p45_op[2]/2,p45_new+p45_op[2]/2)]
    p45_op[1]=p45_new-p45_rec['a'][1]
    bpy.data.objects['OPENING | D01 double entry'].location.y+=p45_new-p45_old
    p45_report['changes'].append({'item':'D01 front door registration','old_centre_y':p45_old,'new_centre_y':p45_new,'rough_width':p45_op[2]})
bpy.context.view_layer.update()
for p45_ob in house.objects:
    if p45_ob.type!='MESH' or p45_ob.get('associated_frame')!=p45_rec['name']:continue
    if not any(abs((p45_ob.matrix_world@v.co).y-old)<.0001 for v in p45_ob.data.vertices for old,new in p45_edges):continue
    p45_ob.data=p45_ob.data.copy();p45_inv=p45_ob.matrix_world.inverted()
    for p45_v in p45_ob.data.vertices:
        p45_p=p45_ob.matrix_world@p45_v.co
        p45_match=next((new for old,new in p45_edges if abs(p45_p.y-old)<.0001),None)
        if p45_match is not None:p45_p.y=p45_match;p45_v.co=p45_inv@p45_p
for p45_ob in list(house.objects):
    if p45_ob.type=='MESH' and p45_ob.name.startswith(p45_rec['name']+' |') and not p45_ob.get('associated_frame'):
        bpy.data.objects.remove(p45_ob,do_unlink=True)
arch_env['wall'](p45_rec['name'],p45_rec['a'][:2],p45_rec['b'][:2],0,2.74,
    bpy.data.collections['02 Ground floor walls'],p45_rec['openings'])

# Sheet17:1500 +90 partition +1500. Existing1470 clear cabinets plus120
# finished partition (90 frame +15 each side) fit the written chain.
arch_wall('Laundry linen divider',(6.425,6.205),(6.985,6.205),
    source='Sheet17:90 divider between two1500 nominal linen bays; finished cabinet clear width1470')
p45_report['changes'].append({'item':'Laundry linen divider','frame_width_m':.09,'finished_width_m':.12})

# The retained garage veneer extended into the northern laundry cupboard.
# Trim this existing skin at the main house north exterior plane, not behind
# an extra decorative panel. Structural cores remain unchanged.
p45_brick=bpy.data.objects['Garage east upstand | Ground brick veneer']
p45_brick.data=p45_brick.data.copy();p45_inv=p45_brick.matrix_world.inverted()
for p45_v in p45_brick.data.vertices:
    p45_p=p45_brick.matrix_world@p45_v.co
    if p45_p.y<7.980:p45_p.y=7.980;p45_v.co=p45_inv@p45_p
p45_report['changes'].append({'item':'Garage veneer in laundry','new_south_limit_y':7.980})

# Void does not mean the external upper wall loses its400mm floor-zone rim.
# Continue the existing45x400 member around the north/east perimeter. Trim
# at every existing timber/steel volume, including the full-height C2 cores.
p45_rim_col=bpy.data.collections['04 Upper floor joists'] if bpy.data.collections.get('04 Upper floor joists') else bpy.data.objects['Floor rim/trimmer 2'].users_collection[0]
p45_pending=[([20.6637,7.8125,2.740],[26.9225,7.8575,3.140]),
             ([26.9225,4.635,2.740],[26.9675,7.8575,3.140])]
# Local AABB subtraction, before room-shell subtract is declared.
def p45_subtract(box,cut):
    lo,hi=box;a,b=cut;l=[max(lo[i],a[i]) for i in range(3)];h=[min(hi[i],b[i]) for i in range(3)]
    if any(h[i]-l[i]<1e-5 for i in range(3)):return [box]
    result=[];low=list(lo);high=list(hi)
    for i in range(3):
        if l[i]-low[i]>1e-5:end=high.copy();end[i]=l[i];result.append((low.copy(),end));low[i]=l[i]
        if high[i]-h[i]>1e-5:start=low.copy();start[i]=h[i];result.append((start,high.copy()));high[i]=h[i]
    return result
bpy.context.view_layer.update()
# Reserve the complete hollow RHS envelope, including its empty centre.
p45_pending=[p for b in p45_pending for p in p45_subtract(b,
    ([powder_column_x-.0445,7.790,-.041],[powder_column_x+.0445,7.879,6]))]
for p45_cut in [([24.277141,7.790,-.041],[24.366145,7.880,6]),
                ([powder_column_right,7.7849,2.9449],[26.945,7.8851,3.0951])]:
    p45_pending=[p for b in p45_pending for p in p45_subtract(b,p45_cut)]
for p45_ob in house.objects:
    if p45_ob.type!='MESH' or not any(c.name[:2] in ('02','03','04','05') for c in p45_ob.users_collection):continue
    p45_b=vr_bounds(p45_ob)
    p45_pending=[p for b in p45_pending for p in p45_subtract(b,([v[0] for v in p45_b],[v[1] for v in p45_b]))]
for p45_i,p45_box in enumerate(p45_pending):
    vr_box('Floor perimeter rim continuation '+str(p45_i+1),*p45_box,p45_rim_col,pine)
p45_report['changes'].append({'item':'North/east perimeter floor rim','section_m':[.045,.4],'pieces':len(p45_pending),
 'basis':'Complete existing rim around external wall above the void; retained upper/lower wall levels. Connection details remain illustrative.'})
