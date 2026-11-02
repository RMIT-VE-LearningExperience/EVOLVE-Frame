import type { ModelKey, Part, ViewState } from './explorer';
import { visiblePart } from './explorer.ts';

export type Hotspot = {
  id: string;
  title: string;
  part: string;
  stage: number;
  what: string;
  purpose: string;
  connects: string;
  question: string;
  basis: string;
  reference: string;
  measurement?: string;
  status: 'verified' | 'illustrative' | 'review';
  detail?: ModelKey;
};
export const hotspots: Hotspot[] = [
  {
    id: 'waffle-slab',
    title: 'Waffle slab — concealed system',
    part: '00 Waffle slab pods and ribs',
    stage: 0,
    what: 'A waffle slab uses void-forming pods between reinforced concrete ribs and beams.',
    purpose:
      'The ribs and beams form the load-carrying concrete system while the pods reduce concrete volume.',
    connects:
      'The slab bears on the prepared ground system; wall loads and slab steps must align with the verified engineering setout.',
    question:
      'Reveal the concealed detail. Can you distinguish the pods, ribs, beams, membrane and reinforcement layers?',
    basis:
      'The web geometry is diagrammatic. Do not read spacing, bar size, cover, rebates or soil classification from it.',
    reference:
      'Project engineering drawings and soil report — exact sheet/detail still requires Chris’s confirmation.',
    status: 'review',
  },
  {
    id: 'waffle-reinforcement',
    title: 'Slab reinforcement and membrane',
    part: '00 Waffle slab reinforcement',
    stage: 0,
    what: 'Mesh, trench reinforcement, chairs and membrane are normally concealed after the pour.',
    purpose:
      'Reinforcement resists designed actions; chairs maintain specified cover and the membrane separates the slab from the ground system.',
    connects:
      'Mesh and bars must be supported at the engineering-specified level and coordinated at beams, penetrations, steps and rebates.',
    question:
      'Which elements establish reinforcement cover, and which drawing would you use before quoting a dimension?',
    basis:
      'Representative visibility only; no reinforcement schedule or cover dimension is asserted.',
    reference:
      'Project engineering drawings; AS 2870 was discussed but edition, applicability and clauses remain unverified.',
    status: 'illustrative',
  },
  {
    id: 'raised-supports',
    title: 'Stumps, bearers and supported joints',
    part: '00 Raised floor bearers',
    stage: 0,
    what: 'The raised-floor alternative supports bearers on stumps, with bearer joints located over supports.',
    purpose:
      'Stumps transfer load to the footing system; bearers collect loads from the joists above.',
    connects:
      'Bearers sit on stumps and joists sit on bearers. The highlighted split demonstrates the principle of supporting a bearer joint.',
    question:
      'Why should a bearer joint occur over a support rather than between supports?',
    basis:
      'Alternative teaching system. Layout, member sizes, connections and footing design await an approved detail.',
    reference:
      'Chris discussion, Video 2; governing raised-floor project detail not yet supplied.',
    status: 'review',
  },
  {
    id: 'raised-joists',
    title: 'Ground-floor joists and sheet flooring',
    part: '00 Raised floor joists',
    stage: 1,
    what: 'Ground-floor joists span between bearers and support sheet flooring.',
    purpose:
      'The joists distribute floor loads to the bearers while blocking and edge support stabilise the system.',
    connects:
      'Joists connect to bearers below and sheet flooring above. This is distinct from the engineered upper-floor system.',
    question:
      'Follow one joist to both supports. What keeps the joist and sheet edge stable?',
    basis:
      'Representative teaching assembly; sheet product, thickness, spans and fixings are not nominated.',
    reference:
      'Chris discussion, Video 2; approved raised-floor detail required.',
    status: 'illustrative',
  },
  {
    id: 'service-penetration',
    title: 'Service penetration through joist zone',
    part: '00 Raised floor service penetration',
    stage: 1,
    what: 'A visible pipe demonstrates the coordination required where services pass through a timber floor zone.',
    purpose:
      'The service needs a route without removing timber outside the permitted zones or weakening connections.',
    connects:
      'The pipe passes through the joist zone; its final diameter and location must be checked against the member manufacturer or engineering detail.',
    question:
      'What information is needed before drilling or notching this member?',
    basis:
      'The pipe and opening are intentionally illustrative and are not an approved penetration.',
    reference:
      'Manufacturer or project engineering detail required; no dimension is asserted.',
    status: 'review',
  },
  {
    id: 'walls',
    title: 'Wall framing',
    part: '02 Ground floor walls',
    stage: 2,
    what: 'Studs, plates and noggings form the wall frame.',
    purpose:
      'Studs support vertical loads; plates connect the studs and transfer loads at the top and bottom of the wall.',
    connects:
      'Bottom plates connect to the floor system; top plates collect loads from upper framing. Corners and T-junctions provide fixing faces for linings and cladding support.',
    question:
      'Trace a load from the top plate to the support below. What changes at an opening?',
    basis:
      'Teaching explanation. Wall setout remains subject to the position audit.',
    reference:
      'Project engineering S12/S13 for wall framing; AS 1684 applicability and edition require verification.',
    status: 'review',
  },
  {
    id: 'window',
    title: 'Window opening',
    part: '26 Windows and doors',
    stage: 6,
    what: 'A window sits within an opening in the wall framing.',
    purpose:
      'The lintel and supporting framing provide a path for loads around the opening.',
    connects:
      'The lintel bears on jamb and stud packs; sill and cripple studs connect the opening back to the wall frame and weatherproofing layers.',
    question:
      'Which members support the lintel, and how is water managed around the window?',
    basis:
      'Opening assemblies are provisional. The detached detail is generic, not a verified project window.',
    reference:
      'Architectural sheet 11 window schedule; engineering S12/S13 for lintels and stud packs.',
    measurement:
      'W04 audit A01: model sill 1,419 mm; schedule 905 mm. Correction awaits approval.',
    status: 'review',
    detail: 'window',
  },
  {
    id: 'floor',
    title: 'Floor system',
    part: '04 First floor joists',
    stage: 3,
    what: 'The first-floor joists span between supporting members.',
    purpose:
      'The floor system transfers loads to the supporting walls and beams.',
    connects:
      'Engineered joists bear on walls, LVL or steel and are restrained by the documented blocking, strongbacks and edge members.',
    question:
      'Follow a joist to each end. What supports it, and where does the load go next?',
    basis:
      'Model floor zone is 400 mm; supplier study uses 413 mm. Chris must resolve the difference.',
    reference:
      'Subfloor shop drawings and layout page 47; architectural section 12.',
    measurement:
      'Audit A09: 400 mm model zone versus 413 mm supplier overall; 360 mm wet-area members are separate.',
    status: 'review',
    detail: 'floor-edge',
  },
  {
    id: 'roof',
    title: 'Roof truss bearing',
    part: '06 Upper roof trusses',
    stage: 5,
    what: 'Roof trusses meet supporting walls at their bearing locations.',
    purpose:
      'These supports transfer roof loads into the structure below; connections also need to resist uplift.',
    connects:
      'Truss bearings meet supporting wall plates and require the specified connector and tie-down arrangement.',
    question:
      'Where does each truss bear, and which connection details would you need to check?',
    basis:
      'The marker identifies the truss system, not an approved bearing or fixing detail.',
    reference:
      'Roof truss shop drawings and final layout; AS 4440 was discussed but exact application remains to be verified.',
    measurement:
      'Audit A08: T5 and T6 chord extensions and bearing positions are incomplete in the model.',
    status: 'review',
    detail: 'eaves',
  },
  {
    id: 'stairs',
    title: 'Stair opening',
    part: '10 Stair framing',
    stage: 2,
    what: 'The stair and surrounding floor framing accommodate an opening between levels.',
    purpose:
      'Members around the opening support the interrupted floor framing.',
    connects:
      'Trimmers collect the cut joists and transfer their loads to continuous members and supporting walls around the stair void.',
    question:
      'Which floor members stop at the opening, and what supports their ends?',
    basis:
      'Stair geometry and opening coordination remain subject to Chris’s review.',
    reference:
      'Architectural sheets 07 and 08; audit A05a/A05b.',
    measurement:
      'Sheets conflict: 3,190 mm versus 4,000 mm stair basis; void and dwarf-wall return remain uncoordinated.',
    status: 'review',
  },
  {
    id: 'bracing',
    title: 'Sheet and cross bracing',
    part: '09 Bracing and connections',
    stage: 2,
    what: 'The project combines sheet bracing and diagonal cross bracing in nominated wall bays.',
    purpose:
      'Bracing transfers lateral actions through the frame into the supporting structure.',
    connects:
      'Brace ends, wall plates, studs and hold-down locations must form a continuous load path.',
    question:
      'Can you identify the bracing type, its nominated bay length and the connection at each end?',
    basis:
      'The saved model has known bracing arrangement and bay-length discrepancies.',
    reference:
      'Engineering S18/S19.',
    measurement:
      'Audit A10: study-side D brace projects 2,604 mm against D2400; C2700 and two D1800 bays need reconciliation.',
    status: 'review',
  },
  {
    id: 'steel',
    title: 'Structural steel and LVL supports',
    part: '03 Ground floor steel and LVL',
    stage: 2,
    what: 'Steel and LVL members support loads where timber wall framing alone is not the documented solution.',
    purpose:
      'These members span openings or collect concentrated loads and transfer them to the supports below.',
    connects:
      'End bearings, posts, brackets, bolts and packers must match the engineering details rather than a generic visual connection.',
    question:
      'Where does this member bear, and which connection detail controls its end support?',
    basis:
      'ST2, HC1, 1L8 and 1L9 coverage remains to be reconciled; generic objects may already represent some locations.',
    reference:
      'Engineering S09/S10 and the checked NCC Part 6.3 screen-share reference.',
    status: 'review',
  },
  {
    id: 'garage',
    title: 'Garage roof',
    part: '07 Garage roof',
    stage: 5,
    what: 'The garage roof framing is present; its covering has been deferred.',
    purpose:
      'Its supports and roof extent must be coordinated before fitting the enclosure.',
    connects:
      'Garage wall setout, lowered datum, roof bearing and T5 truss extent must be resolved together.',
    question:
      'Ask Chris: how should the 86 mm wall-top/chord mismatch and garage setout be resolved?',
    basis:
      'UNRESOLVED: audit A02a, A02b and A07. No garage covering is modelled.',
    reference:
      'Architectural sheet 07 and roof truss shop drawing page 20 (printed 19).',
    measurement:
      'Nominal garage 6,000 × 6,500 mm; garage datum 86 mm below house; T5 overall extent 6,680 mm.',
    status: 'review',
  },
];
export function availableHotspots(state: ViewState, parts: Part[]) {
  return studyHotspots(state.model, parts).filter(
    (h) =>
      (state.model !== 'building' || h.stage <= state.stage) &&
      parts.some((p) => p.key === h.part && visiblePart(p, state)),
  );
}
export function studyHotspots(model: ModelKey, parts: Part[]): Hotspot[] {
  if (model === 'building')
    return hotspots.filter((h) => parts.some((p) => p.key === h.part));
  return parts.map((p) => ({
    id: `${model}:${p.key}`,
    title: p.label.replace(/^\d+\s+/, ''),
    part: p.key,
    stage: p.stage,
    what: p.note,
    purpose:
      'Use the highlighted layer and the exploded view to inspect how this component meets the adjacent layers.',
    connects:
      'Compare the assembled and separated views to identify the neighbouring layers and the direction in which loads or water must continue.',
    question:
      'Which layers touch this component when assembled, and which junction details would you need to verify?',
    basis:
      'Illustrative junction study, not a verified product or installation detail.',
    reference:
      'See the project Basis tab and source drawings before treating the junction as a construction detail.',
    status: 'illustrative',
  }));
}
