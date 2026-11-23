"""Check every visible pane from both sides of all19 scheduled windows."""
bpy.context.view_layer.update();wc_deps=bpy.context.evaluated_depsgraph_get()
wc_rows=[];wc_failures=[]
for wc_root in sorted([o for o in house.objects if o.name.startswith('OPENING | W')],key=lambda o:o.name):
    wc_glasses=[o for o in wc_root.children if o.type=='MESH' and 'glass' in o.name]
    wc_normal=(wc_root.matrix_world.to_quaternion()@Vector((0,1,0))).normalized()
    wc_rays=0;wc_blocked=[]
    for wc_glass in wc_glasses:
        for wc_fx in (.15,.5,.85):
            for wc_fz in (.15,.5,.85):
                wc_point=wc_glass.matrix_world@Vector((wc_fx-.5,0,wc_fz-.5))
                for wc_side in (-1,1):
                    wc_hit=house.ray_cast(wc_deps,wc_point+wc_normal*(.35*wc_side),wc_normal*(-wc_side),distance=.70)
                    wc_rays+=1
                    if not wc_hit[0] or wc_hit[4]!=wc_glass:
                        wc_blocked.append({'pane':wc_glass.name,'point':list(wc_point),'side':wc_side,
                                           'hit':wc_hit[4].name if wc_hit[0] else None})
    wc_rows.append({'window':wc_root.name,'panes':len(wc_glasses),'rays':wc_rays,'blocked':wc_blocked})
    if wc_blocked or not wc_glasses:wc_failures.append(wc_root.name)
wc_report={'result':'PASS' if not wc_failures else 'FAIL','scope':'18rays per pane across all19 scheduled window assemblies. Confirms absence of local model obstructions; drawing position/operation/finish acceptance remains separate.',
           'windows':wc_rows,'failures':wc_failures}
(OUT/'window-clearance-checks.json').write_text(json.dumps(wc_report,indent=2))
print('ALL_WINDOW_CLEARANCE',wc_report['result'],len(wc_rows),sum(r['rays'] for r in wc_rows),wc_failures,flush=True)
assert len(wc_rows)==19 and not wc_failures,wc_failures
