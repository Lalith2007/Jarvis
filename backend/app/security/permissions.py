import os
import tempfile
from pathlib import Path

from app.config.settings import BASE_DIR, settings


class PermissionManager:
    """
    Controls which filesystem locations JARVIS may access.

    Security model: a path is allowed only if its FULLY RESOLVED form (symlinks
    and `..` collapsed) lies inside one of the allowed roots.  Validation is
    always done on the resolved path, never the raw string, so
    `<root>/../../../etc/passwd` cannot escape the sandbox.  Callers should
    operate on the resolved path returned by `resolve_if_allowed`.
    """

    def __init__(self):
        raw_roots: list[Path] = []

        # 1. Configured vault (env-driven, never hardcoded).
        vault = getattr(settings, "VAULT_PATH", None) or getattr(
            settings, "OBSIDIAN_VAULT", None
        )
        if vault:
            raw_roots.append(Path(vault))

        # 2. The JARVIS repository root (computed from BASE_DIR, not a literal) —
        #    so repository.read and repo-relative tools work anywhere the repo lives.
        raw_roots.append(BASE_DIR.parent)

        # 3. Extra workspaces from the environment (comma-separated), so the
        #    allowed surface is configurable per install with no hardcoded paths.
        for entry in os.getenv("JARVIS_ALLOWED_ROOTS", "").split(","):
            entry = entry.strip()
            if entry:
                raw_roots.append(Path(entry).expanduser())

        # System temp dir — pytest and tooling write here.  On macOS
        # gettempdir() may be /var/... while resolved paths are /private/var/...
        temp_dir = Path(tempfile.gettempdir())
        raw_roots.append(temp_dir)
        temp_str = str(temp_dir)
        if temp_str.startswith("/var/"):
            raw_roots.append(Path("/private") / temp_str.lstrip("/"))

        # Store roots in fully-resolved form and de-duplicate.
        resolved_roots: list[Path] = []
        for root in raw_roots:
            try:
                resolved = root.resolve()
            except OSError:
                continue
            if resolved not in resolved_roots:
                resolved_roots.append(resolved)

        self.allowed_roots = resolved_roots

    def resolve_if_allowed(self, path: str) -> Path | None:
        """
        Return the resolved path if it lies within an allowed root, else None.

        This resolves `..` and symlinks BEFORE validating, closing the
        path-traversal / symlink-escape hole.
        """
        try:
            real = Path(path).resolve()
        except (OSError, RuntimeError, ValueError):
            return None

        for root in self.allowed_roots:
            try:
                real.relative_to(root)
                return real
            except ValueError:
                continue
        return None

    def allowed(self, path: str) -> bool:
        return self.resolve_if_allowed(path) is not None


permissions = PermissionManager()
