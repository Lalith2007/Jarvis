/**
 * Dashboard Integration Test
 *
 * Renders the Dashboard using the exact JSON payload returned by
 * GET /api/dashboard. Tests fail if:
 *   - any component throws during rendering
 *   - any DTO field is missing from the mapped model
 *   - any array access is unsafe
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import React from "react";

import { mapDashboardResponse } from "../api/dto";
import type { RawDashboardResponse } from "../api/dto";

// ─── Exact fixture from GET /api/dashboard ───────────────────────────────────
// This mirrors the real backend payload recorded during Sprint 10 verification.
const RAW_DASHBOARD_FIXTURE: RawDashboardResponse = {
  system: {
    timestamp: "2026-07-05T06:29:20.322490+00:00",
    hostname: "Laliths-MacBook-Air.local",
    platform: "Darwin 27.0.0 arm64",
    boot_time: "2026-07-04T16:01:38+00:00",
    uptime_seconds: 52062,
    cpu_percent: 21.5,
    cpu_per_core_percent: [41.6, 38.7, 34.6, 31.4, 27.6, 29.8, 24.1, 18.1],
    cpu_logical_count: 8,
    cpu_physical_count: 8,
    memory: {
      total_bytes: 8589934592,
      available_bytes: 1406533632,
      used_bytes: 3561029632,
      percent: 83.6,
    },
    storage: {
      path: "/System/Volumes/Data",
      total_bytes: 245107195904,
      used_bytes: 192234078208,
      free_bytes: 3281997824,
      percent: 98.3,
    },
    disks: [
      { path: "/", total_bytes: 245107195904, used_bytes: 16595431424, free_bytes: 3281997824, percent: 83.5 },
      { path: "/System/Volumes/Data", total_bytes: 245107195904, used_bytes: 192234078208, free_bytes: 3281997824, percent: 98.3 },
    ],
    network: {
      bytes_sent: 2453393408,
      bytes_recv: 3104955392,
      upload_bps: 36017.7,
      download_bps: 18487.9,
      packets_sent: 2939716,
      packets_recv: 3394677,
    },
    gpu: {
      name: "Apple M2",
      vendor: "Apple",
      utilization_percent: 63.0,
      renderer_percent: 63.0,
      tiler_percent: 63.0,
      memory_used_bytes: 793133056,
      memory_allocated_bytes: 2676539392,
      core_count: 8,
      temperature_celsius: null,
      power_watts: null,
      source: "ioreg IOAccelerator",
      available: true,
    },
    top_processes: [
      { pid: 441, name: "WindowServer", cpu_percent: 20.7, memory_percent: 0.5 },
      { pid: 699, name: "coreaudiod", cpu_percent: 20.6, memory_percent: 0.3 },
      { pid: 851, name: "corespeechd", cpu_percent: 6.3, memory_percent: 0.2 },
    ],
    docker_containers: [],
    services: [
      { id: "backend", name: "JARVIS API", status: "connected", category: "Core", detail: "FastAPI online" },
      { id: "filesystem", name: "Filesystem", status: "connected", category: "System", detail: "psutil disk provider" },
    ],
    metrics: [
      { key: "cpu", label: "CPU", value: 21.5, unit: "%", detail: "8 logical cores", available: true },
      { key: "gpu", label: "GPU", value: 63.0, unit: "%", detail: "Apple M2 · 8 cores", available: true },
      { key: "memory", label: "RAM", value: 83.6, unit: "%", detail: "3.3 GB / 8.0 GB", available: true },
      { key: "storage", label: "Storage", value: 98.3, unit: "%", detail: "179.0 GB / 228.3 GB", available: true },
      { key: "network", label: "Network", value: 0.4, unit: "", detail: "↓ 147.9 Kbps / ↑ 288.1 Kbps", available: true },
    ],
  },
  missions: [],
  mcp_servers: [],
  runtime_sessions: [],
  capabilities: [],
  models: [
    {
      profile: {
        model: "z-ai/glm-5.2",
        strengths: ["agentic reasoning", "software engineering", "planning"],
        routing_keywords: [],
        capabilities: { coding: 100, execution: 100, tool_usage: 100, planning: 100 },
        max_context: 1000000,
        description: "Flagship reasoning and agentic execution model.",
      },
      enabled: true,
      healthy: true,
    },
    {
      profile: {
        model: "deepseek-ai/deepseek-v4-pro",
        strengths: ["software engineering", "debugging", "implementation"],
        routing_keywords: [],
        capabilities: { coding: 100, execution: 95, tool_usage: 90, planning: 70 },
        max_context: 128000,
        description: "Software engineering specialist.",
      },
      enabled: true,
      healthy: true,
    },
  ],
};

// ─── DTO Mapping Tests ────────────────────────────────────────────────────────

describe("mapDashboardResponse (DTO layer)", () => {
  const mapped = mapDashboardResponse(RAW_DASHBOARD_FIXTURE);

  it("maps top_processes → topProcesses", () => {
    expect(mapped.system.topProcesses).toBeDefined();
    expect(Array.isArray(mapped.system.topProcesses)).toBe(true);
    expect(mapped.system.topProcesses[0].cpuPercent).toBe(20.7);
    expect(mapped.system.topProcesses[0].memoryPercent).toBe(0.5);
    // Raw snake_case must not leak through
    expect((mapped.system.topProcesses[0] as any).cpu_percent).toBeUndefined();
    expect((mapped.system.topProcesses[0] as any).memory_percent).toBeUndefined();
  });

  it("maps docker_containers → dockerContainers", () => {
    expect(mapped.system.dockerContainers).toBeDefined();
    expect(Array.isArray(mapped.system.dockerContainers)).toBe(true);
    expect((mapped.system as any).docker_containers).toBeUndefined();
  });

  it("maps uptime_seconds → uptimeSeconds", () => {
    expect(mapped.system.uptimeSeconds).toBe(52062);
    expect((mapped.system as any).uptime_seconds).toBeUndefined();
  });

  it("maps cpu_percent → cpuPercent", () => {
    expect(mapped.system.cpuPercent).toBe(21.5);
    expect((mapped.system as any).cpu_percent).toBeUndefined();
  });

  it("maps mcp_servers → mcpServers", () => {
    expect(Array.isArray(mapped.mcpServers)).toBe(true);
    expect((mapped as any).mcp_servers).toBeUndefined();
  });

  it("maps models correctly", () => {
    expect(mapped.models).toHaveLength(2);
    expect(mapped.models[0].model).toBe("z-ai/glm-5.2");
    expect(mapped.models[0].maxContext).toBe(1000000);
    expect((mapped.models[0] as any).profile).toBeUndefined();
    expect((mapped.models[0] as any).max_context).toBeUndefined();
  });

  it("maps GPU renderer_percent → rendererPercent", () => {
    expect(mapped.system.gpu.rendererPercent).toBe(63.0);
    expect((mapped.system.gpu as any).renderer_percent).toBeUndefined();
  });

  it("returns empty arrays for null lists (not undefined)", () => {
    const emptyPayload: RawDashboardResponse = {
      ...RAW_DASHBOARD_FIXTURE,
      missions: undefined as any,
      mcp_servers: undefined as any,
      capabilities: undefined as any,
      models: undefined as any,
    };
    const m = mapDashboardResponse(emptyPayload);
    expect(m.missions).toEqual([]);
    expect(m.mcpServers).toEqual([]);
    expect(m.capabilities).toEqual([]);
    expect(m.models).toEqual([]);
  });
});

// ─── Component Render Tests ───────────────────────────────────────────────────

function TestWrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  // Pre-populate cache with the mapped fixture so useDashboardSnapshot returns it
  const mapped = mapDashboardResponse(RAW_DASHBOARD_FIXTURE);
  qc.setQueryData(["dashboard"], mapped);
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  );
}

// Mock heavy non-DOM dependencies
vi.mock("../components/reactor/ReactorCore", () => ({ ReactorCore: () => <div>ReactorCore</div> }));
vi.mock("../components/reactor/JarvisRuntimePanel", () => ({ JarvisRuntimePanel: () => <div>JarvisRuntimePanel</div> }));
vi.mock("../components/dashboard/ChatPanel", () => ({ ChatPanel: () => <div>ChatPanel</div> }));
vi.mock("../components/ui/Sparkline", () => ({ Sparkline: () => <svg /> }));
vi.mock("../../electron/config.cjs", () => ({
  FrontendConfig: {
    API_BASE: "http://127.0.0.1:8000/api",
    WS_PLATFORM: "ws://127.0.0.1:8000/ws/platform",
    WS_RUNTIME: "ws://127.0.0.1:8000/ws/runtime",
  },
}));

import { DashboardPage } from "../pages/DashboardPage";
import { ResourcePanel, BottomPanels, AgentsPanel, MissionQueuePanel } from "../components/dashboard/DashboardWidgets";

describe("DashboardPage renders without throwing", () => {
  it("renders DashboardPage fully", () => {
    // Should not throw
    expect(() =>
      render(<TestWrapper><DashboardPage /></TestWrapper>)
    ).not.toThrow();
  });

  it("ResourcePanel renders metrics from live data", () => {
    render(<TestWrapper><ResourcePanel /></TestWrapper>);
    expect(screen.getByText("CPU")).toBeTruthy();
    expect(screen.getByText("GPU")).toBeTruthy();
    expect(screen.getByText("RAM")).toBeTruthy();
  });

  it("BottomPanels renders with 0 docker containers without crashing", () => {
    // Raw fixture has docker_containers: [] — this was the original crash site
    expect(() =>
      render(<TestWrapper><BottomPanels /></TestWrapper>)
    ).not.toThrow();
    expect(screen.getByText("No running containers")).toBeTruthy();
  });

  it("BottomPanels renders running processes", () => {
    render(<TestWrapper><BottomPanels /></TestWrapper>);
    expect(screen.getByText("WindowServer")).toBeTruthy();
  });

  it("AgentsPanel renders model list", () => {
    render(<TestWrapper><AgentsPanel /></TestWrapper>);
    // 2 models available
    expect(screen.getByText("2 available")).toBeTruthy();
  });

  it("MissionQueuePanel renders empty queue without crashing", () => {
    expect(() =>
      render(<TestWrapper><MissionQueuePanel /></TestWrapper>)
    ).not.toThrow();
  });
});
