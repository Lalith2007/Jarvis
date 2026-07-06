"""
Durable mission store (Sprint 13.9).

Checkpoints missions to disk so background/long-running missions survive an
Electron/backend restart. On recovery, missions left mid-flight are marked
recoverable (WAITING) instead of silently lost.
"""

import json
import logging
from pathlib import Path

from app.config.settings import BASE_DIR
from app.mission.models import Mission, MissionStatus

logger = logging.getLogger(__name__)

# Statuses that mean "in flight" — if seen at startup, the process died mid-mission.
_IN_FLIGHT = {
    MissionStatus.ANALYZING,
    MissionStatus.PLANNING,
    MissionStatus.EXECUTING,
    MissionStatus.WAITING,
    MissionStatus.REFLECTING,
}


class MissionStore:
    def __init__(self, root: Path | str | None = None):
        self.root = Path(root) if root else (BASE_DIR / "data" / "missions")

    def _path(self, mission_id: str) -> Path:
        return self.root / f"{mission_id}.json"

    def checkpoint(self, mission: Mission) -> None:
        """Persist a mission snapshot (best-effort — never breaks execution)."""
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            self._path(mission.id).write_text(mission.model_dump_json(), encoding="utf-8")
        except Exception as exc:
            logger.debug("mission checkpoint skipped for %s: %s", mission.id, exc)

    def load(self, mission_id: str) -> Mission | None:
        p = self._path(mission_id)
        if not p.exists():
            return None
        try:
            return Mission.model_validate_json(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    def load_all(self) -> list[Mission]:
        if not self.root.exists():
            return []
        out = []
        for p in sorted(self.root.glob("*.json")):
            try:
                out.append(Mission.model_validate_json(p.read_text(encoding="utf-8")))
            except Exception:
                continue
        return out

    def delete(self, mission_id: str) -> None:
        try:
            self._path(mission_id).unlink(missing_ok=True)
        except Exception:
            pass

    def recover_incomplete(self) -> list[Mission]:
        """
        Load persisted missions that were in flight when the process stopped and
        mark them recoverable (WAITING). Returns the recovered missions.
        """
        recovered = []
        for mission in self.load_all():
            if mission.status in _IN_FLIGHT:
                mission.status = MissionStatus.WAITING
                mission.metadata["recovered"] = True
                self.checkpoint(mission)
                recovered.append(mission)
        return recovered


mission_store = MissionStore()
