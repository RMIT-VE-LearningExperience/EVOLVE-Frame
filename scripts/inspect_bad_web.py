import json
from pathlib import Path
r=next(r for r in json.loads(Path('output/revit/floor_web_manifest.json').read_text()) if r['mark']=='SF-FJ2-01-MSW-07')
print(r)
try:
 import shapely
 from shapely.geometry import Polygon
 from shapely.validation import explain_validity
 for row in json.loads(Path('output/revit/floor_web_manifest.json').read_text()):
  poly=Polygon([(p[1],p[2]) for p in row['points']])
  if not poly.is_valid:print(row['mark'],explain_validity(poly))
except ImportError:print('No shapely')
