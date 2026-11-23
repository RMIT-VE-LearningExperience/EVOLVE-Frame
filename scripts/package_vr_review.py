from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, shutil, html, re
from datetime import datetime
root=Path(__file__).resolve().parents[1]
src=root/'unity-vr/Builds/Preview/Review'
version=re.search(r'^  bundleVersion: (.+)$',(root/'unity-vr/ProjectSettings/ProjectSettings.asset').read_text(encoding='utf-8'),re.M)[1]
out=root/('output/vr/review-'+version)
out.mkdir(parents=True,exist_ok=True)
shots=json.loads((src/'manifest.json').read_text(encoding='utf-8'))['shots']
shots.sort(key=lambda s: 10+int(s['file'][5:7]) if s['file'].startswith('room-') else int(s['file'][:2]))
stamp=datetime.fromtimestamp(max((src/s['file']).stat().st_mtime for s in shots)).strftime('%d %b %Y %H:%M')
for i,s in enumerate(shots,1):
 s['number']=i
 source_file=s['file']
 s['source_file']=source_file
 shutil.copy2(src/source_file,out/s['file'])
(out/'manifest.json').write_text(json.dumps({'version':version,'captured_local':stamp,'source':'Actual Unity URP scene renders,1600x1000; room guides hidden, with a separate inspection-controls view','shots':shots},indent=2))
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
heading=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',26)
groups=[('01-exteriors','Exterior views',[s for s in shots if s['category']=='Exterior']),('02-details','Stairs, canopy and alfresco',[s for s in shots if s['category']=='Details']),('03-rooms-a','Tour views 1–11',[s for s in shots if s['category']=='Rooms'][:11]),('04-rooms-b','Tour views 12–22',[s for s in shots if s['category']=='Rooms'][11:]),('05-structure','Exposed structure',[s for s in shots if s['category']=='Structure']),('06-entries','Corrected upstairs entrances',[s for s in shots if s['category']=='Entries'])]
groups.append(('07-fitout','Kitchen, bathrooms and joinery',[s for s in shots if s['category']=='Fitout']))
groups.append(('08-visibility','Fittings visibility and timber stairs',[s for s in shots if s['category']=='Visibility']))
groups.append(('09-photo-corrections','Latest headset-photo corrections',[s for s in shots if s['category']=='Photo corrections']))
groups.append(('10-architectural-details','Architectural details',[s for s in shots if s['category']=='Architectural details']))
for filename,title,items in groups:
 if not items:continue
 cols=2 if len(items)<=6 else 3; w=800 if cols==2 else 600; h=round(w/1.6); label=46; rows=(len(items)+cols-1)//cols
 sheet=Image.new('RGB',(cols*w,64+rows*(h+label)),(22,27,32)); draw=ImageDraw.Draw(sheet);draw.text((18,15),title+'  /  '+stamp,font=heading,fill=(242,234,219))
 for j,s in enumerate(items):
  x=(j%cols)*w;y=64+(j//cols)*(h+label)
  with Image.open(out/s['file']) as im: sheet.paste(im.resize((w,h),Image.Resampling.LANCZOS),(x,y))
  draw.text((x+12,y+h+8),f"{s['number']:02d}  {s['title']}",font=font,fill=(242,234,219))
 sheet.save(out/(filename+'.jpg'),quality=92)
cards='\n'.join(f'<button class="card" data-category="{s["category"]}" data-index="{i}" onclick="show({i})"><img loading="lazy" src="{s["file"]}" alt="{html.escape(s["title"])}"><span><b>{s["number"]:02d}</b> {html.escape(s["title"])}</span></button>' for i,s in enumerate(shots))
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EVOLVE Frame — visual review</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#13191e;color:#eee9df;font:16px system-ui,sans-serif}header,main{max-width:1500px;margin:auto;padding:30px}header{padding-bottom:10px}h1{font-size:30px;margin:4px 0 10px}p{color:#aeb9c0;max-width:820px;line-height:1.5}.chips{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0}.chips button,.tools button,.tools a{padding:10px 17px;border:1px solid #43505a;border-radius:6px;background:#25303a;color:#eee9df;font:inherit;cursor:pointer;text-decoration:none}.chips button.active{background:#dab77d;color:#191b1e;border-color:#dab77d}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}.card{padding:0;text-align:left;background:#222c34;border:1px solid #36424a;border-radius:9px;overflow:hidden;color:inherit;cursor:zoom-in;font:inherit}.card img{display:block;width:100%;aspect-ratio:1.6;object-fit:contain}.card span{display:block;padding:13px}.card b{color:#e7bd7c;margin-right:8px}.card:hover{border-color:#d7b47a}dialog{width:min(98vw,1700px);max-width:none;background:#13191e;border:1px solid #46545e;padding:15px;color:inherit}dialog::backdrop{background:#000e}#full{width:100%;max-height:78vh;object-fit:contain}.tools{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px}#caption{margin-right:auto;font-size:18px}[hidden]{display:none!important}
</style><header><div>EVOLVE FRAME / VISUAL REVIEW / 0.3.0</div><h1>House, rooms and construction details</h1><p>34 images rendered from the current Unity scene, with the menu hidden. Select an image for its full-size view. Use the image numbers when leaving feedback. These are desktop scene renders; headset appearance still needs review.</p><nav class="chips">'''
for category in ['All','Architectural details','Photo corrections','Visibility','Fitout','Entries','Exterior','Details','Rooms','Structure']: page+=f'<button class="{"active" if category=="All" else ""}" onclick="filter(this,\'{category}\')">{category}</button>'
page+='</nav></header><main class="grid">'+cards+'</main><dialog id="viewer"><div class="tools"><span id="caption"></span><button onclick="show(current-1)">← Previous</button><button onclick="show(current+1)">Next →</button><a id="original" target="_blank">Original PNG</a><button onclick="viewer.close()">Close</button></div><img id="full" alt=""></dialog><script>const shots='+json.dumps(shots)+''';let current=0;const viewer=document.getElementById('viewer');function show(i){current=(i+shots.length)%shots.length;const s=shots[current];document.getElementById('caption').textContent=String(s.number).padStart(2,'0')+' · '+s.title;document.getElementById('full').src=s.file;document.getElementById('full').alt=s.title;document.getElementById('original').href=s.file;if(!viewer.open)viewer.showModal()}function filter(button,category){document.querySelectorAll('.chips button').forEach(b=>b.classList.toggle('active',b===button));document.querySelectorAll('.card').forEach(c=>c.hidden=category!=='All'&&c.dataset.category!==category)}document.addEventListener('keydown',e=>{if(viewer.open&&e.key==='ArrowRight')show(current+1);if(viewer.open&&e.key==='ArrowLeft')show(current-1)});viewer.addEventListener('click',e=>{if(e.target===viewer)viewer.close()});</script></html>'''
page=page.replace('EVOLVE FRAME / VISUAL REVIEW / 0.3.0','LEICHHARDT / VISUAL REVIEW / '+version+' / '+stamp).replace('EVOLVE Frame — visual review','Leichhardt — visual review').replace('34 images rendered',str(len(shots))+' images rendered')
(out/'index.html').write_text(page,encoding='utf-8')
print(json.dumps({'folder':str(out),'images':len(shots),'contact_sheets':len(groups)}))
