from __future__ import annotations

import os
import platform
import re
import shutil
import socket
import subprocess
import time
from datetime import datetime, timezone
from functools import lru_cache

import psutil

from app.system.models import (
    DockerContainerSummary,
    GpuSnapshot,
    MemorySnapshot,
    NetworkSnapshot,
    ProcessSummary,
    ServiceHealth,
    StorageSnapshot,
    SystemMetric,
    SystemSnapshot,
)


class SystemTelemetryService:
    """Collects local host telemetry without inventing unavailable values."""

    def __init__(self) -> None:
        counters = psutil.net_io_counters()
        self._last_network_sample = (time.time(), counters.bytes_sent, counters.bytes_recv)
        psutil.cpu_percent(interval=None)

    def snapshot(self) -> SystemSnapshot:
        now = datetime.now(timezone.utc)
        cpu_percent = round(psutil.cpu_percent(interval=0.1), 1)
        cpu_per_core = [round(value, 1) for value in psutil.cpu_percent(interval=None, percpu=True)]
        memory = self._memory()
        storage = self._storage(self._primary_storage_path())
        disks = self._disks()
        network = self._network()
        gpu = self._gpu()
        boot_time = datetime.fromtimestamp(psutil.boot_time(), timezone.utc)

        metrics = [
            SystemMetric(
                key="cpu",
                label="CPU",
                value=cpu_percent,
                detail=f"{psutil.cpu_count(logical=True) or 0} logical cores",
            ),
            SystemMetric(
                key="gpu",
                label="GPU",
                value=gpu.utilization_percent,
                detail=self._gpu_detail(gpu),
                available=gpu.utilization_percent is not None,
            ),
            SystemMetric(
                key="memory",
                label="RAM",
                value=round(memory.percent, 1),
                detail=f"{self._format_bytes(memory.used_bytes)} / {self._format_bytes(memory.total_bytes)}",
            ),
            SystemMetric(
                key="storage",
                label="Storage",
                value=round(storage.percent, 1),
                detail=f"{self._format_bytes(storage.used_bytes)} / {self._format_bytes(storage.total_bytes)}",
            ),
            SystemMetric(
                key="network",
                label="Network",
                value=min(100, round((network.upload_bps + network.download_bps) / 125_000, 1)),
                unit="",
                detail=(
                    f"↓ {self._format_bits(network.download_bps)} / "
                    f"↑ {self._format_bits(network.upload_bps)}"
                ),
            ),
        ]

        return SystemSnapshot(
            timestamp=now.isoformat(),
            hostname=socket.gethostname(),
            platform=f"{platform.system()} {platform.release()} {platform.machine()}",
            boot_time=boot_time.isoformat(),
            uptime_seconds=int(time.time() - psutil.boot_time()),
            cpu_percent=cpu_percent,
            cpu_per_core_percent=cpu_per_core,
            cpu_logical_count=psutil.cpu_count(logical=True) or 0,
            cpu_physical_count=psutil.cpu_count(logical=False),
            memory=memory,
            storage=storage,
            disks=disks,
            network=network,
            gpu=gpu,
            top_processes=self._top_processes(),
            docker_containers=self._docker_containers(),
            services=self._services(gpu),
            metrics=metrics,
        )

    def _memory(self) -> MemorySnapshot:
        memory = psutil.virtual_memory()
        return MemorySnapshot(
            total_bytes=memory.total,
            available_bytes=memory.available,
            used_bytes=memory.used,
            percent=round(memory.percent, 1),
        )

    def _storage(self, path: str) -> StorageSnapshot:
        disk = psutil.disk_usage(path)
        return StorageSnapshot(
            path=path,
            total_bytes=disk.total,
            used_bytes=disk.used,
            free_bytes=disk.free,
            percent=round(disk.percent, 1),
        )

    def _disks(self) -> list[StorageSnapshot]:
        seen: set[str] = set()
        disks: list[StorageSnapshot] = []
        for partition in psutil.disk_partitions(all=False):
            mountpoint = partition.mountpoint
            if mountpoint in seen:
                continue
            seen.add(mountpoint)
            try:
                disks.append(self._storage(mountpoint))
            except (PermissionError, FileNotFoundError, OSError):
                continue
        if not any(disk.path == "/" for disk in disks):
            disks.insert(0, self._storage("/"))
        return sorted(disks, key=lambda disk: (disk.path != "/", disk.path))[:6]

    @staticmethod
    def _primary_storage_path() -> str:
        macos_data_volume = "/System/Volumes/Data"
        if platform.system() == "Darwin" and os.path.exists(macos_data_volume):
            return macos_data_volume
        return "/"

    def _network(self) -> NetworkSnapshot:
        now = time.time()
        counters = psutil.net_io_counters()
        last_time, last_sent, last_recv = self._last_network_sample
        elapsed = max(now - last_time, 0.001)
        upload_bps = max(0, (counters.bytes_sent - last_sent) / elapsed)
        download_bps = max(0, (counters.bytes_recv - last_recv) / elapsed)
        self._last_network_sample = (now, counters.bytes_sent, counters.bytes_recv)
        return NetworkSnapshot(
            bytes_sent=counters.bytes_sent,
            bytes_recv=counters.bytes_recv,
            upload_bps=round(upload_bps, 1),
            download_bps=round(download_bps, 1),
            packets_sent=counters.packets_sent,
            packets_recv=counters.packets_recv,
        )

    def _gpu(self) -> GpuSnapshot:
        return self._nvidia_gpu() or self._apple_gpu() or self._generic_gpu()

    def _nvidia_gpu(self) -> GpuSnapshot | None:
        if not shutil.which("nvidia-smi"):
            return None
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,vendor,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=1.5,
                check=True,
            )
        except (subprocess.SubprocessError, OSError):
            return None

        first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
        if not first:
            return None
        parts = [part.strip() for part in first.split(",")]
        name, vendor, utilization, memory_used, memory_total, temperature, power = (parts + [""] * 7)[:7]
        return GpuSnapshot(
            name=name or "NVIDIA GPU",
            vendor=vendor or "NVIDIA",
            utilization_percent=self._float_or_none(utilization),
            memory_used_bytes=self._mib_to_bytes(memory_used),
            memory_allocated_bytes=self._mib_to_bytes(memory_total),
            temperature_celsius=self._float_or_none(temperature),
            power_watts=self._float_or_none(power),
            source="nvidia-smi",
        )

    def _apple_gpu(self) -> GpuSnapshot | None:
        if platform.system() != "Darwin" or not shutil.which("ioreg"):
            return None
        try:
            result = subprocess.run(
                ["ioreg", "-r", "-c", "IOAccelerator", "-d", "1", "-w0"],
                capture_output=True,
                text=True,
                timeout=1.5,
                check=False,
            )
        except (subprocess.SubprocessError, OSError):
            return self._apple_gpu_identity_only()

        output = result.stdout
        if "PerformanceStatistics" not in output:
            return self._apple_gpu_identity_only()

        device_utilization = self._extract_ioreg_number(output, "Device Utilization %")
        renderer_utilization = self._extract_ioreg_number(output, "Renderer Utilization %")
        tiler_utilization = self._extract_ioreg_number(output, "Tiler Utilization %")
        memory_used = self._extract_ioreg_number(output, "In use system memory")
        memory_allocated = self._extract_ioreg_number(output, "Alloc system memory")
        core_count = self._extract_ioreg_number(output, "gpu-core-count")
        identity = self._apple_gpu_identity()

        return GpuSnapshot(
            name=identity["name"],
            vendor="Apple",
            utilization_percent=device_utilization,
            renderer_percent=renderer_utilization,
            tiler_percent=tiler_utilization,
            memory_used_bytes=int(memory_used) if memory_used is not None else None,
            memory_allocated_bytes=int(memory_allocated) if memory_allocated is not None else None,
            core_count=int(core_count) if core_count is not None else identity["core_count"],
            source="ioreg IOAccelerator",
        )

    def _apple_gpu_identity_only(self) -> GpuSnapshot | None:
        if platform.system() != "Darwin":
            return None
        identity = self._apple_gpu_identity()
        return GpuSnapshot(
            name=identity["name"],
            vendor="Apple",
            core_count=identity["core_count"],
            source="system_profiler",
            available=identity["name"] != "Apple GPU",
        )

    @lru_cache(maxsize=1)
    def _apple_gpu_identity(self) -> dict[str, int | str | None]:
        if not shutil.which("system_profiler"):
            return {"name": "Apple GPU", "core_count": None}
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
        except (subprocess.SubprocessError, OSError):
            return {"name": "Apple GPU", "core_count": None}

        chipset = re.search(r"Chipset Model:\s*(.+)", result.stdout)
        cores = re.search(r"Total Number of Cores:\s*(\d+)", result.stdout)
        return {
            "name": chipset.group(1).strip() if chipset else "Apple GPU",
            "core_count": int(cores.group(1)) if cores else None,
        }

    def _generic_gpu(self) -> GpuSnapshot:
        return GpuSnapshot(
            name="GPU telemetry unavailable",
            source="not detected",
            available=False,
        )

    def _top_processes(self) -> list[ProcessSummary]:
        ps_processes = self._top_processes_from_ps()
        if ps_processes:
            return ps_processes

        processes: list[ProcessSummary] = []
        for process in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = process.info
                cpu = float(info.get("cpu_percent") or 0)
                memory = float(info.get("memory_percent") or 0)
                if cpu <= 0 and memory <= 0:
                    continue
                processes.append(
                    ProcessSummary(
                        pid=int(info["pid"]),
                        name=str(info.get("name") or f"pid-{info['pid']}"),
                        cpu_percent=round(cpu, 1),
                        memory_percent=round(memory, 1),
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, TypeError):
                continue
        return sorted(processes, key=lambda item: item.cpu_percent, reverse=True)[:8]

    def _top_processes_from_ps(self) -> list[ProcessSummary]:
        if not shutil.which("ps"):
            return []
        try:
            result = subprocess.run(
                ["ps", "-arcwwwxo", "pid=,comm=,%cpu=,%mem="],
                capture_output=True,
                text=True,
                timeout=1,
                check=False,
            )
        except (subprocess.SubprocessError, OSError):
            return []

        processes: list[ProcessSummary] = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                pid = int(parts[0])
                cpu = float(parts[-2])
                memory = float(parts[-1])
            except ValueError:
                continue
            name = " ".join(parts[1:-2])
            processes.append(
                ProcessSummary(
                    pid=pid,
                    name=name,
                    cpu_percent=round(cpu, 1),
                    memory_percent=round(memory, 1),
                )
            )
        return processes[:8]

    def _docker_containers(self) -> list[DockerContainerSummary]:
        if not shutil.which("docker"):
            return []
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=1.5,
                check=False,
            )
        except (subprocess.SubprocessError, OSError):
            return []
        containers: list[DockerContainerSummary] = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            name, _, status = line.partition("\t")
            containers.append(DockerContainerSummary(name=name, status=status or "Running"))
        return containers[:8]

    def _services(self, gpu: GpuSnapshot) -> list[ServiceHealth]:
        return [
            ServiceHealth(id="backend", name="JARVIS API", status="connected", category="Core", detail="FastAPI online"),
            ServiceHealth(id="filesystem", name="Filesystem", status="connected", category="System", detail="psutil disk provider"),
            ServiceHealth(id="processes", name="Processes", status="connected", category="System", detail="psutil process provider"),
            ServiceHealth(id="network", name="Network", status="connected", category="System", detail="psutil network provider"),
            ServiceHealth(
                id="gpu",
                name=gpu.name,
                status="connected" if gpu.available else "disconnected",
                category="Hardware",
                detail=gpu.source,
            ),
            ServiceHealth(
                id="docker",
                name="Docker",
                status="connected" if shutil.which("docker") else "disconnected",
                category="Runtime",
                detail="Docker CLI detected" if shutil.which("docker") else "Docker CLI unavailable",
            ),
        ]

    def _gpu_detail(self, gpu: GpuSnapshot) -> str:
        if gpu.utilization_percent is not None:
            pieces = [gpu.name]
            if gpu.core_count:
                pieces.append(f"{gpu.core_count} cores")
            if gpu.memory_used_bytes is not None:
                pieces.append(f"{self._format_bytes(gpu.memory_used_bytes)} in use")
            return " · ".join(pieces)
        return f"{gpu.name} · {gpu.source}"

    @staticmethod
    def _extract_ioreg_number(output: str, key: str) -> float | None:
        match = re.search(rf'"{re.escape(key)}"\s*=\s*([0-9.]+)', output)
        return float(match.group(1)) if match else None

    @staticmethod
    def _float_or_none(value: str) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _mib_to_bytes(value: str) -> int | None:
        parsed = SystemTelemetryService._float_or_none(value)
        return int(parsed * 1024 * 1024) if parsed is not None else None

    @staticmethod
    def _format_bytes(value: float | int) -> str:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = float(value)
        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
            size /= 1024
        return f"{size:.1f} PB"

    @staticmethod
    def _format_bits(bytes_per_second: float) -> str:
        bits = bytes_per_second * 8
        units = ["bps", "Kbps", "Mbps", "Gbps"]
        for unit in units:
            if bits < 1000 or unit == units[-1]:
                return f"{bits:.1f} {unit}"
            bits /= 1000
        return f"{bits:.1f} Gbps"


system_telemetry = SystemTelemetryService()
