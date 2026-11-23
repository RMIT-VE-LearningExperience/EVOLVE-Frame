"""Prepare the current Unity review gallery for private mobile hosting."""
from pathlib import Path
from html.parser import HTMLParser
import json
import shutil
import re
import html

root = Path(__file__).resolve().parents[1]
version = re.search(r'^  bundleVersion: (.+)$', (root/'unity-vr/ProjectSettings/ProjectSettings.asset').read_text(encoding='utf-8'), re.M)[1]
source = root / ('output/vr/review-' + version)
site = root / 'sites/leichhardt-review'
dest = site / 'dist'
dest.mkdir(parents=True, exist_ok=True)
manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
for shot in manifest['shots']:
    shutil.copy2(source / shot['file'], dest / shot['file'])
shutil.copy2(source / 'manifest.json', dest / 'manifest.json')
page = (source / 'index.html').read_text(encoding='utf-8')
page = page.replace('← Previous', 'Previous').replace('Next →', 'Next')
page = page.replace('Original PNG', 'Open full-size image')
page = page.replace('target="_blank"', 'target="_blank" rel="noopener"')
page = page.replace(f'{len(manifest["shots"])} images rendered from the current Unity scene, with the menu hidden. Select an image for its full-size view. Use the image numbers when leaving feedback. These are desktop scene renders; headset appearance still needs review.',
    f'{len(manifest["shots"])} images from Leichhardt {version}. Tap a view to inspect it, then open the full-size image to pinch and zoom on your phone. Use the image numbers when leaving feedback. View70 shows the inspection controls. These are desktop Unity renders; architectural corrections and headset review are still in progress.')
css = '''
html{scrollbar-gutter:stable}body{overflow-wrap:anywhere}
header,main{padding:24px}.grid{grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr))}
.card{min-width:0}.card:focus-visible,button:focus-visible,a:focus-visible{outline:3px solid #f1c988;outline-offset:3px}
.chips button,.tools button,.tools a{min-height:44px}.tools a{display:inline-flex;align-items:center}
dialog{box-sizing:border-box;max-height:96dvh;overflow:auto}#full{display:block;max-height:72dvh}
@media(max-width:600px){header,main{padding:16px}h1{font-size:26px}.chips{gap:7px}.chips button{padding:10px 13px}.grid{gap:16px}dialog{width:100vw;max-height:100dvh;border-radius:0;padding:12px}.tools{gap:8px}.tools #caption{flex-basis:100%;font-size:17px}.tools button,.tools a{font-size:14px;padding:10px 12px}#full{max-height:65dvh}}
'''
page = page.replace('</style>', css + '</style>')
page = page.replace('</p><nav', '</p><p><a style="color:#e7bd7c" href="review.html">Claude’s findings and update status</a></p><p>Exterior height coordination and the theatre step remain unresolved. Room viewing directions changed. Images 49 and 50 retain earlier cameras to check the reported junctions.</p><nav')
(dest / 'index.html').write_text(page, encoding='utf-8')
response = json.loads((root/f'output/vr/photo-review-{version}/codex-response.json').read_text(encoding='utf-8'))
comparison_images = 0
if response.get('latest_note'):
    latest = '<p style="color:#eee9df">'+html.escape(response['latest_note'])+'</p>'
    if version == '0.4.2':
        latest += '<p><a style="color:#e7bd7c" href="51-bathroom-tile-floor.png">Bathroom floor close-up</a> · <a style="color:#e7bd7c" href="52-bathroom-tile-return.png">Bathroom walls and doorway</a></p>'
        shutil.copy2(root/'output/vr/review-0.4.1/46-upperbath-fitout.png',dest/'bathroom-before.png')
        latest += '<details><summary>Compare the bathroom before and after</summary><p>Before (0.4.1)</p><img loading="lazy" style="width:100%;max-width:900px" src="bathroom-before.png" alt="Upper bathroom before the tile repair"><p>After (0.4.2), same camera</p><img loading="lazy" style="width:100%;max-width:900px" src="46-upperbath-fitout.png" alt="Upper bathroom after the tile repair"></details>'
        comparison_images += 2
    for featured in response.get('featured_images',[]):
        assert (dest/featured['file']).is_file()
        latest += '<p><a style="color:#e7bd7c" href="'+html.escape(featured['file'])+'">'+html.escape(featured['title'])+'</a></p>'
    for comparison in response.get('comparisons',[]):
        baseline = root/('output/vr/review-'+comparison['before_version'])/comparison.get('before_file',comparison['file'])
        asset = comparison['before_asset']
        assert Path(asset).name==asset and (dest/comparison['file']).is_file()
        shutil.copy2(baseline,dest/asset)
        before_label=comparison.get('before_label','Before ('+comparison['before_version']+')')
        after_label=comparison.get('after_label','After ('+version+'), same camera')
        latest += '<details><summary>'+html.escape(comparison['title'])+'</summary><p>'+html.escape(before_label)+'</p><img loading="lazy" style="width:100%;max-width:900px" src="'+html.escape(asset)+'" alt="'+html.escape(before_label)+'"><p>'+html.escape(after_label)+'</p><img loading="lazy" style="width:100%;max-width:900px" src="'+html.escape(comparison['file'])+'" alt="'+html.escape(after_label)+'"></details>'
        comparison_images += 2
    page = page.replace('<nav class="chips">',latest+'<nav class="chips">')
    (dest/'index.html').write_text(page,encoding='utf-8')
