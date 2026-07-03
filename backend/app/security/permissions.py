import tempfile
from pathlib import Path

from app.config.settings import settings


class PermissionManager:
    """
    Controls which filesystem locations JARVIS may access.
    """

    def __init__(self):
        self.allowed_roots = [
            Path(settings.OBSIDIAN_VAULT).resolve(),
            (Path.home() / "Desktop").resolve(),
            (Path.home() / "Documents").resolve(),
            (Path.home() / "Downloads").resolve(),
        ]

        # Allow the system temporary directory.
        #
        # On macOS, tempfile.gettempdir() may return /var/... while pytest
        # creates paths under /private/var/..., so we add both forms.
        temp_dir = Path(tempfile.gettempdir())

        candidates = {
            temp_dir,
            temp_dir.resolve(),
        }

        temp_str = str(temp_dir)

        if temp_str.startswith("/var/"):
            candidates.add(Path("/private") / temp_str.lstrip("/"))

        for candidate in candidates:
            try:
                resolved = candidate.resolve()
            except Exception:
                resolved = candidate

            if resolved not in self.allowed_roots:
                self.allowed_roots.append(resolved)

            if candidate not in self.allowed_roots:
                self.allowed_roots.append(candidate)

    def allowed(
        self,
        path: str,
    ) -> bool:

        target = Path(path)

        candidates = [target]

        try:
            candidates.append(target.resolve())
        except Exception:
            pass

        for candidate in candidates:
            for root in self.allowed_roots:
                try:
                    candidate.relative_to(root)
                    return True
                except ValueError:
                    continue

        return False


permissions = PermissionManager()
