export type ModelKey = 'building' | 'window' | 'eaves' | 'floor-edge';
export type FoundationSystem = 'waffle' | 'raised';
export type Part = {
  key: string;
  label: string;
  note: string;
  stage: number;
  cut: boolean;
  explode: number[];
  system?: FoundationSystem;
  detailOnly?: boolean;
  concealsDetail?: boolean;
};
export type ViewState = {
  model: ModelKey;
  stage: number;
  cutaway: boolean;
  foundation: FoundationSystem;
  foundationDetail: boolean;
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
export const stageNames = [
  'Footings / slab',
  'Ground floor',
  'Ground walls',
  'Upper floor',
  'Upper walls',
  'Roof frame',
  'Enclosure',
];
export const initialState: ViewState = {
  model: 'building',
  stage: 6,
  cutaway: false,
  foundation: 'waffle',
  foundationDetail: false,
  explosion: 0,
  hidden: [],
  selected: null,
};

export function constructionStageForPart(part: Part) {
  if (part.system) return part.stage;
  if (/^0[23]\s/.test(part.key)) return 2;
  if (/^04\s/.test(part.key)) return 3;
  if (/^05\s/.test(part.key)) return 4;
  if (/^0[678]\s|^11\s/.test(part.key)) return 5;
  if (/^09\s|^10\s/.test(part.key)) return 2;
  if (/^2[0-6]\s/.test(part.key)) return 6;
  return Math.max(0, Math.min(6, part.stage));
}

export function visiblePart(part: Part, state: ViewState) {
  return (
    !state.hidden.includes(part.key) &&
    (state.model !== 'building' ||
      ((!part.system || part.system === state.foundation) &&
        constructionStageForPart(part) <= state.stage &&
        !(state.cutaway && part.cut) &&
        !(part.detailOnly && !state.foundationDetail) &&
        !(part.concealsDetail && state.foundationDetail)))
  );
}

const commonPart = {
  cut: false,
  explode: [0, 0, 0],
};

export const foundationParts: Record<FoundationSystem, Part[]> = {
  waffle: [
    {
      ...commonPart,
      key: '00 Waffle slab surface',
      label: 'Waffle slab surface and edge beam',
      note: 'Primary project teaching system. The web overlay shows relationships only; reinforcement sizes, beam schedules, rebates and setout must come from the engineering drawings.',
      stage: 0,
      system: 'waffle',
      concealsDetail: true,
    },
    {
      ...commonPart,
      key: '00 Waffle slab pods and ribs',
      label: 'Waffle pods, ribs and internal beams',
      note: 'Concealed relationship view. Pod and rib spacing is diagrammatic and is not a project dimension.',
      stage: 0,
      system: 'waffle',
      detailOnly: true,
    },
    {
      ...commonPart,
      key: '00 Waffle slab reinforcement',
      label: 'Mesh, trench reinforcement and bar chairs',
      note: 'Representative reinforcement layer for teaching visibility only. Use the project engineering sheets for bar sizes, laps, cover and beam schedules.',
      stage: 0,
      system: 'waffle',
      detailOnly: true,
    },
    {
      ...commonPart,
      key: '00 Waffle slab membrane',
      label: 'Membrane beneath slab',
      note: 'Diagrammatic membrane layer beneath the slab system. Project laps, penetrations and terminations require verified documentation.',
      stage: 0,
      system: 'waffle',
      detailOnly: true,
    },
  ],
  raised: [
    {
      ...commonPart,
      key: '00 Raised floor stumps',
      label: 'Stumps and support pads',
      note: 'Alternative teaching system. Layout, sizes and founding requirements are illustrative until Chris provides or approves the governing raised-floor detail.',
      stage: 0,
      system: 'raised',
    },
    {
      ...commonPart,
      key: '00 Raised floor bearers',
      label: 'Bearers and joints over supports',
      note: 'Bearers are shown supported by stumps, with a representative joint positioned over a support. Member sizes and fixings are not specified.',
      stage: 0,
      system: 'raised',
    },
    {
      ...commonPart,
      key: '00 Raised floor joists',
      label: 'Ground-floor joists and blocking',
      note: 'Joists are shown supported by bearers. This ground-level system is intentionally distinct from the engineered upper-floor framing.',
      stage: 1,
      system: 'raised',
    },
    {
      ...commonPart,
      key: '00 Raised floor sheet flooring',
      label: 'Sheet flooring',
      note: 'Contemporary particleboard or plywood sheet flooring is represented without nominating a product, thickness or fixing schedule.',
      stage: 1,
      system: 'raised',
      concealsDetail: true,
    },
    {
      ...commonPart,
      key: '00 Raised floor service penetration',
      label: 'Service penetration through joist zone',
      note: 'A visible pipe demonstrates why penetrations and notches need coordination. Its position is illustrative, not an approved cut location.',
      stage: 1,
      system: 'raised',
      detailOnly: true,
    },
  ],
};

export function modelParts(parts: Part[], state: ViewState) {
  return state.model === 'building'
    ? [...foundationParts[state.foundation], ...parts]
    : parts;
}

const buildingVerticalOffsets: Record<string, number> = {
  '02 Ground floor walls': 0,
  '03 Ground floor steel and LVL': 0,
  '04 First floor joists': 2.25,
  '05 Upper floor walls': 4.5,
  '06 Upper roof trusses': 7.5,
  '07 Garage roof': 3.8,
  '08 Porch roof': 3.8,
  '09 Bracing and connections': 0,
  '10 Stair framing': 0,
  '11 Roof battens': 8.2,
  '20 Main roof covering': 10.2,
  '21 Main roof sarking': 9.2,
  '22 Fascia and gutters': 9.7,
  '23 Ground brick veneer': 0.8,
  '24 Upper foam render': 5.5,
  '25 Wall wrap': 5,
  '26 Windows and doors': 3,
};
const buildingExplosionScale = 5;
const maximumBuildingVerticalOffset = Math.max(
  ...Object.values(buildingVerticalOffsets),
);

function explosionAmount(state: ViewState) {
  return Number.isFinite(state.explosion)
    ? Math.max(0, Math.min(1, state.explosion))
    : 0;
}

export function verticalExplosionOffset(part: Part, state: ViewState) {
  if (state.model !== 'building' || part.system) return 0;
  return (
    (buildingVerticalOffsets[part.key] ?? part.stage * 1.2) *
    explosionAmount(state) *
    buildingExplosionScale
  );
}

export function buildingExplosionHeight(state: ViewState) {
  return state.model === 'building'
    ? maximumBuildingVerticalOffset *
        explosionAmount(state) *
        buildingExplosionScale
    : 0;
}
export function validateNavigation(input: unknown): Partial<ViewState> {
  if (!input || typeof input !== 'object' || Array.isArray(input))
    throw new Error('Expected an object.');
  const p = input as Record<string, unknown>;
  if (
    Object.keys(p).some(
      (k) =>
        ![
          'model',
          'stage',
          'cutaway',
          'foundation',
          'foundationDetail',
          'explosion',
        ].includes(k),
    )
  )
    throw new Error('Unknown navigation field.');
  if (typeof p.model !== 'string' || !modelKeys.includes(p.model as ModelKey))
    throw new Error('Choose building, window, eaves or floor-edge.');
  if (
    p.stage !== undefined &&
      (!Number.isInteger(p.stage) || Number(p.stage) < 0 || Number(p.stage) > 6)
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
  if (
    p.foundation !== undefined &&
    p.foundation !== 'waffle' &&
    p.foundation !== 'raised'
  )
    throw new Error('Foundation must be waffle or raised.');
  if (
    p.foundationDetail !== undefined &&
    typeof p.foundationDetail !== 'boolean'
  )
    throw new Error('Foundation detail must be a boolean.');
  return {
    model: p.model as ModelKey,
    stage: p.stage === undefined ? 0 : Number(p.stage),
    cutaway: p.cutaway === true,
    foundation:
      p.foundation === 'raised' ? 'raised' : initialState.foundation,
    foundationDetail: p.foundationDetail === true,
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
    'Begin with the ground system',
    'Inspect the primary waffle slab or switch to the alternative stump-and-bearer system. Reveal concealed parts before adding the building above.',
  ],
  [
    'Complete the ground floor',
    'For the raised-floor option, joists and sheet flooring follow the stump-and-bearer supports. The waffle slab already forms the ground floor.',
  ],
  [
    'Stand the ground-floor walls',
    'Add ground-floor wall framing, structural steel and LVL, bracing, openings and the stair support zone.',
  ],
  [
    'Install the upper-floor system',
    'Add the engineered upper-floor framing. Keep it distinct from the alternative stump, bearer and joist system below.',
  ],
  [
    'Stand the upper-floor walls',
    'Add upper walls and inspect their relationship with the floor edge, bracing and openings.',
  ],
  [
    'Set out the roof framing',
    'Add roof trusses, battens and the garage and porch roof frames. Supplier bearings and special trusses remain review items.',
  ],
  [
    'Enclose the frame',
    'Add wrap, windows and doors, cladding, roof sarking, roof covering, fascia and gutters. Use reveal framing to see the structure behind the enclosure.',
  ],
];
