import { Bot, CheckCircle2, Circle, Clock3, Filter, FolderKanban, Plus, Search, ShieldCheck, Workflow, XCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ChatPanel } from "../components/dashboard/ChatPanel";
import { ReactorCore } from "../components/reactor/ReactorCore";
import { Panel, StatusDot } from "../components/ui/Panel";
import { useDashboardSnapshot } from "../hooks/useDashboard";
import { usePlatformEvents } from "../hooks/usePlatformEvents";
import { useMissionEvents } from "../hooks/useMissionEvents";
import type { MappedModelInfo, MappedMission } from "../api/dto";
import { statusLabel } from "../utils/format";

function PageHeading({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="page-heading"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{action}</div>;
}

export function ChatPage() {
  return (
    <div className="feature-page">
      <PageHeading eyebrow="Hermes interface" title="Conversation" description="Every request enters the same mission-aware intelligence pipeline." />
      <div className="chat-page-layout">
        <ChatPanel full />
        <aside className="chat-reactor">
          <ReactorCore compact />
          <div className="pipeline-stack">
            <span className="done"><CheckCircle2 size={14} />Request accepted</span>
            <span className="active"><Circle size={14} />Athena routing</span>
            <span><Circle size={14} />Context assembly</span>
            <span><Circle size={14} />Response</span>
          </div>
        </aside>
      </div>
    </div>
  );
}

export function MissionsPage() {
  const { data } = useDashboardSnapshot();
  const queryClient = useQueryClient();
  const { events } = usePlatformEvents();
  const allMissions: MappedMission[] = data?.missions ?? [];
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filter, setFilter] = useState("all");

  // Auto-refresh mission list when MissionCreated or MissionCompleted arrives
  useEffect(() => {
    const last = events[events.length - 1];
    if (!last) return;
    if (
      last.subsystem === "mission" &&
      (last.event_type === "MissionCreated" || last.event_type === "MissionCompleted" || last.event_type === "MissionFailed")
    ) {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    }
  }, [events, queryClient]);

  const { latestStatus } = useMissionEvents(selectedId);

  const missions = allMissions.filter((m) => filter === "all" || m.status === filter);
  const selected = allMissions.find((m) => m.id === selectedId) ?? missions[0];
  const stages = ["created", "analyzing", "planning", "executing", "reflecting", "completed"];

  // Use live event status if available, fall back to stored status
  const liveStatus = latestStatus ?? selected?.status ?? "created";
  const selectedStage = Math.max(0, stages.indexOf(liveStatus));

  return (
    <div className="feature-page">
      <PageHeading eyebrow="Mission control" title="Missions" description="Inspect goals as they move through analysis, planning, execution, and reflection." action={<button className="primary-button"><Plus size={16} />New mission</button>} />
      <div className="split-page">
        <Panel title="Mission registry" icon={<Workflow size={15} />} action={
          <div className="compact-filter">
            <Filter size={13} />
            <select value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filter missions">
              <option value="all">All states</option>
              <option value="executing">Executing</option>
              <option value="waiting">Waiting</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        }>
          {missions.length === 0 && (
            <div className="empty-state"><Workflow size={24} /><b>No missions yet</b><p>Send a chat message to create your first mission.</p></div>
          )}
          {missions.map((mission) => (
            <button key={mission.id} className={`mission-list-item${selected?.id === mission.id ? " active" : ""}`} onClick={() => setSelectedId(mission.id)}>
              <span className={`mission-glyph ${mission.status}`}><Workflow size={16} /></span>
              <span><b>{mission.goal}</b><small>{mission.priority} priority · {mission.status}</small></span>
            </button>
          ))}
        </Panel>
        <Panel title="Mission telemetry" eyebrow={selected?.id} icon={<ShieldCheck size={15} />} action={liveStatus !== selected?.status ? <span className="live-label"><i /> live</span> : undefined}>
          {selected && (
            <div className="mission-detail">
              <h2>{selected.goal}</h2>
              <div className="timeline">
                {stages.map((stage, index) => (
                  <div key={stage} className={index < selectedStage ? "done" : index === selectedStage ? "active" : ""}>
                    {index < selectedStage ? <CheckCircle2 size={17} /> : index === selectedStage ? <Clock3 size={17} /> : <Circle size={17} />}
                    <span><b>{statusLabel(stage)}</b><small>{index < selectedStage ? "Complete" : index === selectedStage ? "In progress" : "Pending"}</small></span>
                  </div>
                ))}
              </div>
              <dl className="detail-grid">
                <div><dt>Status</dt><dd>{liveStatus}</dd></div>
                <div><dt>Priority</dt><dd>{statusLabel(selected.priority)}</dd></div>
                <div><dt>Mission ID</dt><dd className="mono">{selected.id.slice(0, 12)}…</dd></div>
              </dl>
            </div>
          )}
        </Panel>
      </div>
    </div>
  );
}



