/**
 * DTO Mapping Layer
 *
 * Maps the Python backend's snake_case JSON response to the frontend's
 * camelCase model exactly once, at the API boundary.
 *
 * Backend contract is frozen. Never modify this layer to match a React
 * component expectation — change the component instead.
 */

// ─── Raw backend types (snake_case, exactly as returned by FastAPI) ──────────

export interface RawProcess {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_percent: number;
}

export interface RawDisk {
  path: string;
  total_bytes: number;
  used_bytes: number;
  free_bytes: number;
  percent: number;
}

export interface RawGpu {
  name: string;
  vendor?: string | null;
  utilization_percent?: number | null;
  renderer_percent?: number | null;
  tiler_percent?: number | null;
  memory_used_bytes?: number | null;
  memory_allocated_bytes?: number | null;
  core_count?: number | null;
  temperature_celsius?: number | null;
  power_watts?: number | null;
  source: string;
  available: boolean;
}

export interface RawNetwork {
  bytes_sent: number;
  bytes_recv: number;
  upload_bps: number;
  download_bps: number;
  packets_sent: number;
  packets_recv: number;
}

export interface RawMemory {
  total_bytes: number;
  available_bytes: number;
  used_bytes: number;
  percent: number;
}

export interface RawSystemSnapshot {
  timestamp: string;
  hostname: string;
  platform: string;
  boot_time: string;
  uptime_seconds: number;
  cpu_percent: number;
  cpu_per_core_percent: number[];
  cpu_logical_count: number;
  cpu_physical_count?: number | null;
  memory: RawMemory;
  storage: RawDisk;
  disks: RawDisk[];
  network: RawNetwork;
  gpu: RawGpu;
  top_processes: RawProcess[];
  docker_containers: RawDockerContainer[];
  services: RawService[];
  metrics: RawMetric[];
}

export interface RawDockerContainer {
  name: string;
  status: string;
}

export interface RawService {
  id: string;
  name: string;
  status: string;
  category: string;
  detail?: string | null;
}

export interface RawMetric {
  key: string;
  label: string;
  value: number | null;
  unit: string;
  detail: string;
  available: boolean;
}

export interface RawModelInfo {
  profile: {
    model: string;
    strengths: string[];
    routing_keywords: string[];
    capabilities: Record<string, number>;
    max_context: number;
    description: string;
  };
  enabled: boolean;
  healthy: boolean;
}

export interface RawMission {
  id: string;
  goal: string;
  status: string;
  priority: string;
  execution_ids: string[];
  result?: any;
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
}

export interface RawMcpServer {
  id?: string;
  name: string;
  url?: string;
  status?: string;
}

export interface RawDashboardResponse {
  system: RawSystemSnapshot;
  missions: RawMission[];
  mcp_servers: RawMcpServer[];
  runtime_sessions: any[];
  capabilities: any[];
  models: RawModelInfo[];
}

// ─── Mapped frontend types (camelCase) ───────────────────────────────────────

export interface MappedProcess {
  pid: number;
  name: string;
  cpuPercent: number;
  memoryPercent: number;
}

export interface MappedDisk {
  path: string;
  totalBytes: number;
  usedBytes: number;
  freeBytes: number;
  percent: number;
}

