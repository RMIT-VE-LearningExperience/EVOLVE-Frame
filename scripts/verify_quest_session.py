from pathlib import Path
import datetime, hashlib, json, re, subprocess, time, traceback, argparse
from PIL import Image

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description="Run the selected Quest release USB session checks; headset must be awake.")
parser.add_argument("--serial",required=True)
parser.add_argument("--version",help="Release to check; defaults to the Unity project version.")
args=parser.parse_args()
version=args.version or re.search(r'^  bundleVersion: (.+)$',(root/'unity-vr/ProjectSettings/ProjectSettings.asset').read_text(encoding='utf-8'),re.M)[1]
assert re.fullmatch(r'\d+\.\d+\.\d+',version),'Invalid release version'
evidence=root/f'output/vr/quest-{version}'
validated=json.loads((evidence/'apk-validation.json').read_text(encoding='utf-8'))
assert validated['result']=='PASS' and validated['version']==version
version_code=validated['version_code']
out=evidence/('live-'+datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S'))
out.mkdir(parents=True,exist_ok=True)
adb='C:/Program Files/Unity/Hub/Editor/6000.6.9f1/Editor/Data/PlaybackEngines/AndroidPlayer/SDK/platform-tools/adb.exe'
serial=args.serial
package='au.edu.evolve.framelab'
base='/sdcard/Android/data/'+package+'/files/'
records=[]
started=datetime.datetime.now().astimezone().isoformat()

def call(*args):
    return subprocess.run([adb,'-s',serial,*args],capture_output=True,text=True,check=True,timeout=30).stdout

def command(action,value=0,timeout=12,ready=None):
    cmd={'id':str(time.time_ns()),'action':action,'index':int(value),'value':float(value)}
    local=out/'command.json';local.write_text(json.dumps(cmd),encoding='utf-8')
    # Publish a complete command atomically so Unity never reads a partial ADB transfer.
    call('push',str(local),base+'device-command.pending.json')
    call('shell','mv',base+'device-command.pending.json',base+'device-command.json')
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        time.sleep(.3)
        try:s=json.loads(call('shell','cat',base+'device-state.json'))
        except (ValueError,subprocess.CalledProcessError):continue
        if s.get('id')==cmd['id'] and not s['changing']:
            if ready is not None and not ready(s):continue
            records.append({'action':action,'value':value,'state':s})
            (out/'suite-progress.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
            assert s['version']==version,s
            assert s['focused'],'Headset/app lost focus; keep wear sensor covered'
            print(json.dumps({'action':action,'value':value,'room':s['room'],'narration':s['narration'],'focused':s['focused']}),flush=True)
            return s
    raise RuntimeError('No focused completed response to '+action)

def capture(name):
    path=out/(name+'.png')
    with path.open('wb') as f:
        subprocess.run([adb,'-s',serial,'exec-out','screencap','-p'],stdout=f,check=True,timeout=20)
    with Image.open(path) as im:
        im.thumbnail((1600,1000));im.convert('RGB').save(out/(name+'-preview.jpg'),quality=92)

result={'started':started,'version':version,'serial':serial,
        'scope':'On-device cold startup and session control handlers via local USB diagnostic bridge. Narration means AudioSource playback state; actual sound and physical controller input are not independently observed.',
        'result':'IN_PROGRESS','checks':records}
try:
    result['model']=call('shell','getprop','ro.product.model').strip()
    assert result['model'] in ('Quest 3','Quest 3S'),'Unexpected headset model'
    assert 'mWakefulness=Awake' in call('shell','dumpsys','power'),'Headset is asleep'
    info=call('shell','dumpsys','package',package)
    assert f'versionName={version}' in info and re.search(r'versionCode='+str(version_code)+r'\b',info)
    call('shell','am','force-stop',package)
    launch=call('shell','am','start','-W','-n',package+'/com.unity3d.player.UnityPlayerGameActivity')
    (out/'launch.txt').write_text(launch,encoding='utf-8')
    assert 'Status: ok' in launch,launch
    s=command('status',timeout=30,ready=lambda state: state['guide'] and state['narration'] and state['location']==0)
    assert s['guide'] and s['narration'] and s['location']==0,'Cold-start welcome/narration failed'
    capture('01-startup')
    for index in range(22):
        s=command('goto',index)
        assert s['location']==index and s['narration'] and not s['detail'],s
        if index in (6,10,19):capture(f'room-{index+1:02}')
    s=command('menu');before=s['guide']
    s=command('menu');assert s['guide']!=before
    s=command('goto',6)
    assert len(s['fittingsShown'])==6 and all(s['fittingsShown'])
    for index in range(6):
        s=command('fitting',index)
        assert s['fittingsShown']==[i!=index for i in range(6)],s
        s=command('fitting',index);assert all(s['fittingsShown'])
    s=command('all-fittings',0);assert not any(s['fittingsShown'])
    capture('fittings-hidden')
    s=command('goto',10);assert not any(s['fittingsShown'])
    s=command('walls');assert s['framing']
    capture('walls-hidden')
    s=command('walls');assert not s['framing']
    s=command('roof');assert s['roofHidden']
    s=command('roof');assert not s['roofHidden']
    s=command('all-fittings',1);assert all(s['fittingsShown'])
    s=command('study');assert s['detail'] and s['hotspots']==9
    s=command('explode',.45);assert abs(s['explosion']-.45)<.001
    s=command('zoom',1.15);assert s['zoom']>1.1
    for degrees in (-180,-90,0,90,180):
        s=command('rotation',degrees)
        assert abs(s['rotation']-degrees)<.01 and abs(s['explosion']-.45)<.001 and s['zoom']>1.1
    s=command('part',3);assert s['narration']
    s=command('isolate');assert s['isolated'] and s['visibleParts']==1
    s=command('rotation',-45);assert abs(s['rotation']+45)<.01 and s['visibleParts']==1
    capture('rotation-slider-isolated')
    s=command('reset-study');assert s['rotation']==0 and s['explosion']==0 and abs(s['zoom']-1)<.001 and s['visibleParts']==9
    s=command('restart');assert s['location']==0 and s['guide'] and s['narration'] and all(s['fittingsShown']) and not s['framing'] and not s['roofHidden']
    capture('02-restored-welcome')
    result['result']='PASS'
    print('QUEST_'+version+'_LIVE_PASS '+str(len(records)),flush=True)
except Exception as exc:
    result['result']='INCOMPLETE' if ('focus' in str(exc).lower() or 'asleep' in str(exc).lower()) else 'FAIL'
    result['error']=str(exc)
    result['traceback']=traceback.format_exc()
    print(json.dumps({'result':result['result'],'error':str(exc)}),flush=True)
finally:
    result['finished']=datetime.datetime.now().astimezone().isoformat()
    result['command_count']=len(records)
    result['checks']=records
    (out/'suite-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    power=call('shell','dumpsys','power');(out/'power-final.txt').write_text(power,encoding='utf-8')
    try:
        pids=call('shell','pidof',package).strip().split()
        if pids:
            (out/'logcat.txt').write_text(call('logcat','-d','--pid='+pids[0]),encoding='utf-8')
    except subprocess.CalledProcessError:
        pass # Preserve the primary check failure when the app did not start.
if result['result']!='PASS':raise SystemExit(1)
