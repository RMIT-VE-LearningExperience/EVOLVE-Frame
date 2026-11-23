"""Keep independently removable fittings in separate export batches.

No extra or overlapping solids. Floor finishes stay with the enclosure; the
stair's treads, closed timber risers and stringers remain structural geometry.
"""
def vr_visibility_group(obj, original):
    name=obj.name.removeprefix('Fitout | ')
    if original=='27 Fixed joinery and fixtures':
        if name.endswith('tiled floor'):return original
        if name.startswith(('Kitchen','Island','Dishwasher','Cooktop','Microwave','Concealed rangehood')):return '30 Kitchen'
        if name.startswith(('Laundry','Washer','Dryer')):return '31 Laundry'
        if name.startswith(('WIR','Bedroom','Upper linen')):return '32 Wardrobes and linen'
        if 'vanity' in name:return '33 Vanities and mirrors'
        if 'shower' in name or name=='Bath 2 east screen':return '34 Showers'
        if ' WC' in name:return '35 Toilets'
        raise AssertionError('Unclassified removable fixture: '+obj.name)
    if original.startswith('12') and any(token in obj.name.lower() for token in ('handrail','newel','baluster','bracket')):
        return '29 Stair finish balustrade'
    return original

classified=[(obj,vr_visibility_group(obj,group),cut) for obj,group,cut in classified]
visibility_report={group:[obj.name for obj,g,cut in classified if g==group]
                   for group in sorted({g for obj,g,cut in classified}) if int(group[:2])>=29}
assert all(any(group.startswith(str(n)) for group in visibility_report) for n in range(29,36))
(OUT/'visibility-groups.json').write_text(json.dumps(visibility_report,indent=2))
