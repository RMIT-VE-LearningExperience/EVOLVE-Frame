'use client';
import { useEffect, useState } from 'react';
import { flushSync } from 'react-dom';
import {
  Box,
  ArrowRight,
  ArrowLeft,
  Layers3,
  MousePointer2,
  CheckCircle2,
  ArrowUpRight,
} from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import ModelViewer from '@/components/model-viewer';
import { VerticalExplodeControls } from '@/components/vertical-explode-controls';
import { LayerPanel } from '@/components/layer-panel';
import manifest from '@/public/models/manifest.json';
import { studyHotspots, availableHotspots, type Hotspot } from '@/lib/hotspots';
import {
  initialState,
  lessons,
  modelParts,
  stageLessons,
  stageNames,
  modelKeys,
  validateNavigation,
  type ModelKey,
  type Part,
  type ViewState,
} from '@/lib/explorer';

export default function Home() {
  const [detailed, setDetailed] = useState(true);
  const [state, setState] = useState(initialState);
  const [panel, setPanel] = useState('learn');
  const [showHotspots, setShowHotspots] = useState(true);
  const [hotspotId, setHotspotId] = useState<string | null>(null);
  const [returnView, setReturnView] = useState<ViewState | null>(null);
  const lesson = lessons[state.model],
    isBuilding = state.model === 'building';
  const parts = modelParts(
    manifest.models[state.model].parts as Part[],
    state,
  );
  const selected = parts.find((p) => p.key === state.selected);
  const activeHotspots = availableHotspots(state, parts);
  const hotspots = studyHotspots(state.model, parts);
  const activeHotspot = activeHotspots.find(
    (h) => h.id === hotspotId && h.part === state.selected,
  );
  const chooseHotspot = (h: Hotspot) => {
    setHotspotId(h.id);
    setState((s) => ({ ...s, selected: h.part }));
    setPanel('learn');
  };
  const navigate = (model: ModelKey) => {
    setState({
      ...initialState,
      model,
      explosion: model === 'building' ? 0 : 0.65,
    });
    setPanel('learn');
  };
  useEffect(() => {
    const context = (
      document as Document & {
        modelContext?: {
          registerTool: (
            tool: unknown,
            options: { signal: AbortSignal },
          ) => unknown;
        };
      }
    ).modelContext;
    if (!context?.registerTool) return;
    const life = new AbortController();
    try {
      Promise.resolve(
        context.registerTool(
          {
            name: 'navigate_construction_study',
            title: 'Explore a construction study',
            description:
              'Navigate the visible Frame Lab model and configure a teaching stage or exploded junction. No model geometry is edited.',
            inputSchema: {
              type: 'object',
              properties: {
                model: { type: 'string', enum: modelKeys },
                stage: { type: 'integer', minimum: 0, maximum: 6 },
                cutaway: { type: 'boolean' },
                foundation: {
                  type: 'string',
                  enum: ['waffle', 'raised'],
                },
                foundationDetail: { type: 'boolean' },
                explosion: { type: 'number', minimum: 0, maximum: 1 },
              },
              required: ['model'],
              additionalProperties: false,
            },
            annotations: { readOnlyHint: false, untrustedContentHint: false },
            execute(input: unknown) {
              const next = { ...initialState, ...validateNavigation(input) };
              flushSync(() => {
                setState(next);
                setPanel('learn');
              });
              return {
                model: next.model,
                stage: next.stage,
                cutaway: next.cutaway,
                foundation: next.foundation,
                foundationDetail: next.foundationDetail,
                explosion: next.explosion,
                status: 'visible state updated',
              };
            },
          },
          { signal: life.signal },
        ),
      ).catch(() => {});
    } catch {}
    return () => life.abort();
  }, []);
  return (
    <main className="lab">
      <a className="skip-link" href="#lesson">
        Skip to learning content
      </a>
      <header className="masthead">
        <a href="./" className="brand">
          <Box size={28} /> FRAME LAB <span>LEICHHARDT</span>
        </a>
        <span className="review">
          <span /> Teaching model · review pending
        </span>
      </header>
      <nav className="study-nav" aria-label="Construction studies">
        {modelKeys.map((m, i) => (
          <button
            key={m}
            aria-current={state.model === m ? 'page' : undefined}
            onClick={() => {
              setReturnView(null);
              navigate(m);
            }}
          >
            <span>0{i + 1}</span>
            {['Building', 'Window opening', 'Wall to roof', 'Floor edge'][i]}
            <ArrowUpRight size={16} />
          </button>
        ))}
      </nav>
      <div className="workspace">
        <section className="viewer" aria-label={`${lesson.title} 3D viewer`}>
          <div className="view-heading">
            <span className="eyebrow">{lesson.kicker}</span>
            <h1>{lesson.title}</h1>
          </div>
          <ModelViewer
            parts={parts}
            onWalkthroughStart={() =>
              setState((s) => ({ ...s, explosion: 0, selected: null }))
            }
            hotspots={showHotspots ? activeHotspots : []}
            onHotspot={chooseHotspot}
            detailed={detailed}
            onQualityChange={setDetailed}
            key={state.model}
            state={state}
            onSelect={(key) => setState((s) => ({ ...s, selected: key }))}
            fallback={
              isBuilding
                ? './enclosure_assembled.png'
                : `./studies/${state.model}.png`
            }
          />
          <div className="view-caption">
            <MousePointer2 size={16} />
            <span>
              Drag to orbit · zoom · Shift-drag or use ↕ to move vertically
            </span>
          </div>
          <div className="view-stamp">
            {isBuilding
              ? `STAGE ${String(state.stage + 1).padStart(2, '0')} / ${stageNames[state.stage].toUpperCase()}`
              : 'DETACHED / ILLUSTRATIVE'}
            {state.cutaway && isBuilding ? ' · CUTAWAY' : ''}
          </div>
        </section>
        <aside className="lesson" id="lesson">
          <Tabs value={panel} onValueChange={(v) => setPanel(String(v))}>
            <TabsList className="panel-tabs">
              <TabsTrigger value="learn">Explore</TabsTrigger>
              <TabsTrigger value="layers">Layers</TabsTrigger>
              <TabsTrigger value="notes">Basis</TabsTrigger>
            </TabsList>
            <TabsContent value="learn">
              {isBuilding && (
                <>
                  <section
                    className="foundation-system-control"
                    aria-labelledby="foundation-system-heading"
                  >
                    <span className="eyebrow">GROUND SYSTEM</span>
                    <h2 id="foundation-system-heading">
                      Choose the construction system
                    </h2>
                    <div className="system-buttons">
                      <button
                        aria-pressed={state.foundation === 'waffle'}
                        onClick={() =>
                          setState((s) => ({
                            ...s,
                            foundation: 'waffle',
                            foundationDetail: false,
                            hidden: [],
                            selected: null,
                          }))
                        }
                      >
                        Waffle slab
                      </button>
                      <button
                        aria-pressed={state.foundation === 'raised'}
                        onClick={() =>
                          setState((s) => ({
                            ...s,
                            foundation: 'raised',
                            foundationDetail: false,
                            hidden: [],
                            selected: null,
                          }))
                        }
                      >
                        Raised floor
                      </button>
                    </div>
                    <p className="minor">
                      {state.foundation === 'waffle'
                        ? 'Primary project system. Reveal the concealed teaching overlay to inspect pods, ribs, beams, reinforcement and membrane.'
                        : 'Alternative teaching sequence. Stumps support bearers; bearers support joists; joists support sheet flooring.'}
                    </p>
                    <div className="toggle-row">
                      <span>Reveal concealed foundation details</span>
                      <Switch
                        checked={state.foundationDetail}
                        onCheckedChange={(value) =>
                          setState((s) => ({
                            ...s,
                            foundationDetail: value,
                            selected: null,
                          }))
                        }
                        aria-label="Reveal concealed foundation details"
                      />
                    </div>
                    <p className="minor">
                      Diagrammatic relationships only. No structural sizes,
                      reinforcement schedule or penetration location is
                      asserted.
                    </p>
                  </section>
                  <VerticalExplodeControls state={state} setState={setState} />
                </>
              )}
              {!isBuilding && returnView && (
                <button
                  className="wide-button return-view-button"
                  onClick={() => {
                    setState(returnView);
                    setReturnView(null);
                    setHotspotId(null);
                  }}
                >
                  <ArrowLeft size={17} /> Return to previous building view
                </button>
              )}
              {
                <section
                  className="hotspot-study"
                  aria-label="Learning hotspots"
                >
                  <div className="toggle-row">
                    <span>Show hotspots</span>
                    <Switch
                      checked={showHotspots}
                      onCheckedChange={setShowHotspots}
                      aria-label="Show hotspots on the model"
                    />
                  </div>
                  <p className="minor">
                    Choose a labelled callout or a topic below. Lines track the
                    related layer as you orbit or separate it. Callouts that
                    cannot fit stay available in this list.
                  </p>
                  <div className="hotspot-list">
                    {hotspots.map((h, i) => (
                      <button
                        key={h.id}
                        disabled={!activeHotspots.some((a) => a.id === h.id)}
                        aria-pressed={activeHotspot?.id === h.id}
                        onClick={() => chooseHotspot(h)}
                      >
                        <span>{i + 1}</span> {h.title}
                        {!activeHotspots.some((a) => a.id === h.id) && (
                          <small>Hidden in this view</small>
                        )}
                      </button>
                    ))}
                  </div>
                  {activeHotspot && (
                    <section className="selected-part" aria-live="polite">
                      <span className="eyebrow">
                        LEARNING HOTSPOT · REVIEW PENDING
                      </span>
                      <h2>{activeHotspot.title}</h2>
                      <h3>What it is</h3>
                      <p>{activeHotspot.what}</p>
                      <h3>What it does</h3>
                      <p>{activeHotspot.purpose}</p>
                      <h3>How it connects</h3>
                      <p>{activeHotspot.connects}</p>
                      {activeHotspot.measurement && (
                        <p className="measurement-note">
                          <strong>Measurement / audit</strong>
                          {activeHotspot.measurement}
                        </p>
                      )}
                      <h3>Drawing or reference</h3>
                      <p>{activeHotspot.reference}</p>
                      <h3>Pause & think</h3>
                      <p>{activeHotspot.question}</p>
                      <p className="minor">
                        {activeHotspot.status === 'review'
                          ? 'REVIEW REQUIRED · '
                          : activeHotspot.status === 'verified'
                            ? 'SOURCE CHECKED · '
                            : 'ILLUSTRATIVE · '}
                        {activeHotspot.basis}
                      </p>
                      {activeHotspot.detail && (
                        <button
                          className="wide-button"
                          onClick={() => {
                            setReturnView(state);
                            navigate(activeHotspot.detail!);
                          }}
                        >
                          View illustrative detail <ArrowRight size={17} />
                        </button>
                      )}
                      <button
                        className="text-button"
                        onClick={() => {
                          setHotspotId(null);
                          setState((s) => ({ ...s, selected: null }));
                        }}
                      >
                        Close hotspot
                      </button>
                    </section>
                  )}
                </section>
              }
              <span className="eyebrow">
                {isBuilding ? 'CONSTRUCTION STAGES' : 'JUNCTION STUDY'}
              </span>
              {isBuilding ? (
                <>
                  <div
                    className="stage-buttons"
                    aria-label="Construction stage"
                  >
                    {stageNames.map((name, i) => (
                      <button
                        key={name}
                        aria-pressed={state.stage === i}
                        onClick={() =>
                          setState((s) => ({
                            ...s,
                            stage: i,
                            hidden: [],
                            selected: null,
                          }))
                        }
                      >
                        <span>
                          {state.stage > i ? <CheckCircle2 size={16} /> : i + 1}
                        </span>
                        {name}
                      </button>
                    ))}
                  </div>
                  <h2>{stageLessons[state.stage][0]}</h2>
                  <p>{stageLessons[state.stage][1]}</p>
                  <div className="toggle-row">
                    <span>
                      <Layers3 size={18} /> Reveal framing
                    </span>
                    <Switch
                      checked={state.cutaway}
                      onCheckedChange={(v) =>
                        setState((s) => ({ ...s, cutaway: v }))
                      }
                      aria-label="Reveal framing behind the enclosure"
                    />
                  </div>
                  <p className="minor">
                    Removes selected enclosure faces so the supporting frame
                    remains readable.
                  </p>
                  <div className="step-controls">
                    <button
                      disabled={state.stage === 0}
                      onClick={() =>
                        setState((s) => ({
                          ...s,
                          stage: s.stage - 1,
                          hidden: [],
                          selected: null,
                        }))
                      }
                    >
                      <ArrowLeft size={16} /> Back
                    </button>
                    <button
                      disabled={state.stage === 6}
                      onClick={() =>
                        setState((s) => ({
                          ...s,
                          stage: s.stage + 1,
                          hidden: [],
                          selected: null,
                        }))
                      }
                    >
                      Next layer <ArrowRight size={16} />
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <h2>{lesson.title}</h2>
                  <p>{lesson.intro}</p>
                  <div className="explode">
                    <div>
                      <span id="explode-label">Separate the layers</span>
                      <output>{Math.round(state.explosion * 100)}%</output>
                    </div>
                    <Slider
                      aria-labelledby="explode-label"
                      value={[state.explosion * 100]}
                      min={0}
                      max={100}
                      step={1}
                      onValueChange={(v) =>
                        setState((s) => ({
                          ...s,
                          explosion: Number(Array.isArray(v) ? v[0] : v) / 100,
                        }))
                      }
                    />
                    <div className="slider-captions">
                      <span>Assembled</span>
                      <span>Exploded</span>
                    </div>
                  </div>
                  <p className="minor">
                    Expanded gaps reveal relationships, not installation
                    dimensions.
                  </p>
                </>
              )}
              {selected ? (
                <section className="selected-part" aria-live="polite">
                  <span className="eyebrow">SELECTED LAYER</span>
                  <h3>{selected.label}</h3>
                  <p>{selected.note}</p>
                  <button
                    className="text-button"
                    onClick={() => setState((s) => ({ ...s, selected: null }))}
                  >
                    Clear selection
                  </button>
                </section>
              ) : (
                <div className="selection-hint">
                  <MousePointer2 size={18} />
                  <span>Tap the model or choose a layer to inspect it.</span>
                </div>
              )}
              <section className="prompt">
                <span className="eyebrow">PAUSE & THINK</span>
                <p>{lesson.question}</p>
              </section>
              {!isBuilding && (
                <button
                  className="wide-button"
                  onClick={() => setPanel('layers')}
                >
                  Inspect individual layers <ArrowRight size={17} />
                </button>
              )}
            </TabsContent>
            <TabsContent value="layers">
              <span className="eyebrow">MODEL LAYERS</span>
              <h2>Layers</h2>
              <p className="minor">
                Expand a category. Use its eye to show or hide the group, or
                select individual layers. Stage and cutaway limits still apply.
              </p>
              <LayerPanel parts={parts} state={state} setState={setState} />
              <button
                className="text-button"
                onClick={() =>
                  setState((s) => ({ ...s, hidden: [], selected: null }))
                }
              >
                Restore stage layers
              </button>
              {selected && (
                <section className="selected-part" aria-live="polite">
                  <h3>{selected.label}</h3>
                  <p>{selected.note}</p>
                </section>
              )}
            </TabsContent>
            <TabsContent value="notes">
              <span className="eyebrow">EVIDENCE & ASSUMPTIONS</span>
              <h2>Read critically.</h2>
              <p>{lesson.note}</p>
              <div className="basis-card">
                <h3>Drawing-based</h3>
                <p>
                  Main roof: 25°. Upper skin: 100 mm foam/render. Plasterboard:
                  10 mm. Supplier floor board: 19 mm.
                </p>
                <span className="minor">
                  Architectural sheets 03, 08–12; subfloor layout p. 47.
                </span>
              </div>
              <div className="basis-card">
                <h3>Illustrative, not specified</h3>
                <p>
                  Brick/cavity split, window products, flashing folds, fixings,
                  seals, insulation performance, roof profiles and colours.
                </p>
              </div>
              <h3 className="reading-heading">Continue reading</h3>
              <a
                className="reading-link"
                href="https://www.agwa.com.au/AGWA/Media/VidContent/Installation.aspx"
                target="_blank"
                rel="noreferrer"
              >
                AGWA · window installation <ArrowUpRight size={15} />
              </a>
              <a
                className="reading-link"
                href="https://lysaght.com/support-technical/downloads"
                target="_blank"
                rel="noreferrer"
              >
                Lysaght · roofing manuals <ArrowUpRight size={15} />
              </a>
              <a
                className="reading-link"
                href="https://www.yourhome.gov.au/passive-design/condensation"
                target="_blank"
                rel="noreferrer"
              >
                Your Home · condensation <ArrowUpRight size={15} />
              </a>
              <p className="minor">
                Use current instructions for the selected products. These
                references do not approve the project details.
              </p>
            </TabsContent>
          </Tabs>
          <p className="caution">
            For learning, not construction. Chris’s review is pending. The stage
            order is a teaching reveal, not a site programme.
          </p>
        </aside>
      </div>
    </main>
  );
}
