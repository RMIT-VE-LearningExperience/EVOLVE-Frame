'use client';
import { useEffect, useState } from 'react';
import { flushSync } from 'react-dom';
import Link from 'next/link';
import {
  Box,
  ArrowRight,
  ArrowLeft,
  Layers3,
  MousePointer2,
  Eye,
  EyeOff,
  CheckCircle2,
  ArrowUpRight,
} from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import ModelViewer from '@/components/model-viewer';
import manifest from '@/public/models/manifest.json';
import {
  initialState,
  lessons,
  stageLessons,
  stageNames,
  modelKeys,
  validateNavigation,
  type ModelKey,
  type Part,
} from '@/lib/explorer';

export default function Home() {
  const [state, setState] = useState(initialState);
  const [panel, setPanel] = useState('learn');
  const lesson = lessons[state.model],
    isBuilding = state.model === 'building';
  const parts = manifest.models[state.model].parts as Part[];
  const selected = parts.find((p) => p.key === state.selected);
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
                stage: { type: 'integer', minimum: 0, maximum: 3 },
                cutaway: { type: 'boolean' },
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
        <Link href="/" className="brand">
          <Box size={28} /> FRAME LAB <span>LEICHHARDT</span>
        </Link>
        <span className="review">
          <span /> Teaching model · review pending
        </span>
      </header>
      <nav className="study-nav" aria-label="Construction studies">
        {modelKeys.map((m, i) => (
          <button
            key={m}
            aria-current={state.model === m ? 'page' : undefined}
            onClick={() => navigate(m)}
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
            key={state.model}
            state={state}
            onSelect={(key) => setState((s) => ({ ...s, selected: key }))}
            fallback={
              isBuilding
                ? '/enclosure_cutaway.png'
                : `/studies/${state.model}.png`
            }
          />
          <div className="view-caption">
            <MousePointer2 size={16} />
            <span>Drag to orbit · scroll or pinch to zoom · tap a part</span>
          </div>
          <div className="view-stamp">
            {isBuilding
              ? `STAGE 0${state.stage + 1} / ${stageNames[state.stage].toUpperCase()}`
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
                      <Layers3 size={18} /> Reveal cutaway
                    </span>
                    <Switch
                      checked={state.cutaway}
                      onCheckedChange={(v) =>
                        setState((s) => ({ ...s, cutaway: v }))
                      }
                      aria-label="Reveal enclosure cutaway"
                    />
                  </div>
                  <p className="minor">
                    Removes selected enclosure faces; timber stays visible.
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
                      disabled={state.stage === 3}
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
              <h2>Uncover the relationship.</h2>
              <p className="minor">
                Choose a name to highlight it. Use the eye to hide or restore
                that layer.
              </p>
              <div className="layer-list">
                {parts.map((p) => {
                  const available = !isBuilding || p.stage <= state.stage;
                  return (
                    <div
                      className={`layer-row ${state.selected === p.key ? 'is-selected' : ''}`}
                      key={p.key}
                    >
                      <button
                        disabled={!available}
                        onClick={() =>
                          setState((s) => ({
                            ...s,
                            selected: s.selected === p.key ? null : p.key,
                            hidden: s.hidden.filter((k) => k !== p.key),
                          }))
                        }
                      >
                        <span>{p.label}</span>
                        {!available && <small>Stage {p.stage + 1}</small>}
                      </button>
                      <button
                        disabled={!available}
                        aria-label={`${state.hidden.includes(p.key) ? 'Show' : 'Hide'} ${p.label}`}
                        aria-pressed={!state.hidden.includes(p.key)}
                        onClick={() =>
                          setState((s) => ({
                            ...s,
                            hidden: s.hidden.includes(p.key)
                              ? s.hidden.filter((k) => k !== p.key)
                              : [...s.hidden, p.key],
                          }))
                        }
                      >
                        {state.hidden.includes(p.key) ? (
                          <EyeOff size={17} />
                        ) : (
                          <Eye size={17} />
                        )}
                      </button>
                    </div>
                  );
                })}
              </div>
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
