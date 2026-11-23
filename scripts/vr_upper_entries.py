"""Coordinate Bedroom 5 and upper bathroom entries to architectural sheet 08.

The drawing's 820/720 x 2340 labels describe door leaves. Jamb thickness,
reveals and hardware below are illustrative finish allowances, not shop details.
Runs only on the separate VR revision, before generating its linings.
"""
vr_wall_records=json.loads((ROOT/'output/timber_frame/wall_setout.json').read_text())
entry_report={'source':'Leichhardt Architectural Plans, sheet 08 First Floor Plan',
              'allowances':'22 mm jamb; 3 mm side/top/bottom reveals; 38 mm open leaf',
              'doors':[], 'partitions':[]}

# The original trace stopped both partitions at intermediate returns, leaving
# unplanned passages into the neighbouring enclosure. Continue to the hall wall.
for name,hall in [('FF Bed 5 west','FF Bed 5 south'),('FF WC bath division','FF Bath hall')]:
    rec=next(r for r in vr_wall_records if r['name']==name)
    hall_y=next(r for r in vr_wall_records if r['name']==hall)['a'][1]
    old_end=rec['b'][1]; new_end=hall_y+.045
    extension=old_end-new_end; x=rec['a'][0]; z=rec['z']; h=rec['h']
    for label in ('bottom plate','top plate lower','top plate upper'):
        ob=bpy.data.objects[name+' | '+label]
        ob.location.y-=extension/2; ob.scale.z+=extension
    vr_box(name+' | completed end stud',(x-.045,new_end,z+.045),
           (x+.045,new_end+.035,z+h-.09),upper,pine)
    for level in (h/3,2*h/3):
        vr_box(name+' | return nogging',(x-.045,new_end+.035,z+level-.0175),
               (x+.045,old_end,z+level+.0175),upper,pine)
    rec['b'][1]=new_end
    entry_report['partitions'].append({'wall':name,'old_end_y':old_end,
        'new_end_y':new_end,'extension_mm':round(extension*1000,1)})
    changes.append({'object':name,'action':'Extended incomplete partition to hall framing; sheet 08 has no side passage here'})
bpy.context.view_layer.update()

# Rebuild the two door-bearing frames, preserving the traced hinge-side edge.
# Retaining that edge avoids moving the door into the perpendicular wall/casing.
for wall_name,tag,leaf_width in [('FF Bed 5 south','Bed 5 door',.820),
                                  ('FF Bath hall','Bathroom door',.720)]:
    rec=next(r for r in vr_wall_records if r['name']==wall_name)
    tag,c,old_width,s,old_h=rec['openings'][0]
    rough=leaf_width+.006+.044
    c+=(rough-old_width)/2
    head=.019+.003+2.340+.003+.022
    rec['openings']=[[tag,c,rough,0,head]]
    rec['jamb_thickness']=.022;rec['nominal_door_width']=leaf_width
    a=Vector(rec['a']);b=Vector(rec['b']);t=(b-a).normalized();length=(b-a).length
    z=rec['z'];h=rec['h'];l=c-rough/2;r=c+rough/2
    for ob in list(house.objects):
        if ob.name.startswith(wall_name+' |'):
            bpy.data.objects.remove(ob,do_unlink=True)
    def member(label,u0,u1,z0,z1,mat=pine):
        p=a+t*u0; q=a+t*u1
        if label.startswith('top plate'):
            p.z=q.z=z+(z0+z1)/2
            return vr_beam(wall_name+' | '+label,p,q,.09,z1-z0,upper,mat)
        return vr_box(wall_name+' | '+label,(p.x,a.y-.045,z+z0),
                      (q.x,a.y+.045,z+z1),upper,mat)
    for i,(lo,hi) in enumerate(((0,l),(r,length))):member('bottom plate '+str(i),lo,hi,0,.045)
    member('top plate lower',0,length,h-.09,h-.045)
    member('top plate upper',0,length,h-.045,h)
    for label,lo,hi in [('hinge jack',l-.045,l),('hinge king',l-.090,l-.045),
                        ('strike jack',r,r+.045),('strike king',r+.045,r+.090)]:
        member(tag+' '+label,max(0,lo),hi,.045,head if 'jack' in label else h-.09)
    lintel_top=min(head+.14,h-.09)
    member(tag+' LVL lintel',l-.045,r+.045,head,lintel_top,bpy.data.materials['LVL beams'])
    if h-.09-lintel_top>.003:
        for u in (l+.0175,c,r-.0175):member(tag+' head cripple',u-.0175,u+.0175,lintel_top,h-.09)
    stud_spans=[]
    for u in [.0175]+[i*.45 for i in range(1,math.ceil(length/.45))]+[length-.0175]:
        if u-.0175<0 or u+.0175>length+.00001:continue
        if l-.125<u<r+.125:continue
        member('common stud',u-.0175,u+.0175,.045,h-.09)
        stud_spans.append((u-.0175,u+.0175))
    # Nogging stops at actual stud/jamb faces instead of intersecting them.
    for lo,hi in ((0,l-.090),(r+.090,length)):
        cursor=lo
        for sl,sr in sorted(stud_spans+[(hi,hi)]):
            if sr<=lo or sl>hi:continue
            if sl>cursor+.003:
                for level in (h/3,2*h/3):member('nogging',cursor,sl,level-.0175,level+.0175)
            cursor=max(cursor,sr)
    entry_report['doors'].append({'name':tag,'wall':wall_name,'nominal_leaf_width_mm':round(leaf_width*1000),
        'nominal_leaf_height_mm':2340,'rough_width_mm':round(rough*1000),
        'jamb_clear_width_mm':round((rough-.044)*1000),'finished_head_above_floor_mm':2346,
        'hinge_edge_x':a.x+l,'centre_x':a.x+c,'wall_y':a.y})
    changes.append({'object':wall_name,'action':'Rebuilt framing for scheduled leaf plus jamb/reveal allowances; retained hinge-side position'})
bpy.context.view_layer.update()
