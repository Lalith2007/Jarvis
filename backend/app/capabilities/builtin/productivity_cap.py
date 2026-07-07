"""
Calendar + Email capabilities — Sprint 13 (architecture "calendar.create",
"email.send"). These produce real local artifacts with no credentials:
- calendar.create -> a valid .ics (RFC 5545) file
- email.compose  -> a valid .eml draft (RFC 5322)
Actual delivery (SMTP send / calendar sync) is a credentialed follow-up or an
MCP server; the drafting/creation half works fully local and is pipeline-executed.
"""
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory, CapabilityConfig, CapabilityContext,
    CapabilityDiagnostics, CapabilityManifest, CapabilityResult,
)
from app.security.permissions import permissions


def _write(path: str, content: str):
    safe = permissions.resolve_if_allowed(path)
    if safe is None:
        raise PermissionError("output path not allowed")
    safe.parent.mkdir(parents=True, exist_ok=True)
    safe.write_text(content, encoding="utf-8")
    return str(safe)


class CalendarCreateCapability(BaseCapability):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="calendar.create", name="Calendar Event", version="1.0.0", author="System",
            description="Create a calendar event as an .ics file (RFC 5545).",
            category=CapabilityCategory.SYSTEM, permissions=["calendar:write"],
            parameters={"title": {"type": "string"}, "start": {"type": "string"},
                        "duration_min": {"type": "integer"}, "out_path": {"type": "string"}},
        ), CapabilityConfig())

    def initialize(self, c): ...
    def validate(self, c):
        if not (c.runtime_state or {}).get("title"):
            raise ValueError("calendar.create requires 'title'")
    def cleanup(self, c): ...
    def health_check(self): return "healthy"
    def estimate_cost(self, c): return 0.0
    def estimate_latency(self, c): return 10.0

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        title = rs.get("title")
        start_raw = rs.get("start")
        try:
            start = datetime.fromisoformat(start_raw) if start_raw else datetime.now(timezone.utc)
        except ValueError:
            start = datetime.now(timezone.utc)
        dur = int(rs.get("duration_min", 30))
        end = start + timedelta(minutes=dur)
        fmt = lambda d: d.strftime("%Y%m%dT%H%M%SZ")
        uid = f"{fmt(start)}-{abs(hash(title)) % 10**8}@jarvis"
        ics = (
            "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//JARVIS//EN\nBEGIN:VEVENT\n"
            f"UID:{uid}\nDTSTAMP:{fmt(datetime.now(timezone.utc))}\n"
            f"DTSTART:{fmt(start)}\nDTEND:{fmt(end)}\nSUMMARY:{title}\n"
            f"DESCRIPTION:{rs.get('description','')}\nEND:VEVENT\nEND:VCALENDAR\n"
        )
        out = rs.get("out_path") or f"/tmp/jarvis_event_{fmt(start)}.ics"
        try:
            path = _write(out, ics)
            return CapabilityResult(success=True, status="completed",
                result={"path": path, "title": title, "start": fmt(start), "end": fmt(end)})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])


class EmailComposeCapability(BaseCapability):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="email.compose", name="Email Compose", version="1.0.0", author="System",
            description="Compose an email as an .eml draft (RFC 5322). Send needs SMTP creds/MCP.",
            category=CapabilityCategory.NETWORK, permissions=["email:draft"],
            parameters={"to": {"type": "string"}, "subject": {"type": "string"},
                        "body": {"type": "string"}, "out_path": {"type": "string"}},
        ), CapabilityConfig())

    def initialize(self, c): ...
    def validate(self, c):
        rs = c.runtime_state or {}
        if not rs.get("to") or not rs.get("subject"):
            raise ValueError("email.compose requires 'to' and 'subject'")
    def cleanup(self, c): ...
    def health_check(self): return "healthy"
    def estimate_cost(self, c): return 0.0
    def estimate_latency(self, c): return 10.0

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        msg = EmailMessage()
        msg["To"] = rs["to"]
        msg["Subject"] = rs["subject"]
        msg["From"] = rs.get("from", "jarvis@localhost")
        msg.set_content(rs.get("body", ""))
        out = rs.get("out_path") or "/tmp/jarvis_draft.eml"
        try:
            path = _write(out, msg.as_string())
            return CapabilityResult(success=True, status="completed",
                result={"path": path, "to": rs["to"], "subject": rs["subject"], "sent": False})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])
