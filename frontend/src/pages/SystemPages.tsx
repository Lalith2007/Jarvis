import { BrainCircuit, CheckCircle2, ChevronRight, Cpu, Database, Gauge, HardDrive, Layers3, MemoryStick, Network, Search, ServerCog, ShieldCheck, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";
import { Panel, StatusDot } from "../components/ui/Panel";
import { Sparkline } from "../components/ui/Sparkline";
import { useDashboardSnapshot } from "../hooks/useDashboard";
import { formatMetricValue } from "../utils/format";

function PageHeading({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <div className="page-heading"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div></div>;
}

export function RuntimePage() {
  const { data } = useDashboardSnapshot();
  const caps = data?.capabilities ?? [];
  const services = data?.mcpServers ?? [];          // camelCase mapped field
  const metrics = data?.system?.metrics ?? [];
  const [tab, setTab] = useState("overview");
  const tabs = ["overview", "capabilities", "services"];
  const icons = [Cpu, Gauge, MemoryStick, HardDrive, Network];
  return (
    <div className="feature-page">
      <PageHeading eyebrow="Developer mode" title="Runtime" description="One operational view across hardware, providers, registries, and execution services." />
      <div className="tab-list">{tabs.map((item) => <button className={tab === item ? "active" : ""} onClick={() => setTab(item)} key={item}>{item}</button>)}</div>

      {tab === "overview" && <>
        <div className="metric-card-grid">
          {metrics.map((metric, index) => {
            const Icon = icons[index % icons.length];
            return (
              <article className="metric-card" key={metric.key}>
                <span><Icon size={18} />{metric.label}</span>
                <strong>{formatMetricValue(metric.value, metric.unit)}</strong>
                <small>{metric.detail}</small>
                <Sparkline data={(metric as any).history} height={40} />
              </article>
            );
          })}
        </div>
        <div className="runtime-grid">
          <Panel title="Core services" icon={<ServerCog size={15} />}>
            <div className="health-list">
              <div><span><StatusDot status={data?.system ? "online" : "offline"} /><b>FastAPI application</b></span><small>{data?.system ? "Reachable" : "Offline"}</small></div>
              <div><span><StatusDot status="online" /><b>Frontend runtime</b></span><small>Healthy</small></div>
              <div><span><StatusDot status="idle" /><b>Mission event bus</b></span><small>Backend-only</small></div>
              <div><span><StatusDot status="idle" /><b>Execution manager</b></span><small>Backend-only</small></div>
            </div>
          </Panel>
          <Panel title="Architecture contracts" icon={<Layers3 size={15} />}>
            <div className="contract-grid">
              {["Mission", "ExecutionContext", "PromptContext", "RouteDecision", "ToolCall", "SearchResult"].map((item) => (
                <span key={item}><CheckCircle2 size={14} />{item}</span>
              ))}
            </div>
          </Panel>
        </div>
      </>}

      {tab === "capabilities" && (
        <div className="capability-page-grid">
          {caps.map((capability: any) => {
            const id = typeof capability === "string" ? capability : (capability.id ?? "unknown");
            return (
              <article key={id}>
                <span><Sparkles size={17} /><StatusDot status={"online"} /></span>
                <h2>{id}</h2>
                <p>Execution category</p>
                <small>Registry contract available</small>
              </article>
            );
          })}
        </div>
      )}

      {tab === "services" && (
        <div className="service-page-grid">
          {services.map((service) => (
            <article key={service.id}>
              <div><Database size={18} /><span><b>{service.name}</b><small>MCP Server</small></span></div>
              <span className="badge connected">connected</span>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

const memoryNotes = [
  { path: "jarvis/architecture/hermes.md", title: "Hermes Orchestrator", excerpt: "Coordinates context, tools, memory, and final model responses." },
  { path: "jarvis/architecture/athena.md", title: "Athena Model Router", excerpt: "Selects models using intent, capability scores, latency, and health." },
  { path: "jarvis/product/reactor.md", title: "Reactor State Language", excerpt: "A living visualization of the operating system's current cognitive state." },
  { path: "jarvis/conversations/alpha.md", title: "JARVIS", excerpt: "Product shell, live capability surfaces, and vertical sprint strategy." },
];

export function MemoryPage() {
  const [query, setQuery] = useState(""); const [selected, setSelected] = useState(memoryNotes[0]);
  const results = useMemo(() => memoryNotes.filter((note) => `${note.title} ${note.excerpt}`.toLowerCase().includes(query.toLowerCase())), [query]);
  const choose = (note: typeof memoryNotes[number]) => { setSelected(note); };
  return (
    <div className="feature-page">
      <PageHeading eyebrow="Recall systems" title="Memory" description="Conversation context and durable knowledge exposed through the backend MemoryService." />
      <div className="memory-search"><Search size={18} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search the JARVIS vault…" /><kbd>⌘ /</kbd></div>
      <div className="memory-layout">
        <Panel title="Vault index" icon={<Database size={15} />} action={<span className="micro-copy">Development index · {results.length} notes</span>}>
          {results.map((note) => (
            <button key={note.path} className={`note-result${selected.path === note.path ? " active" : ""}`} onClick={() => choose(note)}>
              <BrainCircuit size={17} />
              <span><b>{note.title}</b><p>{note.excerpt}</p><small>{note.path}</small></span>
              <ChevronRight size={15} />
            </button>
          ))}
        </Panel>
        <Panel title={selected.title} eyebrow={selected.path} icon={<ShieldCheck size={15} />}>
          <article className="note-preview">
            <h2>{selected.title}</h2><p>{selected.excerpt}</p><hr />
            <p>This preview is served through a frontend provider matching the backend <code>VaultNote</code> and <code>SearchResult</code> contracts. Once vault routes are exposed, this surface can switch to live notes without structural changes.</p>
            <div className="note-tags"><span>Knowledge</span><span>Indexed</span><span>Local-first</span></div>
          </article>
        </Panel>
      </div>
    </div>
  );
}

export function KnowledgePage() {
  const nodes = ["JARVIS", "Hermes", "Athena", "Memory", "Tools", "Planner", "Executor", "Models", "Vault"];
  return (
    <div className="feature-page">
      <PageHeading eyebrow="Semantic map" title="Knowledge" description="Explore how JARVIS concepts, memories, and execution systems relate." />
      <Panel title="Knowledge graph" icon={<BrainCircuit size={15} />} action={<span className="live-label"><i /> Vault index</span>}>
        <div className="knowledge-graph">
          {nodes.map((node, index) => (
            <button key={node} className={node === "JARVIS" ? "root" : ""} style={{ "--angle": `${index * 45}deg`, "--radius": node === "JARVIS" ? "0px" : `${150 + (index % 2) * 70}px` } as React.CSSProperties}>
              <span>{node}</span>
            </button>
          ))}
          <svg viewBox="0 0 600 440" aria-hidden="true">
            {nodes.slice(1).map((_, index) => {
              const angle = (index * 45) * Math.PI / 180;
              const radius = 150 + ((index + 1) % 2) * 70;
              return <line key={index} x1="300" y1="220" x2={300 + Math.cos(angle) * radius} y2={220 + Math.sin(angle) * radius} />;
            })}
          </svg>
        </div>
      </Panel>
    </div>
  );
}

export function ModelsPage() {
  const { data } = useDashboardSnapshot();
  const models = data?.models ?? [];
  return (
    <div className="feature-page">
      <PageHeading eyebrow="Athena router" title="Models" description="The backend model registry, capability profiles, and routing health in one place." />
      <div className="model-grid">
        {models.map((model) => (
          <button key={model.model} className="model-card">
            <div className="model-card-head">
              <span className="model-orb"><BrainCircuit size={20} /></span>
              <StatusDot status={model.healthy ? "online" : "offline"} />
            </div>
            <span className="eyebrow">{model.model.split("/")[0]}</span>
            <h2>{model.model.split("/")[1] ?? model.model}</h2>
            <p>{model.description}</p>
            <div className="model-strengths">
              {(model.strengths ?? []).slice(0, 3).map((s) => <span key={s}>{s}</span>)}
            </div>
            <dl>
              <div><dt>Context</dt><dd>{model.maxContext?.toLocaleString() ?? "—"}</dd></div>
              <div><dt>Enabled</dt><dd>{model.enabled ? "Yes" : "No"}</dd></div>
              <div><dt>Health</dt><dd>{model.healthy ? "Healthy" : "Offline"}</dd></div>
            </dl>
          </button>
        ))}
      </div>
    </div>
  );
}
