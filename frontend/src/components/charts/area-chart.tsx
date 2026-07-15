"use client";

import * as React from "react";

import type { GrowthPoint } from "@/lib/analytics-api";

const W = 640;
const H = 180;
const PAD = { top: 16, right: 12, bottom: 24, left: 28 };

/**
 * Single-series area chart for change-over-time (prompt growth).
 * Single hue (primary) → no legend needed; title names the series.
 * Ships a hover crosshair + tooltip per the interaction spec.
 */
export function AreaChart({ data }: { data: GrowthPoint[] }) {
  const [hover, setHover] = React.useState<number | null>(null);
  const svgRef = React.useRef<SVGSVGElement>(null);

  if (data.length === 0) return null;

  const max = Math.max(1, ...data.map((d) => d.count));
  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;

  const x = (i: number) => PAD.left + (innerW * i) / Math.max(1, data.length - 1);
  const y = (v: number) => PAD.top + innerH - (innerH * v) / max;

  const linePath = data.map((d, i) => `${i === 0 ? "M" : "L"}${x(i)},${y(d.count)}`).join(" ");
  const areaPath =
    `M${x(0)},${y(0)} ` +
    data.map((d, i) => `L${x(i)},${y(d.count)}`).join(" ") +
    ` L${x(data.length - 1)},${y(0)} Z`;

  const onMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const rect = svgRef.current!.getBoundingClientRect();
    const rel = ((e.clientX - rect.left) / rect.width) * W;
    const i = Math.round(((rel - PAD.left) / innerW) * (data.length - 1));
    setHover(Math.min(data.length - 1, Math.max(0, i)));
  };

  const ticks = [0, Math.round(max / 2), max];

  return (
    <div className="relative">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        role="img"
        aria-label="Prompt growth over time"
        onMouseMove={onMove}
        onMouseLeave={() => setHover(null)}
      >
        {/* Recessive y gridlines + labels */}
        {ticks.map((t) => (
          <g key={t}>
            <line
              x1={PAD.left}
              x2={W - PAD.right}
              y1={y(t)}
              y2={y(t)}
              stroke="var(--color-border)"
              strokeWidth={1}
            />
            <text
              x={PAD.left - 6}
              y={y(t) + 3}
              textAnchor="end"
              fontSize={9}
              fill="var(--color-muted-foreground)"
            >
              {t}
            </text>
          </g>
        ))}

        <path d={areaPath} fill="var(--color-primary)" opacity={0.12} />
        <path
          d={linePath}
          fill="none"
          stroke="var(--color-primary)"
          strokeWidth={2}
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {hover != null && (
          <g>
            <line
              x1={x(hover)}
              x2={x(hover)}
              y1={PAD.top}
              y2={PAD.top + innerH}
              stroke="var(--color-muted-foreground)"
              strokeWidth={1}
              strokeDasharray="3 3"
            />
            <circle
              cx={x(hover)}
              cy={y(data[hover]!.count)}
              r={4}
              fill="var(--color-primary)"
              stroke="var(--color-background)"
              strokeWidth={2}
            />
          </g>
        )}
      </svg>

      {hover != null && (
        <div
          className="pointer-events-none absolute -translate-x-1/2 rounded-md border border-border bg-popover px-2 py-1 text-xs shadow"
          style={{ left: `${(x(hover) / W) * 100}%`, top: 0 }}
        >
          <span className="font-medium">{data[hover]!.count}</span>{" "}
          <span className="text-muted-foreground">on {data[hover]!.date.slice(5)}</span>
        </div>
      )}
    </div>
  );
}
