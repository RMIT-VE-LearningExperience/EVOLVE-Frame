"""Targeted regression probes on the actual Unity captures, not ideal renders."""
from pathlib import Path
import json,re
from PIL import Image, ImageStat

root=Path(__file__).resolve().parents[1]
version=re.search(r'^  bundleVersion: (.+)$',(root/'unity-vr/ProjectSettings/ProjectSettings.asset').read_text(),re.M)[1]
current=root/('output/vr/review-'+version)
baseline=root/'output/vr/review-0.4.0'
checks=[]
for label,old_name,new_name,point,minimum in [
 ('Bedroom5 robe-head plaster','room-21-bedroom5.png','49-bedroom5-robe-check.png',(1450,35),100),
 ('Upper-bath wall end','37-upperbath-from-hall.png','37-upperbath-from-hall.png',(565,400),100),
 ('Powder privacy glass','39-powder-window.png','39-powder-window.png',(800,500),140)]:
    def rgb(folder,name):
        im=Image.open(folder/name).convert('RGB');x,y=point
        return [round(v,1) for v in ImageStat.Stat(im.crop((x-2,y-2,x+3,y+3))).mean]
    before=rgb(baseline,old_name);after=rgb(current,new_name)
    checks.append({'surface':label,'pixel':point,'before_rgb':before,'after_rgb':after,
                   'pass':min(after)>minimum,'scope':'Known dark patch at the original camera, supplemented by full-image visual review.'})
geometry=json.loads((root/'output/vr/photo-revision.json').read_text())
assert geometry['new_garage_parts_upper_interior_aabb_check']['result']=='PASS'
assert geometry['porch_pier_caps']==2
result={'result':'PASS' if all(c['pass'] for c in checks) else 'FAIL','pixel_checks':checks,
        'garage_upper_interior':geometry['new_garage_parts_upper_interior_aabb_check'],
        'porch_pier_caps':2,'scope':'Targeted photo regressions only; not whole-model or headset acceptance.'}
report_dir=root/('output/vr/photo-review-'+version)
report_dir.mkdir(exist_ok=True)
(report_dir/'visual-regressions.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
assert result['result']=='PASS'
