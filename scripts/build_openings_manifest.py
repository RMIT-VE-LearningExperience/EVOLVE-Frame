import json
from pathlib import Path
walls=json.loads(Path('output/revit/build_manifest.json').read_text())['walls'];out=[]
for wall in walls:
 for o in wall['openings']:
  mark=o['mark']
  if mark=='D-ENS-INNER':continue
  window=mark.startswith('W');key=mark if window or mark in ['D01','D02','D03','D04','D05-A','D05-B'] else f'Door-{o["width"]}x{o["height"]}'
  if mark=='D-WIR':key='Passage-800x2400'
  style='window' if window else 'garage' if mark=='D03' else 'glazed' if mark.startswith('D05') or mark=='D04' else 'passage' if mark=='D-WIR' else 'timber'
  panels=1;verticals=[];horizontals=[]
  if mark in ['W05','W06','W08']:verticals=[1/3,2/3]
  if mark in ['W07','W11','W14','W15','W17','W18','W19']:verticals=[.5]
  if mark in ['W02','W03','W05','W06','W10']:horizontals=[.25]
  if mark=='W01':verticals=[.3];horizontals=[1/3,2/3]
  if style=='glazed':verticals=[1/3,2/3]
  if mark=='D01':verticals=[.5]
  horizontal=wall['a'][1]==wall['b'][1]
  out.append(dict(mark=mark,family='LC '+key+' - A11',window=window,width=o['width'],height=o['height'],sill=wall['z']+o['sill'],wall=wall['mark'],x=o['centre'] if horizontal else wall['a'][0],y=wall['a'][1] if horizontal else o['centre'],style=style,verticals=verticals,horizontals=horizontals,obscure=mark in ['W03','W07','W12','W13','W16'],note='A07/A08 position, A11 overall sizes. Frame50x100 and glazing6mm are visual coordination profiles; manufacturer sections/glazing specification pending. Panel divisions follow schedule appearance, undimensioned divisions provisional.'))
Path('output/revit/openings_manifest.json').write_text(json.dumps(out,indent=2));print(len(out),'hosted window/door instances;',len(set(r['family'] for r in out)),'families')
