export type ModelKey = 'building' | 'window' | 'eaves' | 'floor-edge';
export type Part = {
  key: string;
  label: string;
  note: string;
  stage: number;
  cut: boolean;
  explode: number[];
};
export type ViewState = {
  model: ModelKey;
  stage: number;
  cutaway: boolean;
  explosion: number;
  hidden: string[];
  selected: string | null;
};
export const modelKeys: ModelKey[] = [
  'building',
  'window',
  'eaves',
  'floor-edge',
];
export const stageNames = ['Frame', 'Wrap', 'Cladding', 'Roof'];
export const initialState: ViewState = {
  model: 'building',
  stage: 3,
  cutaway: false,
  explosion: 0,
  hidden: [],
  selected: null,
};
export function visiblePart(part: Part, state: ViewState) {
  return (
    !state.hidden.includes(part.key) &&
    (state.model !== 'building' ||
      (part.stage <= state.stage && !(state.cutaway && part.cut)))
  );
}
export function validateNavigation(input: unknown): Partial<ViewState> {
  if (!input || typeof input !== 'object' || Array.isArray(input))
    throw new Error('Expected an object.');
  const p = input as Record<string, unknown>;
  if (
    Object.keys(p).some(
      (k) => !['model', 'stage', 'cutaway', 'explosion'].includes(k),
    )
  )
    throw new Error('Unknown navigation field.');
  if (typeof p.model !== 'string' || !modelKeys.includes(p.model as ModelKey))
    throw new Error('Choose building, window, eaves or floor-edge.');
  if (
    p.stage !== undefined &&
    (!Number.isInteger(p.stage) || Number(p.stage) < 0 || Number(p.stage) > 3)
  )
    throw new Error('Stage must be 0–3.');
  if (
    p.explosion !== undefined &&
    (typeof p.explosion !== 'number' ||
      !Number.isFinite(p.explosion) ||
      p.explosion < 0 ||
      p.explosion > 1)
  )
    throw new Error('Explosion must be 0–1.');
  if (p.cutaway !== undefined && typeof p.cutaway !== 'boolean')
    throw new Error('Cutaway must be a boolean.');
  return {
    model: p.model as ModelKey,
    stage: p.stage === undefined ? 0 : Number(p.stage),
    cutaway: p.cutaway === true,
    explosion: p.explosion === undefined ? 0 : Number(p.explosion),
    hidden: [],
    selected: null,
  };
}
export const lessons = {
  building: {
    title: 'Read the whole building.',
    kicker: '01 / BUILDING EXPLORER',
    intro:
      'Orbit the model, then reveal each construction layer. Select a part to see what it represents.',
    question:
      'Which elements carry the floor and roof loads down through the building?',
    note: 'The frame is preserved from the positioning audit. W04, stairs, floor levels and other discrepancies await Chris. Low roof coverings, full decking and D05 corner glazing remain deferred.',
  },
  window: {
    title: 'A window is a junction.',
    kicker: '02 / WINDOW OPENING',
    intro:
      'Separate the layers to distinguish the rough opening, the window product and the flashings around it.',
    question:
      'Can you trace the overlaps from the head, down the jambs, to the sill? Where must water be able to leave?',
    note: 'Generic teaching opening, not W04. Flashing folds, end dams, laps, supports, seals and installation clearances require the selected manufacturer’s detail.',
  },
  eaves: {
    title: 'Follow the roof to its edge.',
    kicker: '03 / WALL TO ROOF',
    intro:
      'Find the roof covering, sarking, battens, fascia, gutter and soffit. Reveal the parts that are usually hidden.',
    question:
      'What collects water from the roof? Which layer lies beneath the metal sheet, and what happens at its lower edge?',
    note: '25° main pitch follows the drawings. Profiles, fixings, overhang, gutter capacity, overflow, ventilation and membrane termination remain to be coordinated.',
  },
  'floor-edge': {
    title: 'Two skins. One transition.',
    kicker: '04 / FLOOR EDGE',
    intro:
      'Study where the lower brick veneer meets the upper foam/render system around the floor structure.',
    question:
      'How would you maintain drainage at this change of material? What support and movement details are still missing?',
    note: 'This detached sample uses the supplier’s 413 mm zone and 19 mm board. The house remains at 400 mm pending Chris. Do not transfer the sample’s datum to the building.',
  },
};
export const stageLessons = [
  [
    'The supporting skeleton',
    'Trace the walls, floor joists, roof trusses and stair framing. Steel and LVL members remain part of this structural model.',
  ],
  [
    'A second line of defence',
    'Reveal the wall wrap and roof sarking. Their products, laps and junctions need to work with the chosen enclosure systems.',
  ],
  [
    'The external skin',
    'Add lower brick veneer, upper foam/render and provisional opening assemblies. Switch on cutaway to see the structure behind them.',
  ],
  [
    'The main roof enclosure',
    'Reveal the main metal roof, fascia and gutters. The garage and porch coverings are intentionally still absent.',
  ],
];
