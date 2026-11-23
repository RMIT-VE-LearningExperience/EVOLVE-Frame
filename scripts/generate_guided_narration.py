"""Generate only missing/changed Clara clips, strictly within included credits."""
import json, hashlib, urllib.request, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
env={}
for line in (root/'.env.narration.local').read_text(encoding='utf-8-sig').splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k,v=line.split('=',1);env[k.strip()]=v.strip().strip('\"\'')
key=env.get('ELEVENLABS_API_KEY') or env.get('ELEVEN_LABS_API_KEY')
assert key,'Narration key not configured'
def request(path,data=None):
    req=urllib.request.Request('https://api.elevenlabs.io/v1/'+path,
        data=json.dumps(data).encode() if data else None,
        headers={'xi-api-key':key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=120) as response: return response.read()
config=json.loads((root/'output/narration/clara_welcome_sample.json').read_text())
tour=json.loads((root/'unity-vr/Assets/FrameLab/Content/tour.json').read_text(encoding='utf-8'))
out=root/'unity-vr/Assets/FrameLab/Audio/Tour';out.mkdir(exist_ok=True)
pending=[]
inspection=json.loads((root/'unity-vr/Assets/FrameLab/Content/inspection.json').read_text(encoding='utf-8'))
part_rows=[dict(id='part_'+p['id'],caption=p['caption']) for p in inspection['parts']]
for row in tour['rooms']+tour['studies']+part_rows:
    payload=dict(text=row['caption'],model_id=config['model_id'],voice_settings=config['voice_settings'])
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    clip=out/(row['id']+'.mp3');meta=out/(row['id']+'.json')
    if clip.exists() and meta.exists() and json.loads(meta.read_text())['sha256']==digest: continue
    pending.append((row,payload,digest,clip,meta))
subscription=json.loads(request('user/subscription'))
remaining=subscription['character_limit']-subscription['character_count']
characters=sum(len(row['caption']) for row,*_ in pending)
assert not subscription.get('allowed_to_extend_character_limit'), 'Abort: overage spending is enabled'
assert characters+1000<remaining,'Abort: insufficient included credits'
print(f'Included-credit preflight: {characters} characters needed; {remaining} available; no overage.',flush=True)
for row,payload,digest,clip,meta in pending:
    audio=request('text-to-speech/'+config['voice_id']+'?output_format=mp3_44100_128',payload)
    assert len(audio)>1000,'Invalid narration response'
    clip.write_bytes(audio)
    meta.write_text(json.dumps(dict(sha256=digest,voice_id=config['voice_id'],**payload),indent=2),encoding='utf-8')
    print('Saved '+row['id'],flush=True)
print('NARRATION_COMPLETE',flush=True)
