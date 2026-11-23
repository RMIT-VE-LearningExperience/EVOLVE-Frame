"""Install the verified Quest review APK only on a selected Quest 3/3S."""
from pathlib import Path
import argparse,subprocess,json,hashlib,datetime,re

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--serial',required=True)
parser.add_argument('--version',help='Release to install; defaults to the Unity project version.')
args=parser.parse_args()
adb='C:/Program Files/Unity/Hub/Editor/6000.6.9f1/Editor/Data/PlaybackEngines/AndroidPlayer/SDK/platform-tools/adb.exe'
version=args.version or re.search(r'^  bundleVersion: (.+)$',(root/'unity-vr/ProjectSettings/ProjectSettings.asset').read_text(encoding='utf-8'),re.M)[1]
assert re.fullmatch(r'\d+\.\d+\.\d+',version),'Invalid release version'
evidence=root/f'output/vr/quest-{version}'
validated=json.loads((evidence/'apk-validation.json').read_text(encoding='utf-8'))
apk=Path(validated['apk']);package='au.edu.evolve.framelab'
assert validated['result']=='PASS' and validated['version']==version
version_code=validated['version_code']
assert hashlib.sha256(apk.read_bytes()).hexdigest()==validated['sha256'],'APK changed since validation'
def call(*cmd):return subprocess.run([adb,'-s',args.serial,*cmd],capture_output=True,text=True,check=True,timeout=90).stdout
model=call('shell','getprop','ro.product.model').strip()
assert model in ('Quest 3','Quest 3S'),f'Unexpected headset: {model}'
result=call('install','-r',str(apk));assert 'Success' in result,result
info=call('shell','dumpsys','package',package)
assert f'versionName={version}' in info and re.search(r'versionCode='+str(version_code)+r'\b',info)
base=next(p.removeprefix('package:').strip() for p in call('shell','pm','path',package).splitlines() if p.endswith('/base.apk'))
assert base.startswith('/data/app/') and re.fullmatch(r'[A-Za-z0-9_./+=~\-]+',base)
installed=call('shell','sha256sum',base).split()[0]
assert installed==validated['sha256']
report={'result':'PASS','model':model,'serial':args.serial,'version':version,'version_code':version_code,
 'installed_apk_sha256':installed,'timestamp':datetime.datetime.now().astimezone().isoformat(),
 'scope':'Installation and exact APK identity. Live session and physical controls are separate checks.',
 'awake':'mWakefulness=Awake' in call('shell','dumpsys','power')}
(evidence/'installation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