review = (root/response.get('claude_review_file','output/vr/photo-review-0.4.0/claude-review.txt')).read_text(encoding='utf-8')
cards = ''.join(f'<article><h2>{html.escape(i["id"])} — {html.escape(i["title"])}</h2><b>{html.escape(i["status"])}</b><p>{html.escape(i["response"])}</p></article>' for i in response['items'])
report = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Leichhardt — Claude review</title><style>body{background:#13191e;color:#eee9df;font:16px/1.65 system-ui;margin:0 auto;padding:24px;max-width:850px}a{color:#e7bd7c}h1{font-size:28px}h2{font-size:20px}article{padding:18px 0;border-bottom:1px solid #43505a}article b{color:#e7bd7c}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}summary{cursor:pointer;padding:20px 0}</style><p><a href="index.html">Back to updated photos</a></p><h1>Claude’s review and Codex updates</h1><p>Claude Fable 5.2 reviewed all 48 earlier views through seven contact sheets and 14 original PNGs, with plan sheets 07–10. The review is independent; it is not certification of the design or headset performance.</p>'+cards+'<details><summary>Read Claude’s original review of 0.4.0</summary><pre>'+html.escape(review)+'</pre></details></html>'
followup = (root/'output/vr/photo-review-0.4.1/claude-review.txt').read_text(encoding='utf-8')
report = report.replace('</html>', '<details><summary>Claude’s follow-up before the final corrections</summary><p>This review describes the intermediate 23:39 capture. The item statuses above describe the later correction pass.</p><pre>' + html.escape(followup) + '</pre></details></html>')
if response.get('claude_review_file'):
    # A new review must not inherit the old0.4.0 inspection/provenance claims.
    style=report.split('<style>',1)[1].split('</style>',1)[0]
    report='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Leichhardt review</title><style>'+style+'</style><p><a href="index.html">Back to updated photos</a></p><h1>Architectural review and updates</h1><p>'+html.escape(response['review_intro'])+'</p>'+cards+'<details><summary>Read Claude’s review of this revision</summary><pre>'+html.escape(review)+'</pre></details></html>'
(dest/'review.html').write_text(report,encoding='utf-8')
latest_review=root/f'output/vr/photo-review-{version}/claude-review.txt'
if latest_review.exists() and version not in ('0.4.0','0.4.1') and not response.get('claude_review_file'):
    report=report.replace('<h1>Claude’s review and Codex updates</h1>',
        '<h1>Claude’s review and Codex updates</h1><p>Latest review: Claude inspected the 12 submitted headset photographs for the 0.4.5 revision. That photo review did not open the drawing sheets; Codex subsequently checked the relevant architectural sheets directly. Item statuses distinguish implemented corrections from remaining issues.</p>')
    report=report.replace('</html>','<details><summary>Latest Claude review of the submitted headset photos</summary><pre>'+html.escape(latest_review.read_text(encoding='utf-8'))+'</pre></details></html>')
    (dest/'review.html').write_text(report,encoding='utf-8')

class GalleryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and attrs.get('src'):
            self.images.append(attrs['src'])

parsed = GalleryParser()
parsed.feed(page)
assert len(parsed.images) == len(manifest['shots']) + comparison_images and len(manifest['shots']) >= 48
assert all((dest / name).is_file() for name in parsed.images)
assert 'C:/' not in page and 'D:/' not in page and 'file://' not in page
assert 'width=device-width' in page
script = page.split('<script>', 1)[1].split('</script>', 1)[0]
(site / 'gallery-check.js').write_text(script, encoding='utf-8')
(site / 'README.md').write_text(f'Private Leichhardt {version} review gallery. Generated by scripts/package_phone_review.py in the main Leichhardt workspace. Source images are unchanged Unity renders. No original plan PDFs, credentials or model files are included.\n', encoding='utf-8')
print(json.dumps({'review_images': len(manifest['shots']), 'folder': str(dest), 'bytes': sum(p.stat().st_size for p in dest.iterdir() if p.is_file())}))