export interface MappedGpu {
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

export interface MappedNetwork {
  bytesSent: number;
  bytesRecv: number;
  uploadBps: number;
  downloadBps: number;
  packetsSent: number;
  packetsRecv: number;
}

export interface MappedMemory {
  totalBytes: number;
  availableBytes: number;
  usedBytes: number;
  percent: number;
}

export interface MappedDockerContainer {
  name: string;
  status: string;
}

export interface MappedService {
  id: string;
  name: string;
  status: string;
  category: string;
  detail?: string | null;
}

export interface MappedMetric {
  key: string;
  label: string;
  value: number | null;
  unit: string;
  detail: string;
  available: boolean;
}

export interface MappedSystemSnapshot {
  timestamp: string;
  hostname: string;
  platform: string;
  bootTime: string;
  uptimeSeconds: number;
  cpuPercent: number;
  cpuPerCorePercent: number[];
  cpuLogicalCount: number;
  cpuPhysicalCount?: number | null;
  memory: MappedMemory;
  storage: MappedDisk;
  disks: MappedDisk[];
  network: MappedNetwork;
  gpu: MappedGpu;
  topProcesses: MappedProcess[];
  dockerContainers: MappedDockerContainer[];
  services: MappedService[];
  metrics: MappedMetric[];
}

export interface MappedModelInfo {
  model: string;
  description: string;
  strengths: string[];
  capabilities: Record<string, number>;
  maxContext: number;
  enabled: boolean;
  healthy: boolean;
}

export interface MappedMission {
  id: string;
  goal: string;
  status: string;
  priority: string;
  executionIds: string[];
  createdAt: string;
  updatedAt: string;
}

export interface MappedMcpServer {
  id: string;
  name: string;
  url?: string;
  status?: string;
}

export interface MappedDashboardSnapshot {
  system: MappedSystemSnapshot;
  missions: MappedMission[];
  mcpServers: MappedMcpServer[];
  runtimeSessions: any[];
  capabilities: any[];
  models: MappedModelInfo[];
}

// ─── Mappers ─────────────────────────────────────────────────────────────────

function mapProcess(raw: RawProcess): MappedProcess {
  return {
    pid: raw.pid,
    name: raw.name,
    cpuPercent: raw.cpu_percent,
    memoryPercent: raw.memory_percent,
  };
}

function mapDisk(raw: RawDisk): MappedDisk {
  return {
    path: raw.path,
    totalBytes: raw.total_bytes,
    usedBytes: raw.used_bytes,
    freeBytes: raw.free_bytes,
    percent: raw.percent,
  };
}

function mapGpu(raw: RawGpu): MappedGpu {
  return {
    name: raw.name,
    vendor: raw.vendor,
    utilizationPercent: raw.utilization_percent,
    rendererPercent: raw.renderer_percent,
    tilerPercent: raw.tiler_percent,
    memoryUsedBytes: raw.memory_used_bytes,
    memoryAllocatedBytes: raw.memory_allocated_bytes,
    coreCount: raw.core_count,
    temperatureCelsius: raw.temperature_celsius,
    powerWatts: raw.power_watts,
    source: raw.source,
    available: raw.available,
  };
}

function mapNetwork(raw: RawNetwork): MappedNetwork {
  return {
    bytesSent: raw.bytes_sent,
    bytesRecv: raw.bytes_recv,
    uploadBps: raw.upload_bps,
    downloadBps: raw.download_bps,
    packetsSent: raw.packets_sent,
    packetsRecv: raw.packets_recv,
  };
}

function mapMemory(raw: RawMemory): MappedMemory {
  return {
    totalBytes: raw.total_bytes,
    availableBytes: raw.available_bytes,
    usedBytes: raw.used_bytes,
    percent: raw.percent,
  };
}

function mapSystemSnapshot(raw: RawSystemSnapshot): MappedSystemSnapshot {
  return {
    timestamp: raw.timestamp,
    hostname: raw.hostname,
    platform: raw.platform,
    bootTime: raw.boot_time,
    uptimeSeconds: raw.uptime_seconds,
    cpuPercent: raw.cpu_percent,
    cpuPerCorePercent: raw.cpu_per_core_percent ?? [],
    cpuLogicalCount: raw.cpu_logical_count,
    cpuPhysicalCount: raw.cpu_physical_count,
    memory: mapMemory(raw.memory),
    storage: mapDisk(raw.storage),
    disks: (raw.disks ?? []).map(mapDisk),
    network: mapNetwork(raw.network),
    gpu: mapGpu(raw.gpu),
    topProcesses: (raw.top_processes ?? []).map(mapProcess),
    dockerContainers: (raw.docker_containers ?? []).map((c) => ({ name: c.name, status: c.status })),
    services: (raw.services ?? []).map((s) => ({
      id: s.id,
      name: s.name,
      status: s.status,
      category: s.category,
      detail: s.detail,
    })),
    metrics: raw.metrics ?? [],
  };
}

function mapModel(raw: RawModelInfo): MappedModelInfo {
  return {
    model: raw.profile.model,
    description: raw.profile.description,
    strengths: raw.profile.strengths ?? [],
    capabilities: raw.profile.capabilities ?? {},
    maxContext: raw.profile.max_context,
    enabled: raw.enabled,
    healthy: raw.healthy,
  };
}

function mapMission(raw: RawMission): MappedMission {
  return {
    id: raw.id,
    goal: raw.goal,
    status: raw.status,
    priority: raw.priority,
    executionIds: raw.execution_ids ?? [],
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  };
}

function mapMcpServer(raw: RawMcpServer): MappedMcpServer {
  return {
    id: raw.id ?? raw.name,
    name: raw.name,
    url: raw.url,
    status: raw.status,
  };
}

/**
 * Maps the raw /api/dashboard response to the canonical frontend model.
 * This is the ONLY place where snake_case → camelCase conversion happens.
 */
export function mapDashboardResponse(raw: RawDashboardResponse): MappedDashboardSnapshot {
  return {
    system: mapSystemSnapshot(raw.system),
    missions: (raw.missions ?? []).map(mapMission),
    mcpServers: (raw.mcp_servers ?? []).map(mapMcpServer),
    runtimeSessions: raw.runtime_sessions ?? [],
    capabilities: raw.capabilities ?? [],
    models: (raw.models ?? []).map(mapModel),
  };
}
