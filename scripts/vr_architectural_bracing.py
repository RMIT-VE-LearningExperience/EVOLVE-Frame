"""Keep the retained illustrative braces seated on the revised frame faces.

This restores visual connections only. A brace moved or shortened to clear an
architectural opening remains a structural-coordination item, not a verified
bracing design or a substituted engineering schedule.
"""
brace_registration=[]
for saved in brace_report:
    ob=bpy.data.objects.get(saved['object'])
    rec=next((r for r in vr_wall_records if r['name']==saved['wall']),None)
    old=next((r for r in wall_data if r['name']==saved['wall']),None)
    if ob is None or rec is None or old is None:continue
    axis=0 if abs(rec['b'][0]-rec['a'][0])>abs(rec['b'][1]-rec['a'][1]) else 1
    normal=1-axis
    bb=vr_bounds(ob);before=[b[:] for b in bb]
    side=1 if sum(bb[normal])/2>old['a'][normal] else -1
    half=(bb[normal][1]-bb[normal][0])/2
    target=rec['a'][normal]+side*(.045+half)
    ob.location[normal]+=target-sum(bb[normal])/2
    # The record's opening distances follow a->b, including reversed walls.
    sign=1 if rec['b'][axis]>rec['a'][axis] else -1
    low,high=sorted((rec['a'][axis],rec['b'][axis]))
    intervals=[]
    for tag,c,w,s,h in rec['openings']:
        centre=rec['a'][axis]+sign*c
        intervals.append((centre-w/2,centre+w/2))
    edges=[low]
    for l,r in sorted(intervals):edges.extend((l,r))
    edges.append(high)
    bays=[(l+.10,r-.10) for l,r in zip(edges[::2],edges[1::2]) if r-l>.4]
    width=bb[axis][1]-bb[axis][0]
    assert bays,('No brace bay',ob.name)
    choices=[]
    for l,r in bays:
        span=min(width,r-l);left=max(l,min(bb[axis][0],r-span))
        choices.append((max(0,width-span)*5+abs(left-bb[axis][0]),left,left+span))
    _,left,right=min(choices)
    if abs(left-bb[axis][0])>.00001 or abs(right-bb[axis][1])>.00001:
        ob.data=ob.data.copy();bpy.context.view_layer.update();inv=ob.matrix_world.inverted()
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co
            p[axis]=left+(p[axis]-bb[axis][0])*(right-left)/width;v.co=inv@p
    ob['source_status']='Illustrative brace seated on architectural revision; structural bracing setout remains unverified'
    brace_registration.append({'object':ob.name,'wall':rec['name'],
        'normal_shift_mm':round((target-sum(before[normal])/2)*1000,1),
        'along_shift_mm':round((left-before[axis][0])*1000,1),
        'original_span_mm':round(width*1000,1),'revised_span_mm':round((right-left)*1000,1),
        'status':'Geometry coordination only; engineering acceptance pending'})
bpy.context.view_layer.update()
(OUT/'architectural-brace-registration.json').write_text(json.dumps(brace_registration,indent=2))
changes.append({'object':'Retained illustrative braces','action':'Seated on revised wall faces and cleared window/door apertures; structural setout remains unverified.'})
