import { visiblePart, type Part, type ViewState } from './explorer.ts';

export function groupLayers(parts: Part[], building: boolean) {
  const definitions = building
    ? ([
        [
          'Walls & supports',
          [
            '02 Ground floor walls',
            '03 Ground floor steel and LVL',
            '05 Upper floor walls',
            '09 Bracing and connections',
          ],
        ],
        ['Floors & stairs', ['04 First floor joists', '10 Stair framing']],
        [
          'Roof framing',
          [
            '06 Upper roof trusses',
            '07 Garage roof',
            '08 Porch roof',
            '11 Roof battens',
          ],
        ],
        [
          'Wrap & cladding',
          ['23 Ground brick veneer', '24 Upper foam render', '25 Wall wrap'],
        ],
        [
          'Roof enclosure',
          [
            '20 Main roof covering',
            '21 Main roof sarking',
            '22 Fascia and gutters',
          ],
        ],
        ['Windows & doors', ['26 Windows and doors']],
      ] as const)
    : ([
        ['Structure', ['frame', 'joists', 'deck', 'battens']],
        [
          'Weather protection',
          ['wrap', 'sill', 'jamb', 'head', 'sarking', 'transition'],
        ],
        [
          'Finishes & fittings',
          [
            'window',
            'glass',
            'brick',
            'lining',
            'cladding',
            'roof',
            'fascia',
            'gutter',
            'soffit',
            'foam',
          ],
        ],
      ] as const);
  const groups: { label: string; parts: Part[] }[] = definitions
    .map(([label, keys]) => ({
      label,
      parts: parts.filter((p) => (keys as readonly string[]).includes(p.key)),
    }))
    .filter((g) => g.parts.length);
  const other = parts.filter((p) => !groups.some((g) => g.parts.includes(p)));
  if (other.length) groups.push({ label: 'Other layers', parts: other });
  return groups;
}
export function eligibleLayer(p: Part, s: ViewState) {
  return visiblePart(p, { ...s, hidden: [] });
}
export function toggleLayers(state: ViewState, parts: Part[]): ViewState {
  const eligible = parts.filter((p) => eligibleLayer(p, state));
  if (!eligible.length) return state;
  const hide = eligible.every((p) => visiblePart(p, state));
  const keys = eligible.map((p) => p.key);
  const hidden = state.hidden.filter((k) => !keys.includes(k));
  if (hide) hidden.push(...keys);
  return {
    ...state,
    hidden,
    selected:
      hide && keys.includes(state.selected ?? '') ? null : state.selected,
  };
}
