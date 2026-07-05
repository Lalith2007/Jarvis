import { Bell, Command, Menu, Search, Wifi, WifiOff } from "lucide-react";
import { useEffect, useState } from "react";
import { useDashboardSnapshot } from "../../hooks/useDashboard";
import { useJarvisStore } from "../../stores/use-jarvis-store";
import { formatMetricValue, formatUptime } from "../../utils/format";
import { Sparkline } from "../ui/Sparkline";

export function Topbar() {
  const [now, setNow] = useState(new Date());
  const { data } = useDashboardSnapshot();
  const setSidebarOpen = useJarvisStore((state) => state.setSidebarOpen);
  const setCommandPaletteOpen = useJarvisStore((state) => state.setCommandPaletteOpen);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  // Use camelCase mapped fields from DTO
  const uptimeSeconds = data?.system?.uptimeSeconds ?? 0;
  const metrics = data?.system?.metrics ?? [];

  return (
    <header className="topbar">
      <button className="icon-button menu-button" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={19} /></button>
      <div className="clock-block">
        <span className="clock">{now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</span>
        <small>{now.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" })}</small>
      </div>
      <div className="top-stat uptime"><small>System uptime</small><strong>{formatUptime(uptimeSeconds)}</strong></div>
      <div className="top-metrics">
        {metrics.slice(0, 4).map((metric) => (
          <div className="top-metric" key={metric.key}>
            <div><small>{metric.label}</small><strong>{formatMetricValue(metric.value, metric.unit)}</strong></div>
            <Sparkline data={(metric as any).history} height={18} />
          </div>
        ))}
      </div>
      <button className="command-trigger" onClick={() => setCommandPaletteOpen(true)}>
        <Search size={15} /><span>Command JARVIS</span><kbd><Command size={11} /> K</kbd>
      </button>
      <div
        className={`connection-badge ${data?.system ? "online" : "offline"}`}
        title={data?.system ? "Backend connected" : "Development provider active"}
      >
        {data?.system ? <Wifi size={15} /> : <WifiOff size={15} />}
      </div>
      <button className="icon-button notification-button" aria-label="Notifications"><Bell size={18} /><i>3</i></button>
    </header>
  );
}
