export type Anchor = { id: string; x: number; y: number; selected?: boolean };
export type Callout = Anchor & {
  left: number;
  top: number;
  width: number;
  circleX: number;
  circleY: number;
  side: 'left' | 'right';
};
// Keep fixed-height labels in two rails, leaving heading and camera controls clear.
export function layoutCallouts(
  anchors: Anchor[],
  width: number,
  height: number,
): Callout[] {
  const top = width < 520 ? 260 : 140,
    bottom = height - 190,
    step = 58;
  const capacity = Math.floor((bottom - top) / step);
  if (capacity < 1 || width < 260) return [];
  const labelWidth = Math.min(184, Math.max(108, width * 0.21));
  const chosen = anchors
    .filter(
      (a) =>
        Number.isFinite(a.x) &&
        Number.isFinite(a.y) &&
        a.x >= 0 &&
        a.x <= width &&
        a.y >= 0 &&
        a.y <= height,
    )
    .sort((a, b) => Number(!!b.selected) - Number(!!a.selected))
    .slice(0, capacity * 2)
    .sort((a, b) => a.x - b.x);
  const split = Math.ceil(chosen.length / 2);
  return chosen.flatMap((_, index) =>
    index === 0 || index === split
      ? (() => {
          const side = index === 0 ? 'left' : 'right';
          const column = chosen
            .slice(index, index === 0 ? split : chosen.length)
            .sort((a, b) => a.y - b.y);
          return column.flatMap((a, row): Callout[] => {
            const left =
              side === 'left'
                ? 14
                : width - (width < 520 ? 14 : 80) - labelWidth;
            const circleX =
              side === 'left' ? left + labelWidth - 22 : left + 22;
            const circleY = top + row * step + 24;
            // Never place the circle directly over its own attachment point.
            if (Math.hypot(circleX - a.x, circleY - a.y) < 56) return [];
            return [
              {
                ...a,
                left,
                top: circleY - 24,
                width: labelWidth,
                circleX,
                circleY,
                side,
              },
            ];
          });
        })()
      : [],
  );
}
