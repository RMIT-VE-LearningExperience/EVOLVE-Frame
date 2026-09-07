'use client';
import type { Dispatch, SetStateAction } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from '@/components/ui/accordion';
import { eligibleLayer, groupLayers, toggleLayers } from '@/lib/layer-groups';
import { visiblePart, type Part, type ViewState } from '@/lib/explorer';

export function LayerPanel({
  parts,
  state,
  setState,
}: {
  parts: Part[];
  state: ViewState;
  setState: Dispatch<SetStateAction<ViewState>>;
}) {
  return (
    <Accordion key={state.model} multiple className="layer-groups">
      {groupLayers(parts, state.model === 'building').map((group) => {
        const eligible = group.parts.filter((p) => eligibleLayer(p, state));
        const shown = eligible.filter((p) => visiblePart(p, state)).length;
        const allShown = eligible.length > 0 && shown === eligible.length;
        const action = allShown ? 'Hide' : 'Show';
        return (
          <AccordionItem key={group.label} value={group.label}>
            <div className="layer-group-heading">
              <AccordionTrigger>
                <span>
                  {group.label}
                  <small>
                    {shown}/{group.parts.length} visible
                  </small>
                </span>
              </AccordionTrigger>
              <button
                className="group-eye"
                disabled={!eligible.length}
                aria-label={`${action} all available layers in ${group.label}`}
                title={`${action} group`}
                onClick={() => setState((s) => toggleLayers(s, group.parts))}
              >
                {shown ? <Eye size={18} /> : <EyeOff size={18} />}
              </button>
            </div>
            <AccordionContent>
              <div className="layer-list">
                {group.parts.map((p) => {
                  const available = eligibleLayer(p, state);
                  const shown = visiblePart(p, state);
                  return (
                    <div
                      className={`layer-row ${state.selected === p.key ? 'is-selected' : ''}`}
                      key={p.key}
                    >
                      <button
                        disabled={!available}
                        aria-pressed={state.selected === p.key}
                        onClick={() =>
                          setState((s) => ({
                            ...s,
                            selected: s.selected === p.key ? null : p.key,
                            hidden: s.hidden.filter((k) => k !== p.key),
                          }))
                        }
                      >
                        <span>{p.label}</span>
                        {!available && (
                          <small>
                            {p.stage > state.stage
                              ? `Stage ${p.stage + 1}`
                              : 'Cutaway'}
                          </small>
                        )}
                      </button>
                      <button
                        disabled={!available}
                        aria-label={`${shown ? 'Hide' : 'Show'} ${p.label}`}
                        aria-pressed={shown}
                        onClick={() => setState((s) => toggleLayers(s, [p]))}
                      >
                        {shown ? <Eye size={17} /> : <EyeOff size={17} />}
                      </button>
                    </div>
                  );
                })}
              </div>
            </AccordionContent>
          </AccordionItem>
        );
      })}
    </Accordion>
  );
}
