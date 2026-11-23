"""Finish gaps and floor thresholds identified in the twelve0.4.5 photos."""
solid('Entry void south floor-zone lining',([24.400,4.685,2.740],[26.885,4.695,3.159]),linings,plaster)
p45_report['changes'].append({'item':'Entry void south fascia','height_m':.419})
# Section12 depicts horizontal eave linings. Terminate at the retained fascia
# and outside render faces; four abutting strips, no doubled corner sheets.
for p45_name,p45_lo,p45_hi in [
 ('south',(5.8425,-.5375,5.5145),(27.5275,-.100,5.5245)),
 ('north',(5.8425,7.980,5.5145),(27.5275,8.4175,5.5245)),
 ('west',(5.8425,-.100,5.5145),(6.280,7.980,5.5245)),
 ('east',(27.090,-.100,5.5145),(27.5275,7.980,5.5245))]:
    p45_ob=vr_box('Main eave soffit '+p45_name,p45_lo,p45_hi,roof_trim,photo_ceiling)
    p45_ob['source']='Sheet12 horizontal eave lining;10mm illustrative sheet fitted to existing fascia. Existing roof datum retained.'
p45_report['changes'].append({'item':'Main roof eave soffits','pieces':4,'thickness_m':.010})

# Tile the actual door throats, keeping a shared edge with existing floor
# finishes. Width is the rough opening minus two22mm jambs.
for p45_name,p45_lo,p45_hi,p45_floor in [
 ('Ensuite WC threshold',(19.517,.975),(20.243,1.095),0),
 ('Ensuite access threshold',(20.345,1.587),(20.555,2.313),0),
 ('Powder threshold',(20.737,5.095),(21.563,5.215),0),
 ('Upper WC threshold',(11.377,5.575),(12.103,5.695),3.159),
 ('Upper bathroom threshold',(12.467,4.485),(13.193,4.605),3.159),
 ('Bathroom2 threshold',(11.907,2.185),(12.633,2.305),3.159)]:
    ff_tiles(p45_name,p45_lo,p45_hi,p45_floor)
p45_report['changes'].append({'item':'Wet room doorway tile continuations','count':6,'finish_thickness_m':.003})

# Narrow jambs, wall slivers and casings need usable lightmap texels.
# Separate the skirting too, so its invisible back does not blacken wall
# texels beside the7mm ledge. The geometry remains continuous behind it.
p45_skirting=vr_material('VR Plaster skirting trim',(.84,.835,.82))
for p45_ob in house.objects:
    if p45_ob.type!='MESH' or not p45_ob.data.materials or p45_ob.data.materials[0]!=plaster:continue
    if '| skirting' in p45_ob.name:p45_ob.data.materials[0]=p45_skirting
    else:
        p45_dims=sorted(hi-lo for lo,hi in vr_bounds(p45_ob))
        if ('| opening return' in p45_ob.name or p45_ob.name.startswith('Door casing ') or
            ('| lining' in p45_ob.name and p45_dims[1]<.10)):
            p45_ob.data.materials[0]=photo_junction
p45_report['changes'].append({'item':'Door jamb/casing bake grouping','material':'VR Plaster junction returns','geometry':'unchanged'})
p45_report['changes'].append({'item':'Skirting bake grouping','material':'VR Plaster skirting trim','geometry':'unchanged; higher bake density and non-occluding trim'})
p45_report['changes'].append({'item':'Robe opening junction','clear_width_m':.800,'centre_y':3.455,'basis':'15mm scaled shift aligns north finished jamb with adjoining wall faceY3.855; no filler overlaps'})
bpy.context.view_layer.update()
p45_deps=bpy.context.evaluated_depsgraph_get()
def p45_ray(label,origin,direction,distance,expected):
    hit=house.ray_cast(p45_deps,Vector(origin),Vector(direction),distance=distance)
    name=hit[4].name if hit[0] else ''
    assert hit[0] and any(token in name for token in expected),(label,name)
    p45_report['checks'].append({'label':label,'object':name,'hit':list(hit[1]),'result':'PASS'})
p45_ray('Entry south floor fascia',(25.3,5.3,2.95),(0,-1,0),1,['Entry void south floor-zone lining'])
for p45_label,p45_origin in [('north',(10,8.15,5)),('south',(17,-.3,5)),('east',(27.3,6,5)),('west',(6.05,5,5))]:
    p45_ray('Eave '+p45_label,p45_origin,(0,0,1),1,['Main eave soffit '+p45_label])
p45_ray('Linen divider front',(7.4,6.205,1.5),(-1,0,0),1,['Laundry linen divider | end return'])
p45_ray('WC tile threshold',(19.88,1.035,.5),(0,0,-1),1,['Ensuite WC threshold tiled floor'])
for p45_z in (.4,1.5,2.2):
    p45_aim=Vector((22.79142,3.87,p45_z))-Vector((24.1,2.9,p45_z))
    p45_ray('Robe jamb former exposed stud',(24.1,2.9,p45_z),p45_aim.normalized(),2.0,['lining','opening return'])
for p45_x,p45_y in [(22,7.835),(25.5,7.835),(26.945,6)]:
    p45_ray('Perimeter floor-zone contact',(p45_x,p45_y,2.741),(0,0,1),.41,['Floor perimeter rim continuation'])
p45_doors=[o for o in house.objects if o.type=='MESH' and o.name.startswith('D01') and 'leaf' in o.name]
assert p45_doors and min(vr_bounds(o)[1][0] for o in p45_doors)>4.695
p45_report['checks'].append({'label':'D01 clear of Bedroom1','result':'PASS'})
p45_intrusions=[]
for p45_ob in house.objects:
    if p45_ob.type!='MESH' or not any('Brick' in m.name for m in p45_ob.data.materials):continue
    p45_b=vr_bounds(p45_ob)
    if all(min(p45_b[i][1],(8.815,7.775,2.73)[i])-max(p45_b[i][0],(6.485,4.699,.01)[i])>1e-4 for i in range(3)):
        p45_intrusions.append(p45_ob.name)
assert not p45_intrusions,('Masonry in finished laundry',p45_intrusions)
p45_report['checks'].append({'label':'No brickwork in finished laundry','result':'PASS'})
(OUT/'photo-review-0.4.5/geometry-response.json').write_text(json.dumps(p45_report,indent=2))
changes.append({'object':'Photo revision0.4.5','action':p45_report['changes'],'limitations':p45_report['limitations']})
