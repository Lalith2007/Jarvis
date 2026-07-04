from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


MetricKey = Literal["cpu", "gpu", "memory", "storage", "network"]


class SystemMetric(BaseModel):
    key: MetricKey
    label: str
    value: float | None = Field(default=None, ge=0)
    unit: str = "%"
    detail: str
    available: bool = True


class MemorySnapshot(BaseModel):
    total_bytes: int
    available_bytes: int
    used_bytes: int
    percent: float


class StorageSnapshot(BaseModel):
    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent: float


class NetworkSnapshot(BaseModel):
    bytes_sent: int
    bytes_recv: int
    upload_bps: float
    download_bps: float
    packets_sent: int
    packets_recv: int


class GpuSnapshot(BaseModel):
    name: str
    vendor: str | None = None
    utilization_percent: float | None = None
    renderer_percent: float | None = None
    tiler_percent: float | None = None
    memory_used_bytes: int | None = None
    memory_allocated_bytes: int | None = None
    core_count: int | None = None
    temperature_celsius: float | None = None
    power_watts: float | None = None
    source: str
    available: bool = True


class ProcessSummary(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float


class DockerContainerSummary(BaseModel):
    name: str
    status: str


class ServiceHealth(BaseModel):
    id: str
    name: str
    status: Literal["connected", "disconnected", "syncing", "error"]
    category: str
    detail: str | None = None


class SystemSnapshot(BaseModel):
    timestamp: str
    hostname: str
    platform: str
    boot_time: str
    uptime_seconds: int
    cpu_percent: float
    cpu_per_core_percent: list[float]
    cpu_logical_count: int
    cpu_physical_count: int | None
    memory: MemorySnapshot
    storage: StorageSnapshot
    disks: list[StorageSnapshot]
    network: NetworkSnapshot
    gpu: GpuSnapshot
    top_processes: list[ProcessSummary]
    docker_containers: list[DockerContainerSummary]
    services: list[ServiceHealth]
    metrics: list[SystemMetric]

