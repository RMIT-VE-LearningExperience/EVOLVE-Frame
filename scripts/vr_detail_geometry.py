"""Small axis-aligned reconstruction helpers; executed inside build_vr_model."""
def detail_box_bounds(ob):
    bb=vr_bounds(ob)
    return ([v[0] for v in bb],[v[1] for v in bb])

def detail_intersection(a,b):
    lo=[max(a[0][i],b[0][i]) for i in range(3)]
    hi=[min(a[1][i],b[1][i]) for i in range(3)]
    return (lo,hi) if min(hi[i]-lo[i] for i in range(3))>.00001 else None

def detail_replace_box(ob,pieces,material=None):
    # Only generated axis-aligned cuboids: never approximate an arbitrary mesh.
    bb=detail_box_bounds(ob)
    assert len(ob.data.vertices)==8 and len(ob.data.polygons)==6,ob.name
    for vertex in ob.data.vertices:
        p=ob.matrix_world@vertex.co
        assert all(min(abs(p[i]-bb[0][i]),abs(p[i]-bb[1][i]))<.00002 for i in range(3)),ob.name
    name=ob.name;col=ob.users_collection[0];mat=material or ob.data.materials[0]
    props={key:ob[key] for key in ob.keys()}
    bpy.data.objects.remove(ob,do_unlink=True)
    result=[]
    for n,piece in enumerate(pieces):
        obj=vr_box(name if n==0 else name+f' split {n}',piece[0],piece[1],col,mat)
        for key,value in props.items():obj[key]=value
        result.append(obj)
    bpy.context.view_layer.update()
    return result

def detail_cut_objects(objects,cut,record):
    bpy.context.view_layer.update()
    for ob in list(objects):
        bb=detail_box_bounds(ob)
        if not detail_intersection(bb,cut):continue
        record.append({'name':ob.name,'bounds_before':bb,'cut':cut})
        detail_replace_box(ob,subtract(bb,cut))

def detail_pipe(name,points,radius,collection,material,sides=12,open_ends=False):
    # Shared mitered rings give closed, connected elbows without intersecting
    # cylinder end caps. Used for illustrative drainage, not hydraulic design.
    points=[Vector(p) for p in points]
    tangents=[(b-a).normalized() for a,b in zip(points,points[1:])]
    reference=Vector((1,0,0))
    if abs(tangents[0].dot(reference))>.95:reference=Vector((0,1,0))
    vertices=[]
    previous=None
    for i,p in enumerate(points):
        tangent=tangents[0] if i==0 else tangents[-1] if i==len(points)-1 else (tangents[i-1]+tangents[i]).normalized()
        axis=reference-tangent*reference.dot(tangent)
        if axis.length<.01:axis=Vector((0,0,1)).cross(tangent)
        axis.normalize()
        if previous is not None and axis.dot(previous)<0:axis=-axis
        other=tangent.cross(axis).normalized();previous=axis
        correction=1.0 if i in (0,len(points)-1) else 1/max(.5,tangent.dot(tangents[i-1]))
        for j in range(sides):
            angle=2*math.pi*j/sides
            vertices.append(p+radius*(math.cos(angle)*axis+math.sin(angle)*other)*correction)
    faces=[]
    if not open_ends:faces=[tuple(range(sides-1,-1,-1)),tuple(range((len(points)-1)*sides,len(points)*sides))]
    for i in range(len(points)-1):
        faces.extend((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j) for j in range(sides))
    obj=vr_mesh(name,vertices,faces,collection,material)
    for face in obj.data.polygons:face.use_smooth=len(face.vertices)==4
    return obj
