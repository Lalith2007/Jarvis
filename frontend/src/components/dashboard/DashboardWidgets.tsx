import {
  Activity, Bot, Boxes, BrainCircuit, BriefcaseBusiness, CalendarClock,
  CircleSlash2, CloudCog, Code2, Container, Database, FileCode2, Files, FolderCog, Gauge,
  GitBranch, Globe2, HardDrive, Image, MemoryStick, Network, Radio, Search, ServerCog, TerminalSquare,
  Volume2, Workflow, Wrench,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useDashboardSnapshot } from "../../hooks/useDashboard";
import type { MappedSystemSnapshot } from "../../api/dto";
import { formatBitsPerSecond, formatBytes, formatMetricValue, formatTime, statusLabel } from "../../utils/format";
import { Panel, StatusDot } from "../ui/Panel";
import { Sparkline } from "../ui/Sparkline";
import { usePlatformEvents } from "../../hooks/usePlatformEvents";

const metricIcon: Record<string, LucideIcon> = {
  cpu: Activity, gpu: Gauge, memory: MemoryStick, storage: HardDrive, network: Network,
};
const capabilityIcon: Record<string, LucideIcon> = {
  code: Code2, terminal: TerminalSquare, browser: Globe2, files: Files, api: CloudCog,
  image: Image, documents: FileCode2, data: Database, voice: Volume2, vision: Activity,
  knowledge: Search, models: BrainCircuit,
};

function EmptyLoading() { return <div className="skeleton-stack"><i /><i /><i /></div>; }

