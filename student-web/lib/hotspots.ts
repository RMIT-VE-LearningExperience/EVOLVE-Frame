import type { ModelKey, Part, ViewState } from './explorer';

export type Hotspot = {
  id: string;
  title: string;
  part: string;
  stage: number;
  what: string;
  purpose: string;
  question: string;
  basis: string;
  detail?: ModelKey;
};
export const hotspots: Hotspot[] = [
  {
    id: 'walls',
    title: 'Wall framing',
    part: '02 Ground floor walls',
    stage: 0,
    what: 'Studs, plates and noggings form the wall frame.',
    purpose:
      'Studs support vertical loads; plates connect the studs and transfer loads at the top and bottom of the wall.',
    question:
      'Trace a load from the top plate to the support below. What changes at an opening?',
    basis:
      'Teaching explanation. Wall setout remains subject to the position audit.',
  },
  {
    id: 'window',
    title: 'Window opening',
    part: '26 Windows and doors',
    stage: 2,
    what: 'A window sits within an opening in the wall framing.',
    purpose:
      'The lintel and supporting framing provide a path for loads around the opening.',
    question:
      'Which members support the lintel, and how is water managed around the window?',
    basis:
      'Opening assemblies are provisional. The detached detail is generic, not a verified project window.',
    detail: 'window',
  },
  {
    id: 'floor',
    title: 'Floor system',
    part: '04 First floor joists',
    stage: 0,
    what: 'The first-floor joists span between supporting members.',
    purpose:
      'The floor system transfers loads to the supporting walls and beams.',
    question:
      'Follow a joist to each end. What supports it, and where does the load go next?',
    basis:
      'Model floor zone is 400 mm; supplier study uses 413 mm. Chris must resolve the difference.',
    detail: 'floor-edge',
  },
  {
    id: 'roof',
    title: 'Roof truss bearing',
    part: '06 Upper roof trusses',
    stage: 0,
    what: 'Roof trusses meet supporting walls at their bearing locations.',
    purpose:
      'These supports transfer roof loads into the structure below; connections also need to resist uplift.',
    question:
      'Where does each truss bear, and which connection details would you need to check?',
    basis:
      'The marker identifies the truss system, not an approved bearing or fixing detail.',
    detail: 'eaves',
  },
  {
    id: 'stairs',
    title: 'Stair opening',
    part: '10 Stair framing',
    stage: 0,
    what: 'The stair and surrounding floor framing accommodate an opening between levels.',
    purpose:
      'Members around the opening support the interrupted floor framing.',
    question:
      'Which floor members stop at the opening, and what supports their ends?',
    basis:
      'Stair geometry and opening coordination remain subject to Chris’s review.',
  },
  {
    id: 'garage',
    title: 'Garage roof',
    part: '07 Garage roof',
    stage: 0,
    what: 'The garage roof framing is present; its covering has been deferred.',
    purpose:
      'Its supports and roof extent must be coordinated before fitting the enclosure.',
    question:
      'Ask Chris: how should the 86 mm wall-top/chord mismatch and garage setout be resolved?',
    basis:
      'UNRESOLVED: audit A02a, A02b and A07. No garage covering is modelled.',
  },
];
export function availableHotspots(state: ViewState, parts: Part[]) {
  return hotspots.filter(
    (h) =>
      state.model === 'building' &&
      h.stage <= state.stage &&
      parts.some(
        (p) =>
          p.key === h.part &&
          p.stage <= state.stage &&
          !state.hidden.includes(p.key) &&
          !(state.cutaway && p.cut),
      ),
  );
}
