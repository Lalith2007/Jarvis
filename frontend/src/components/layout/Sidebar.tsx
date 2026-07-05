import {
  Bot, Boxes, BrainCircuit, CalendarClock, ChevronLeft, CircleGauge, Database,
  Files, FolderKanban, Globe2, HardDrive, MessageSquareText, Settings, TerminalSquare, Workflow,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { NavLink } from "react-router-dom";
import { useJarvisStore } from "../../stores/use-jarvis-store";

interface NavItem { to: string; label: string; icon: LucideIcon }

const primary: NavItem[] = [
  { to: "/dashboard", label: "Dashboard", icon: CircleGauge },
  { to: "/chat", label: "Chat", icon: MessageSquareText },
  { to: "/missions", label: "Missions", icon: Workflow },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/agents", label: "Agents", icon: Bot },
  { to: "/runtime", label: "Runtime", icon: HardDrive },
];

const systems: NavItem[] = [
  { to: "/memory", label: "Memory", icon: BrainCircuit },
  { to: "/knowledge", label: "Knowledge", icon: Database },
  { to: "/files", label: "Files", icon: Files },
  { to: "/browser", label: "Browser", icon: Globe2 },
  { to: "/terminal", label: "Terminal", icon: TerminalSquare },
  { to: "/models", label: "Models", icon: Boxes },
  { to: "/automation", label: "Automation", icon: CalendarClock },
  { to: "/settings", label: "Settings", icon: Settings },
];

function NavGroup({ label, items }: { label: string; items: NavItem[] }) {
  const setSidebarOpen = useJarvisStore((state) => state.setSidebarOpen);
  return (
    <div className="nav-group">
      <span className="nav-group-label">{label}</span>
      {items.map(({ to, label: itemLabel, icon: Icon }) => (
        <NavLink key={to} to={to} onClick={() => setSidebarOpen(false)} className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
          <Icon size={17} strokeWidth={1.7} />
          <span>{itemLabel}</span>
        </NavLink>
      ))}
    </div>
  );
}

export function Sidebar() {
  const open = useJarvisStore((state) => state.sidebarOpen);
  const setOpen = useJarvisStore((state) => state.setSidebarOpen);
  return (
    <>
      {open && <button className="sidebar-scrim" aria-label="Close navigation" onClick={() => setOpen(false)} />}
      <aside className={`sidebar${open ? " open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><span /><span /><span /></div>
          <div className="brand-copy"><strong>J.A.R.V.I.S.</strong><small>Autonomous AI Operating System</small></div>
          <button className="icon-button sidebar-close" aria-label="Close navigation" onClick={() => setOpen(false)}><ChevronLeft size={18} /></button>
        </div>
        <nav aria-label="Primary navigation">
          <NavGroup label="Command" items={primary} />
          <NavGroup label="Systems" items={systems} />
        </nav>
        <div className="operator-card">
          <div className="operator-orb"><span /></div>
          <div><small>Operator</small><strong>Lalith Praveen</strong><span><i /> System owner</span></div>
        </div>
      </aside>
    </>
  );
}

