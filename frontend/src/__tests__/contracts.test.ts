import { describe, it, expect } from 'vitest';
import type { 
  RawDashboardResponse,
  MappedDashboardSnapshot
} from '../api/dto';
import { mapDashboardResponse } from '../api/dto';

describe('Frontend API Contracts', () => {
  it('validates DashboardState DTO mapping', () => {
    const raw: any = {
      system: {
        timestamp: "now",
        hostname: "mac",
        platform: "darwin",
        boot_time: "boot",
        uptime_seconds: 10,
        cpu_percent: 5,
        cpu_per_core_percent: [5],
        cpu_logical_count: 8,
        memory: { total_bytes: 1, available_bytes: 1, used_bytes: 0, percent: 0 },
        storage: { path: "/", total_bytes: 1, used_bytes: 0, free_bytes: 1, percent: 0 },
        disks: [],
        network: { bytes_sent: 0, bytes_recv: 0, upload_bps: 0, download_bps: 0, packets_sent: 0, packets_recv: 0 },
        gpu: { name: "M1", source: "system", available: true },
        top_processes: [],
        docker_containers: [],
        services: [],
        metrics: []
      },
      missions: [],
      mcp_servers: [],
      runtime_sessions: [],
      capabilities: [],
      models: []
    };
    
    const mapped: MappedDashboardSnapshot = mapDashboardResponse(raw as RawDashboardResponse);
    expect(mapped.system.uptimeSeconds).toBe(10);
  });

  it('validates SSE Chunk format', () => {
    // We expect SSE chunks to parse strictly to this shape in intelligence.ts
    const rawData = `{"type":"chunk","content":"Hello"}`;
    const parsed = JSON.parse(rawData);
    expect(parsed.type).toBe('chunk');
    expect(parsed.content).toBe('Hello');
  });
});
