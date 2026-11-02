'use client';
import {
  useEffect,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from 'react';
import { Play, Pause, RotateCcw } from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import type { ViewState } from '@/lib/explorer';

export function VerticalExplodeControls({
  state,
  setState,
}: {
  state: ViewState;
  setState: Dispatch<SetStateAction<ViewState>>;
}) {
  const [playing, setPlaying] = useState(false);
  const [reduced, setReduced] = useState(false);
  const latest = useRef(state);
  useEffect(() => { latest.current = state; }, [state]);
  useEffect(() => {
    const query = window.matchMedia('(prefers-reduced-motion: reduce)');
    const change = () => {
      setReduced(query.matches);
      if (query.matches) setPlaying(false);
    };
    change();
    query.addEventListener('change', change);
    const hide = () => {
      if (document.hidden) setPlaying(false);
    };
    document.addEventListener('visibilitychange', hide);
    return () => {
      query.removeEventListener('change', change);
      document.removeEventListener('visibilitychange', hide);
    };
  }, []);
  useEffect(() => {
    if (!playing) return;
    let frame = 0,
      previous = 0;
    const tick = (time: number) => {
      const s = latest.current;
      if (s.model !== 'building') {
        setPlaying(false);
        return;
      }
      const delta = previous ? Math.min(time - previous, 100) / 4500 : 0;
      previous = time;
      const explosion = Math.min(1, s.explosion + delta);
      setState((current) => ({
        ...current,
        explosion,
        cutaway: explosion > 0,
      }));
      if (explosion >= 1) setPlaying(false);
      else frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, setState]);
  const setExplosion = (explosion: number) =>
    setState((s) => ({
      ...s,
      explosion,
      stage: 3,
      cutaway: explosion > 0,
      selected: null,
    }));
  return (
    <section
      className="vertical-explode-controls"
      aria-label="Vertical exploded view"
    >
      <div className="explode-heading">
        <h2 id="vertical-explode-label">Vertical exploded view</h2>
        <output>{Math.round(state.explosion * 100)}% separated</output>
      </div>
      <Slider
        aria-labelledby="vertical-explode-label"
        min={0}
        max={100}
        step={1}
        value={[state.explosion * 100]}
        onValueChange={(v) => {
          setPlaying(false);
          setExplosion(Number(Array.isArray(v) ? v[0] : v) / 100);
        }}
      />
      <div className="slider-captions">
        <span>Assembled</span>
        <span>Lifted apart</span>
      </div>
      <div className="step-controls">
        <button
          disabled={reduced}
          onClick={() => {
            if (playing) setPlaying(false);
            else {
              setExplosion(state.explosion >= 1 ? 0 : state.explosion);
              setPlaying(true);
            }
          }}
        >
          {playing ? <Pause size={17} /> : <Play size={17} />}
          {playing ? 'Pause' : 'Play lift'}
        </button>
        <button
          onClick={() => {
            setPlaying(false);
            setExplosion(0);
          }}
        >
          <RotateCcw size={17} /> Reset spacing
        </button>
      </div>
      <p className="minor">
        Ground framing stays anchored while the floor, upper walls and roof
        systems lift vertically. Enclosure sheets cut away while separated so
        the structural relationships remain readable. Gaps are not installation
        dimensions.
      </p>
      {reduced && (
        <p className="minor">
          Automatic animation is off for reduced motion. You can still use the
          slider.
        </p>
      )}
    </section>
  );
}
