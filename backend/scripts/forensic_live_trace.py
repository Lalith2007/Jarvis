"""
Live production forensic trace — Sprint 12 architecture validation.

Runs the REAL in-process production code path (hermes.chat, exactly what the
/api/chat endpoint invokes) against live queries and instruments every stage:

  EventPublisher, MissionGraphBuilder, AthenaOrchestrator, GraphExecutionManager,
  CapabilityManager, MessageBuilder, LLMProvider (real calls), Reflection.

Queries run SEQUENTIALLY and events are bucketed per query (no thread-local
guessing) — this fixes the earlier harness flaw where ThreadPoolExecutor worker
threads recorded traces under "unknown".

Bypass detectors flag: second Athena routing pass, legacy vault.search,
direct/ungrounded LLM use.

Writes: scripts/forensic_live_report.json
"""
import json
import os
import sys
import time

os.chdir("/Users/lalithpraveen/desktop/jarvis/backend")
sys.path.insert(0, "/Users/lalithpraveen/desktop/jarvis/backend")

from dotenv import load_dotenv
load_dotenv("/Users/lalithpraveen/desktop/jarvis/backend/.env")

# ── Per-query capture buckets (queries run sequentially) ────────────────────
CURRENT = {"events": [], "caps": [], "prompts": [], "graph": None, "llm": []}
BYPASS = {"second_athena_route": 0, "legacy_vault_search": 0}


def _reset():
    CURRENT["events"] = []
    CURRENT["caps"] = []
    CURRENT["prompts"] = []
    CURRENT["graph"] = None
    CURRENT["llm"] = []


print("[trace] importing production modules...")
from app.agents.hermes.service import hermes
from app.providers.registry import provider_registry
from app.capabilities.registry import capability_registry
from app.mission.builder import mission_graph_builder
from app.mission.capabilities import CapabilityManager
from app.llm.builder import MessageBuilder
import app.llm.provider as prov
from app.platform.publisher import EventPublisher

# ── Instrument EventPublisher ───────────────────────────────────────────────
_orig_publish = EventPublisher.publish.__func__ if hasattr(EventPublisher.publish, "__func__") else EventPublisher.publish


def _patched_publish(*args, **kwargs):
    # publish is called as EventPublisher.publish(subsystem=..., event_type=..., ...)
    CURRENT["events"].append({
        "t": round(time.perf_counter(), 4),
        "subsystem": kwargs.get("subsystem"),
        "event_type": kwargs.get("event_type"),
        "payload_keys": list((kwargs.get("payload") or {}).keys()),
    })
    return _orig_publish(*args, **kwargs)


EventPublisher.publish = staticmethod(_patched_publish)

# ── Instrument MissionGraphBuilder ──────────────────────────────────────────
_orig_build = mission_graph_builder.__class__.build


def _patched_build(self, mission):
    g = _orig_build(self, mission)
    CURRENT["graph"] = g
    return g


mission_graph_builder.__class__.build = _patched_build

# ── Instrument CapabilityManager ────────────────────────────────────────────
_orig_cap = CapabilityManager.execute


def _patched_cap(self, node):
    t0 = time.perf_counter()
    raw = _orig_cap(self, node)
    dt = round((time.perf_counter() - t0) * 1000, 1)
    out = raw
    if isinstance(raw, dict):
        out = json.loads(json.dumps(raw, default=str))
        for k, v in list(out.items()):
            if isinstance(v, list) and len(v) > 6:
                out[k] = v[:6] + [f"...(+{len(v)-6})"]
            if isinstance(v, str) and len(v) > 400:
                out[k] = v[:400] + "…"
    elif isinstance(raw, str) and len(raw) > 400:
        out = raw[:400] + "…"
    CURRENT["caps"].append({"capability": node.capability, "node_id": node.id, "ms": dt, "output": out})
    return raw


CapabilityManager.execute = _patched_cap

# ── Instrument MessageBuilder ───────────────────────────────────────────────
_orig_msg = MessageBuilder.build


def _patched_msg(self, context):
    msgs = _orig_msg(self, context)
    CURRENT["prompts"].append([
        {"role": m.get("role"), "content": (m.get("content", "")[:500] + ("…" if len(m.get("content", "")) > 500 else ""))}
        for m in msgs
    ])
    return msgs


MessageBuilder.build = _patched_msg

# ── Instrument LLMProvider (REAL calls) ─────────────────────────────────────
_orig_chat = prov.LLMProvider.chat


def _patched_chat(self, *, model, messages):
    resp = _orig_chat(self, model=model, messages=messages)
    CURRENT["llm"].append({"mode": "chat", "model": model, "resp_preview": (resp or "")[:200]})
    return resp


prov.LLMProvider.chat = _patched_chat

_orig_stream = prov.LLMProvider.stream


def _patched_stream(self, *, model, messages):
    CURRENT["llm"].append({"mode": "stream", "model": model, "resp_preview": "<streamed>"})
    yield from _orig_stream(self, model=model, messages=messages)


prov.LLMProvider.stream = _patched_stream