export function ResourcePanel() {
  const { data } = useDashboardSnapshot();
  const metrics = data?.system?.metrics ?? [];
  return (
    <Panel title="System resources" icon={<ServerCog size={15} />}>
      {!data?.system ? <EmptyLoading /> : (
        <div className="resource-list">
          {metrics.map((metric) => {
            const Icon = metricIcon[metric.key] ?? ServerCog;
            const value = metric.value ?? 0;
            return (
              <div className={`resource-item${!metric.available ? " unavailable" : ""}`} key={metric.key}>
                <Icon size={15} />
                <div>
                  <span><b>{metric.label}</b><strong>{formatMetricValue(metric.value, metric.unit)}</strong></span>
                  <div className="meter"><i style={{ transform: `scaleX(${value / 100})` }} /></div>
                  <small>{metric.detail}</small>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Panel>
  );
}

export function CapabilitiesPanel() {
  const { data } = useDashboardSnapshot();
  const caps = data?.capabilities ?? [];
  return (
    <Panel title="Capabilities" icon={<Workflow size={15} />}>
      <div className="capability-grid">
        {caps.map((capability: any) => {
          const id = typeof capability === "string" ? capability : (capability.id ?? "unknown");
          const name = id.charAt(0).toUpperCase() + id.slice(1);
          const Icon = capabilityIcon[id] ?? Wrench;
          return (
            <button key={id} className="">
              <Icon size={18} /><span>{name}</span><small>Ready</small>
            </button>
          );
        })}
      </div>
    </Panel>
  );
}

export function ProjectPanel() {
  return (
    <Panel title="Current project" icon={<BriefcaseBusiness size={15} />} action={<button className="text-button">Open project</button>}>
      <div className="empty-state"><b>No active project</b><p>Projects subsystem pending.</p></div>
    </Panel>
  );
}

export function AgentsPanel() {
  const { data } = useDashboardSnapshot();
  const models = data?.models ?? [];
  return (
    <Panel title="Registered Models" icon={<Bot size={15} />} action={<span className="micro-copy">{models.length} available</span>}>
      <div className="agent-grid">
        {models.map((model) => (
          <button key={model.model} className="agent-row">
            <span className="agent-avatar"><Bot size={13} /></span>
            <span>
              <b>{model.model}</b>
              <small>{model.description}</small>
            </span>
            <span className="agent-state">
              <StatusDot status={model.healthy ? "online" : "offline"} />
              <small>{model.healthy ? "Ready" : "Offline"}</small>
            </span>
          </button>
        ))}
      </div>
    </Panel>
  );
}

export function MissionQueuePanel() {
  const { data } = useDashboardSnapshot();
  const missions = data?.missions ?? [];
  return (
    <Panel title="Mission queue" icon={<Workflow size={15} />} action={<a className="text-button" href="/missions">View all</a>}>
      <div className="task-table">
        {missions.map((mission, index) => (
          <div className="task-row" key={mission.id}>
            <span className="queue-index">{index + 1}</span>
            <span className={`task-status ${mission.status}`}>{statusLabel(mission.status)}</span>
            <span className="task-name">{mission.goal}</span>
            <span className="task-time">{(mission.executionIds?.length ?? 0) > 0 ? "Executing" : "Waiting"}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

export function ServicesPanel() {
  const { data } = useDashboardSnapshot();
  const servers = data?.mcpServers ?? [];
  const icons = [GitBranch, Container, CloudCog, BrainCircuit, Database, ServerCog];
  return (
    <Panel title="Connected MCP Servers" icon={<CloudCog size={15} />} action={<button className="text-button">Manage</button>}>
      <div className="service-grid">
        {servers.map((server, index) => {
          const Icon = icons[index % icons.length];
          return (
            <button key={server.id}>
              <Icon size={16} />
              <span><b>{server.name}</b><small>{server.url ?? "—"}</small></span>
              <span className="service-status connected"><StatusDot status={"online"} />Connected</span>
            </button>
          );
        })}
      </div>
    </Panel>
  );
}

// Subsystem → CSS class for color coding in the event stream
const SUBSYSTEM_CLASS: Record<string, string> = {
  hermes: "info",
  mission: "warning",
  memory: "muted",
  athena: "success",
  planner: "info",
  executor: "success",
  runtime: "warning",
};

// Human-readable labels for common event types
const EVENT_LABEL: Record<string, string> = {
  HermesReceivedRequest: "Request received",
  MissionCreated: "Mission created",
  MissionStarted: "Mission started",
  MissionCompleted: "Mission completed",
  MissionFailed: "Mission failed",
  MemoryRetrievalStarted: "Memory retrieval started",
  MemoryRetrievalCompleted: "Memory retrieved",
  AthenaStarted: "Routing started",
  AthenaDecision: "Model selected",
  AthenaCompleted: "Routing complete",
  PlannerStarted: "Planning started",
  PlanningStarted: "Planning started",
  PlannerCompleted: "Plan ready",
  PlanningCompleted: "Plan ready",
  ExecutionStarted: "Execution started",
  ExecutorStarted: "Executor started",
  ExecutionCompleted: "Execution complete",
  ExecutorCompleted: "Executor complete",
  ProviderStarted: "Provider started",
  ProviderCompleted: "Provider done",
};

export function TerminalPanel() {
  const { events } = usePlatformEvents();
  const recentEvents = events.slice(-12);
  return (
    <Panel
      title="Platform Event Stream"
      icon={<TerminalSquare size={15} />}
      action={
        <span className="micro-copy">{events.length} events</span>
      }
    >
      <div className="terminal-log" role="log">
        {recentEvents.map((log) => (
          <div key={log.id}>
            <time>{formatTime(log.timestamp)}</time>
            <b className={SUBSYSTEM_CLASS[log.subsystem] ?? "muted"}>
              {log.subsystem}
            </b>
            <span>›</span>
            <p>
              {EVENT_LABEL[log.event_type] ?? log.event_type}
              {log.duration_ms ? <span className="muted"> ({log.duration_ms} ms)</span> : null}
            </p>
          </div>
        ))}
        <div>
          <time>{new Date().toLocaleTimeString([], { hour12: false })}</time>
          <b className="success">jarvis</b>
          <span>›</span>
          <i className="terminal-cursor" />
        </div>
      </div>
    </Panel>
  );
}

export function LiveMetricsPanel() {
  const { data } = useDashboardSnapshot();
  const metrics = data?.system?.metrics ?? [];
  return (
    <Panel
      title="Live metrics"
      icon={<Activity size={15} />}
      action={<span className="live-label"><i /> {data?.system ? "System" : "Waiting"}</span>}
    >
      <div className="live-metrics">
        {metrics.map((metric) => (
          <div key={metric.key}>
            <span>{metric.label}</span>
            <strong>{formatMetricValue(metric.value, metric.unit)}</strong>
            <Sparkline data={(metric as any).history} height={24} color={metric.key === "storage" ? "var(--green)" : "var(--cyan)"} />
          </div>
        ))}
      </div>
    </Panel>
  );
}

export function BottomPanels() {
  const { data } = useDashboardSnapshot();
  const system: MappedSystemSnapshot | undefined = data?.system;
  const gpu = system?.gpu;

  const gpuRows: [string, string][] = [
    ["Adapter", gpu?.name ?? "Backend required"],
    ["Renderer", gpu?.rendererPercent != null ? `${Math.round(gpu.rendererPercent)}%` : "—"],
    ["Tiler", gpu?.tilerPercent != null ? `${Math.round(gpu.tilerPercent)}%` : "—"],
    ["Memory", gpu?.memoryUsedBytes ? formatBytes(gpu.memoryUsedBytes) : "—"],
  ];

  const topProcessRows: [string, string][] = system
    ? (system.topProcesses ?? []).slice(0, 4).map((p) => [p.name, `${p.cpuPercent.toFixed(1)}%`])
    : [["Backend offline", "—"]];

  const dockerRows: [string, string][] = system
    ? (system.dockerContainers ?? []).length > 0
      ? (system.dockerContainers ?? []).slice(0, 4).map((c) => [c.name, c.status])
      : [["No running containers", "—"]]
    : [["Backend offline", "—"]];

  const diskRows: [string, string][] = system
    ? (system.disks ?? []).slice(0, 4).map((d) => [d.path, `${formatBytes(d.usedBytes)} / ${formatBytes(d.totalBytes)}`])
    : [["Backend offline", "—"]];

  const networkRows: [string, string][] = system
    ? [
        ["Download", formatBitsPerSecond(system.network.downloadBps)],
        ["Upload", formatBitsPerSecond(system.network.uploadBps)],
        ["Received", formatBytes(system.network.bytesRecv)],
        ["Sent", formatBytes(system.network.bytesSent)],
      ]
    : [["Backend offline", "—"]];

  const bottomData = [
    { title: "Running processes", icon: Radio, value: String(system?.topProcesses?.length ?? 0), rows: topProcessRows },
    { title: "Docker containers", icon: Boxes, value: String(system?.dockerContainers?.length ?? 0), rows: dockerRows },
    { title: "GPU monitor", icon: Gauge, value: gpu?.utilizationPercent != null ? `${Math.round(gpu.utilizationPercent)}%` : "—", rows: gpuRows },
    { title: "Filesystem", icon: FolderCog, value: String(system?.disks?.length ?? 0), rows: diskRows },
    { title: "Network I/O", icon: Network, value: data?.system ? "Live" : "—", rows: networkRows },
    { title: "Upcoming automation", icon: CalendarClock, value: "4", rows: [["Backup database", "11:00"], ["Weekly report", "13:00"], ["Data sync", "16:00"], ["System cleanup", "21:00"]] as [string, string][] },
  ];

  return (
    <>
      {bottomData.map(({ title, icon: Icon, value, rows }) => (
        <Panel key={title} title={title} icon={<Icon size={14} />} action={<span className="micro-copy">{value}</span>} className="mini-panel">
          <div className="mini-list">
            {rows.map(([label, itemValue]) => (
              <div key={label}><span>{label}</span><b>{itemValue}</b></div>
            ))}
          </div>
        </Panel>
      ))}
    </>
  );
}

export function BackendNotice() {
  const { data } = useDashboardSnapshot();
  if (!data?.system) {
    return (
      <div className="backend-notice">
        <CircleSlash2 size={14} />
        <span>Backend is offline. Start FastAPI to unlock live CPU, Apple GPU, RAM, disk, process, Docker, and network telemetry.</span>
      </div>
    );
  }
  return null;
}
