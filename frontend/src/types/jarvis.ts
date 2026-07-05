export type ReactorMode =
  | "offline"
  | "idle"
  | "listening"
  | "thinking"
  | "routing"
  | "collaborating"
  | "browsing"
  | "memory"
  | "coding"
  | "speaking"
  | "error";

export type HealthState = "online" | "busy" | "idle" | "offline" | "error";

export interface MetricPoint {
  time: number;
  value: number;
}

export interface SystemMetric {
  key: "cpu" | "gpu" | "memory" | "storage" | "network";
  label: string;
  value: number | null;
  unit: string;
  detail: string;
  available: boolean;
  history: MetricPoint[];
}

export interface ProcessSummary {
  pid: number;
  name: string;
  cpuPercent: number;
  memoryPercent: number;
}

export interface DiskSummary {
  path: string;
  totalBytes: number;
  usedBytes: number;
  freeBytes: number;
  percent: number;
}

export interface GpuSummary {
  name: string;
  vendor?: string | null;
  utilizationPercent?: number | null;
  rendererPercent?: number | null;
  tilerPercent?: number | null;
  memoryUsedBytes?: number | null;
  memoryAllocatedBytes?: number | null;
  coreCount?: number | null;
  temperatureCelsius?: number | null;
  powerWatts?: number | null;
  source: string;
  available: boolean;
}

export interface DockerContainerSummary {
  name: string;
  status: string;
}

export interface SystemDetails {
  hostname: string;
  platform: string;
  bootTime: string;
  cpuPerCorePercent: number[];
  cpuLogicalCount: number;
  cpuPhysicalCount?: number | null;
  memory: {
    totalBytes: number;
    availableBytes: number;
    usedBytes: number;
    percent: number;
  };
  storage: DiskSummary;
  disks: DiskSummary[];
  network: {
    bytesSent: number;
    bytesRecv: number;
    uploadBps: number;
    downloadBps: number;
    packetsSent: number;
    packetsRecv: number;
  };
  gpu: GpuSummary;
  topProcesses: ProcessSummary[];
  dockerContainers: DockerContainerSummary[];
}

export interface AgentSummary {
  id: string;
  name: string;
  role: string;
  status: HealthState;
  lastActivity: string;
  mission?: string;
}

export interface MissionSummary {
  id: string;
  goal: string;
  status: "created" | "analyzing" | "planning" | "executing" | "waiting" | "reflecting" | "completed" | "failed" | "cancelled";
  priority: "low" | "normal" | "high" | "critical";
  progress: number;
  createdAt: string;
  modelsUsed: string[];
  toolsUsed: string[];
}

export interface ProjectSummary {
  id: string;
  name: string;
  description: string;
  version: string;
  progress: number;
  completedTasks: number;
  totalTasks: number;
  status: "active" | "paused" | "completed";
  eta: string;
}

export interface ServiceSummary {
  id: string;
  name: string;
  status: "connected" | "disconnected" | "syncing" | "error";
  category: string;
}

export interface CapabilitySummary {
  id: string;
  name: string;
  available: boolean;
  category: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  createdAt: string;
  status?: "sending" | "sent" | "error";
}

export interface LogEntry {
  id: string;
  timestamp: string;
  source: string;
  level: "info" | "success" | "warning" | "error";
  message: string;
}

export interface DashboardSnapshot {
  source: "backend" | "development-provider";
  backendOnline: boolean;
  uptimeSeconds: number;
  metrics: SystemMetric[];
  system?: SystemDetails;
  agents: AgentSummary[];
  missions: MissionSummary[];
  project: ProjectSummary;
  services: ServiceSummary[];
  capabilities: CapabilitySummary[];
  logs: LogEntry[];
}