export function ProjectsPage() {
  const tasks = [
    ["Map backend domain contracts", true], ["Build application shell", true], ["Engineer reactor state machine", true], ["Connect live chat route", true],
    ["Expose mission REST endpoints", true], ["Add WebSocket event transport", true], ["Connect native system telemetry", false],
  ] as const;
  return (
    <div className="feature-page">
      <PageHeading eyebrow="Workspaces" title="Projects" description="Goals, files, missions, and artifacts gathered into durable workspaces." action={<button className="primary-button"><Plus size={16} />New project</button>} />
      <div className="project-hero panel">
        <div className="project-icon"><FolderKanban size={28} /></div>
        <div><span className="version-chip">v1.0.0-alpha</span><h2>AI Operating System</h2><p>Building an autonomous, local-first AI operating environment.</p></div>
        <div className="project-ring" style={{ "--progress": "78%" } as React.CSSProperties}><strong>78%</strong><small>Complete</small></div>
      </div>
      <div className="three-column-page">
        <Panel title="Milestone tasks" icon={<CheckCircle2 size={15} />}>
          {tasks.map(([task, complete]) => (
            <div className="check-row" key={task}>
              {complete ? <CheckCircle2 className="success" size={16} /> : <Circle size={16} />}
              <span>{task}</span><small>{complete ? "Complete" : "Planned"}</small>
            </div>
          ))}
        </Panel>
        <Panel title="Recent artifacts" icon={<FolderKanban size={15} />}>
          <div className="empty-state"><FolderKanban size={28} /><b>No mission artifacts yet</b><p>Generated files and documents will appear here through ExecutionContext.artifacts.</p></div>
        </Panel>
        <Panel title="Project activity" icon={<Clock3 size={15} />}>
          <div className="activity-feed">
            <div><i /><span><b>Frontend shell initialized</b><small>Just now</small></span></div>
            <div><i /><span><b>Mission contracts mapped</b><small>12 minutes ago</small></span></div>
            <div><i /><span><b>Athena registry verified</b><small>1 hour ago</small></span></div>
          </div>
        </Panel>
      </div>
    </div>
  );
}

export function AgentsPage() {
  const { data } = useDashboardSnapshot();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<MappedModelInfo | null>(null);
  // Models are the "agents" — filter by the model identifier string
  const agents: MappedModelInfo[] = useMemo(
    () => (data?.models ?? []).filter((m) => m.model.toLowerCase().includes(query.toLowerCase())),
    [data, query],
  );
  return (
    <div className="feature-page">
      <PageHeading eyebrow="Agent mesh" title="Agents" description="Specialized workers coordinated as one JARVIS intelligence." />
      <div className="toolbar">
        <label className="search-control"><Search size={15} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Find an agent…" /></label>
        <span className="toolbar-status"><i />{agents.filter((a) => a.healthy).length} agents available</span>
      </div>
      <div className="agent-card-grid">
        {agents.map((agent) => (
          <button className="agent-card" key={agent.model} onClick={() => setSelected(agent)}>
            <div className="agent-card-top">
              <span className="agent-large-icon"><Bot size={22} /></span>
              <StatusDot status={agent.healthy ? "online" : "offline"} />
            </div>
            <h2>{agent.model.split("/")[1] ?? agent.model}</h2>
            <p>{agent.description}</p>
            <dl>
              <div><dt>Status</dt><dd>{agent.healthy ? "Healthy" : "Offline"}</dd></div>
              <div><dt>Context</dt><dd>{agent.maxContext?.toLocaleString() ?? "—"}</dd></div>
            </dl>
          </button>
        ))}
      </div>
      {selected && (
        <div className="drawer-backdrop" onMouseDown={() => setSelected(null)}>
          <aside className="detail-drawer" onMouseDown={(e) => e.stopPropagation()}>
            <button className="drawer-close" onClick={() => setSelected(null)} aria-label="Close"><XCircle size={20} /></button>
            <span className="agent-large-icon"><Bot size={26} /></span>
            <span className="eyebrow">Agent telemetry</span>
            <h2>{selected.model}</h2>
            <p>{selected.description}</p>
            <dl className="detail-grid">
              <div><dt>Status</dt><dd>{selected.healthy ? "Healthy" : "Offline"}</dd></div>
              <div><dt>Context</dt><dd>{selected.maxContext?.toLocaleString() ?? "—"}</dd></div>
              <div><dt>Enabled</dt><dd>{selected.enabled ? "Yes" : "No"}</dd></div>
              <div><dt>Contract</dt><dd>ModelInfo</dd></div>
            </dl>
          </aside>
        </div>
      )}
    </div>
  );
}
