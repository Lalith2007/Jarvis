export function formatUptime(totalSeconds: number) {
  const days = Math.floor(totalSeconds / 86_400);
  const hours = Math.floor((totalSeconds % 86_400) / 3_600);
  const minutes = Math.floor((totalSeconds % 3_600) / 60);
  return `${days}d ${hours}h ${minutes}m`;
}

export function formatTime(iso: string) {
  return new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date(iso));
}

export function statusLabel(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export function formatBytes(value: number, fractionDigits = 1) {
  const units = ["B", "KB", "MB", "GB", "TB", "PB"];
  let size = value;
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(index === 0 ? 0 : fractionDigits)} ${units[index]}`;
}

export function formatBitsPerSecond(bytesPerSecond: number) {
  const units = ["bps", "Kbps", "Mbps", "Gbps"];
  let value = bytesPerSecond * 8;
  let index = 0;
  while (value >= 1000 && index < units.length - 1) {
    value /= 1000;
    index += 1;
  }
  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

export function formatMetricValue(value: number | null, unit: string) {
  if (value === null || Number.isNaN(value)) return "—";
  return `${Math.round(value)}${unit}`;
}
