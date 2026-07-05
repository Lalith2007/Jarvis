import { ArrowLeft, ArrowRight, CalendarClock, ChevronRight, CirclePlus, FileCode2, Folder, Globe2, Home, LockKeyhole, MoreHorizontal, Play, Plus, RefreshCw, Save, Search, Settings2, ShieldCheck, Trash2 } from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";
import { Panel, StatusDot } from "../components/ui/Panel";

function PageHeading({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="page-heading"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{action}</div>;
}

const files = [
  ["backend", "Folder", "Modified today", "—"], ["frontend", "Folder", "Modified now", "—"], ["docs", "Folder", "Modified today", "—"],
  ["README.md", "Markdown", "Modified yesterday", "4.2 KB"], ["LICENSE", "Text", "Modified yesterday", "1.1 KB"],
];

export function FilesPage() {
  const [query, setQuery] = useState("");
  const visible = files.filter(([name]) => name.toLowerCase().includes(query.toLowerCase()));
  return <div className="feature-page"><PageHeading eyebrow="Local workspace" title="Files" description="A safe file surface designed around the backend filesystem tool registry." action={<button className="primary-button"><Plus size={16} />New file</button>} /><div className="file-toolbar"><div className="breadcrumbs"><button><Home size={14} /></button><ChevronRight size={13} /><button>Jarvis</button></div><label className="search-control"><Search size={15} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search files…" /></label></div><Panel title="Workspace root" icon={<Folder size={15} />} action={<span className="micro-copy">{visible.length} items</span>}><div className="file-table"><div className="file-head"><span>Name</span><span>Type</span><span>Modified</span><span>Size</span><span /></div>{visible.map(([name, type, modified, size]) => <button key={name}><span className="file-name">{type === "Folder" ? <Folder size={17} /> : <FileCode2 size={17} />}<b>{name}</b></span><span>{type}</span><span>{modified}</span><span>{size}</span><MoreHorizontal size={16} /></button>)}</div></Panel><div className="permission-note"><ShieldCheck size={15} /><span>Write operations will follow the backend PermissionManager before they are enabled.</span></div></div>;
}

export function BrowserPage() {
  const [address, setAddress] = useState("https://");
  const [submitted, setSubmitted] = useState("");
  const navigate = (event: FormEvent) => { event.preventDefault(); setSubmitted(address); };
  return <div className="feature-page browser-page"><PageHeading eyebrow="Automation surface" title="Browser" description="Mission-scoped browser sessions will appear here when the Playwright provider is exposed." /><div className="browser-chrome panel"><div className="browser-tabs"><button className="active"><Globe2 size={13} />New session</button><button aria-label="New tab"><Plus size={15} /></button></div><div className="browser-toolbar"><button aria-label="Back"><ArrowLeft size={16} /></button><button aria-label="Forward"><ArrowRight size={16} /></button><button aria-label="Reload"><RefreshCw size={15} /></button><form onSubmit={navigate}><LockKeyhole size={14} /><input value={address} onChange={(event) => setAddress(event.target.value)} aria-label="Browser address" /></form><button aria-label="Browser options"><MoreHorizontal size={16} /></button></div><div className="browser-viewport"><Globe2 size={46} /><h2>{submitted ? "Browser provider not connected" : "Start a mission browser session"}</h2><p>{submitted ? `${submitted} is queued for the future BrowserState provider.` : "A real tab, current URL, title, and session state will be rendered here—not a screenshot."}</p><button className="secondary-button" onClick={() => setAddress("https://example.com")}>Load example address</button></div><div className="browser-statusbar"><span><StatusDot status="offline" />Provider pending</span><span>BrowserState · session_id · current_url · tabs[]</span></div></div></div>;
}

const initialTerminal = [
  "JARVIS terminal interface initialized", "Connected to frontend command adapter", "Type 'help' to view safe local commands",
];

export function TerminalPage() {
  const [lines, setLines] = useState(initialTerminal);
  const [command, setCommand] = useState("");
  const run = (event: FormEvent) => {
    event.preventDefault(); const value = command.trim(); if (!value) return;
    let output = `Command '${value}' requires the backend shell provider.`;
    if (value === "help") output = "Available: help, clear, status, models, missions";
    if (value === "status") output = "Frontend: online · Backend shell: provider pending";
    if (value === "models") output = "Athena registry: 5 model profiles mapped";
    if (value === "missions") output = "Mission service contract: ready · REST route: pending";
    if (value === "clear") { setLines([]); setCommand(""); return; }
    setLines((current) => [...current, `jarvis@ai-os:~$ ${value}`, output]); setCommand("");
  };
  return <div className="feature-page terminal-page"><PageHeading eyebrow="Execution surface" title="Terminal" description="A streaming terminal prepared for a permission-aware backend shell transport." /><div className="terminal-window panel"><div className="terminal-window-bar"><span><i /><i /><i /></span><b>jarvis — zsh</b><button><Plus size={15} /></button></div><div className="terminal-output" role="log">{lines.map((line, index) => <div key={`${index}-${line}`} className={line.startsWith("jarvis@") ? "command" : ""}>{line}</div>)}<form onSubmit={run}><span>jarvis@ai-os:~$</span><input autoFocus value={command} onChange={(event) => setCommand(event.target.value)} aria-label="Terminal command" autoComplete="off" /></form></div></div></div>;
}

const defaultJobs = [
  { id: 1, name: "Backup knowledge vault", schedule: "Daily · 11:00", enabled: true, next: "Today, 11:00" },
  { id: 2, name: "Generate weekly report", schedule: "Monday · 09:00", enabled: true, next: "Monday, 09:00" },
  { id: 3, name: "Refresh model health", schedule: "Every 30 minutes", enabled: false, next: "Paused" },
  { id: 4, name: "Clean execution artifacts", schedule: "Friday · 21:00", enabled: true, next: "Friday, 21:00" },
];

export function AutomationPage() {
  const [jobs, setJobs] = useState(defaultJobs);
  const toggle = (id: number) => setJobs((items) => items.map((job) => job.id === id ? { ...job, enabled: !job.enabled, next: job.enabled ? "Paused" : "Next interval" } : job));
  return <div className="feature-page"><PageHeading eyebrow="Scheduled intelligence" title="Automation" description="Recurring missions and event-triggered workflows controlled from one timeline." action={<button className="primary-button"><CirclePlus size={16} />New automation</button>} /><div className="automation-stats"><article><CalendarClock size={19} /><span><strong>{jobs.length}</strong><small>Total automations</small></span></article><article><Play size={19} /><span><strong>{jobs.filter((job) => job.enabled).length}</strong><small>Active schedules</small></span></article><article><RefreshCw size={19} /><span><strong>0</strong><small>Runs today</small></span></article></div><Panel title="Automation registry" icon={<CalendarClock size={15} />}><div className="automation-list">{jobs.map((job) => <div key={job.id}><button className={`toggle ${job.enabled ? "on" : ""}`} aria-label={`${job.enabled ? "Disable" : "Enable"} ${job.name}`} onClick={() => toggle(job.id)}><i /></button><span><b>{job.name}</b><small>{job.schedule}</small></span><span className={job.enabled ? "success" : "muted"}>{job.next}</span><button className="icon-button" aria-label={`Delete ${job.name}`} onClick={() => setJobs((items) => items.filter((item) => item.id !== job.id))}><Trash2 size={15} /></button></div>)}</div></Panel></div>;
}

interface SettingsState { apiUrl: string; operator: string; reducedMotion: boolean; sound: boolean; compact: boolean }
import { FrontendConfig } from '../../electron/config.cjs';

const defaults: SettingsState = { apiUrl: FrontendConfig.API_BASE.replace(/\/api$/, ''), operator: "Lalith Praveen", reducedMotion: false, sound: true, compact: false };

export function SettingsPage() {
  const [settings, setSettings] = useState<SettingsState>(() => { try { return { ...defaults, ...JSON.parse(localStorage.getItem("jarvis-settings") ?? "{}") }; } catch { return defaults; } });
  const [saved, setSaved] = useState(false);
  useEffect(() => { if (!saved) return; const timer = window.setTimeout(() => setSaved(false), 2200); return () => clearTimeout(timer); }, [saved]);
  const save = (event: FormEvent) => { event.preventDefault(); localStorage.setItem("jarvis-settings", JSON.stringify(settings)); setSaved(true); };
  return <div className="feature-page"><PageHeading eyebrow="System configuration" title="Settings" description="Local preferences and provider endpoints for this JARVIS installation." /><form onSubmit={save} className="settings-layout"><Panel title="Connection" icon={<Globe2 size={15} />}><label className="field"><span>Backend API URL</span><input value={settings.apiUrl} onChange={(event) => setSettings({ ...settings, apiUrl: event.target.value })} /><small>Build-time deployments should set VITE_API_URL.</small></label><label className="field"><span>Operator name</span><input value={settings.operator} onChange={(event) => setSettings({ ...settings, operator: event.target.value })} /></label></Panel><Panel title="Interface" icon={<Settings2 size={15} />}><SettingToggle label="Reduce reactor motion" detail="Minimize rotation and parallax" value={settings.reducedMotion} onChange={(value) => setSettings({ ...settings, reducedMotion: value })} /><SettingToggle label="Voice feedback" detail="Enable audio when the voice provider is ready" value={settings.sound} onChange={(value) => setSettings({ ...settings, sound: value })} /><SettingToggle label="Compact density" detail="Use a tighter desktop information layout" value={settings.compact} onChange={(value) => setSettings({ ...settings, compact: value })} /></Panel><div className="settings-actions"><span className={saved ? "visible" : ""}>Settings saved locally</span><button className="primary-button" type="submit"><Save size={16} />Save settings</button></div></form></div>;
}

function SettingToggle({ label, detail, value, onChange }: { label: string; detail: string; value: boolean; onChange: (value: boolean) => void }) {
  return <div className="setting-row"><span><b>{label}</b><small>{detail}</small></span><button type="button" className={`toggle ${value ? "on" : ""}`} aria-pressed={value} onClick={() => onChange(!value)}><i /></button></div>;
}