# ── Bypass detectors ────────────────────────────────────────────────────────
try:
    from app.athena.router import athena as _router_athena
    _orig_route = _router_athena.__class__.route

    def _patched_route(self, *a, **k):
        BYPASS["second_athena_route"] += 1
        CURRENT["events"].append({"BYPASS": "second_athena_route"})
        return _orig_route(self, *a, **k)

    _router_athena.__class__.route = _patched_route
except Exception as e:
    print("[trace] router patch skipped:", e)

try:
    from app.memory.vault.service import VaultService
    _orig_vsearch = VaultService.search

    def _patched_vsearch(self, *a, **k):
        BYPASS["legacy_vault_search"] += 1
        CURRENT["events"].append({"BYPASS": "legacy_vault_search"})
        return _orig_vsearch(self, *a, **k)

    VaultService.search = _patched_vsearch
except Exception as e:
    print("[trace] vault patch skipped:", e)

print("[trace] instrumentation installed")

# ── Ground-truth registries ─────────────────────────────────────────────────
# All models stay routable; grounding queries route to the ranked primary
# (minimax for simple queries), which responds. glm/deepseek are untouched.
REG_MODELS = {m.id for m in provider_registry.all()}
REG_MODEL_NAMES = {m.display_name for m in provider_registry.all()}
REG_PROVIDERS = {m.provider.value for m in provider_registry.all()}
FOREIGN = ["gpt-4", "gpt-3.5", "claude", "gemini", "chatgpt", "bard", "palm", "copilot"]

QUERIES = [
    "Who are you?",
    "Which model are you?",
    "What models are available?",
    "What tools do you have?",
    "What capabilities exist?",
    "What memories do you have?",
    "How many providers are configured?",
]

REPORT = {
    "sprint": "12.8/12.9 live forensic",
    "registered_models": sorted(REG_MODELS),
    "registered_providers": sorted(REG_PROVIDERS),
    "registered_capability_count": len(capability_registry.ids()),
    "queries": [],
    "bypasses": BYPASS,
}


def _topo(g):
    order, seen = [], set()
    def visit(nid):
        for d in g.nodes[nid].dependencies:
            if d not in seen:
                visit(d)
        if nid not in seen:
            seen.add(nid); order.append(g.nodes[nid].capability)
    for nid in g.nodes:
        visit(nid)
    return order


def _attr(resp, caps):
    lower = (resp or "").lower()
    executed = {c["capability"] for c in caps}
    fabricated = []
    for f in FOREIGN:
        if f in lower and not any(f in x.lower() for x in REG_MODELS | REG_PROVIDERS | REG_MODEL_NAMES):
            fabricated.append(f)
    return {
        "grounding_caps_executed": sorted(executed & {"registry.models", "registry.capabilities", "memory.retrieve", "repository.read"}),
        "fabricated_foreign_models": fabricated,
        "fabrication_free": len(fabricated) == 0,
    }


for q in QUERIES:
    print(f"\n[trace] === {q} ===")
    _reset()
    t0 = time.perf_counter()
    try:
        resp, sid = hermes.chat(q)
        err = None
    except Exception as e:
        import traceback
        resp, sid, err = None, None, traceback.format_exc()
    # Give the background reflection thread a moment to emit its events.
    time.sleep(2.5)
    elapsed = round((time.perf_counter() - t0) * 1000, 1)

    g = CURRENT["graph"]
    evt_types = [e.get("event_type") for e in CURRENT["events"] if e.get("event_type")]
    REPORT["queries"].append({
        "query": q,
        "elapsed_ms": elapsed,
        "error": err,
        "final_response": resp,
        "selected_model": (CURRENT["llm"][0]["model"] if CURRENT["llm"] else None),
        "graph_execution_order": (_topo(g) if g else None),
        "graph_nodes": ([{"cap": n.capability, "deps": n.dependencies, "type": n.type.value} for n in g.nodes.values()] if g else None),
        "athena_decision": ({
            "intent": (g.athena_decision or {}).get("intent"),
            "recommended_capabilities": [
                {"capability": c["capability"], "required": c["required"], "confidence": c["confidence"], "priority": c["priority"]}
                for c in (g.athena_decision or {}).get("recommended_capabilities", [])
            ],
            "recommended_models": [m["model"] for m in (g.athena_decision or {}).get("recommended_models", [])],
        } if g and g.athena_decision else None),
        "capability_execution_order": CURRENT["caps"],
        "prompt_context": (CURRENT["prompts"][-1] if CURRENT["prompts"] else None),
        "llm_calls": CURRENT["llm"],
        "event_sequence": evt_types,
        "reflection_ran": any("Reflection" in (t or "") for t in evt_types),
        "attribution": _attr(resp, CURRENT["caps"]),
    })
    print(f"[trace]   order={_topo(g) if g else None}")
    print(f"[trace]   model={CURRENT['llm'][0]['model'] if CURRENT['llm'] else None} resp={str(resp)[:80]!r}")
    print(f"[trace]   events={evt_types}")

REPORT["bypasses"] = BYPASS
with open("scripts/forensic_live_report.json", "w") as f:
    json.dump(REPORT, f, indent=2, default=str)

print("\n" + "=" * 60)
print("BYPASSES:", BYPASS)
print("Report -> scripts/forensic_live_report.json")
print("=" * 60)
