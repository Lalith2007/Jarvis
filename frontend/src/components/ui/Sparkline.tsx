import type { MetricPoint } from "../../types/jarvis";

export function Sparkline({ data, color = "var(--cyan)", height = 30 }: { data?: MetricPoint[]; color?: string; height?: number }) {
  if (!data || data.length < 2) return <div className="sparkline-empty" style={{ height }} />;
  const width = 140;
  const points = data.map((point, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - (point.value / 100) * height;
    return `${x},${y}`;
  }).join(" ");
  return (
    <svg className="sparkline" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id={`spark-${color.replace(/\W/g, "")}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={color} stopOpacity=".34" />
          <stop offset="1" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={`0,${height} ${points} ${width},${height}`} fill={`url(#spark-${color.replace(/\W/g, "")})`} />
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.8" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

