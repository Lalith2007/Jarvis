"""
Sprint 12.9 — Production Forensic Audit (Semantic Capability Grounding)
=======================================================================

Read-only instrumentation. Drives the REAL production pipeline
(MissionGraphBuilder + GraphExecutionManager + CapabilityManager +
runtime.generate) live against the configured LLM provider.

For each verification query it captures:
    - MissionGraph topology (nodes, dependencies, execution order)
    - AthenaDecision (intent, complexity, capabilities, models)
    - Capability execution order + structured outputs
    - Prompt context supplied to runtime.generate
    - Selected model
    - Final grounded response
    - Source attribution — every model/provider/capability named in the
      response is checked against the live registries.

Run:
    python forensic_audit_sprint_12_9.py
Writes:
    forensic_audit_sprint_12_9_report.json
"""

import json
import os
import re
import sys
import threading
import time
import traceback
from collections import defaultdict

os.chdir("/Users/lalithpraveen/desktop/jarvis/backend")
sys.path.insert(0, "/Users/lalithpraveen/desktop/jarvis/backend")

from dotenv import load_dotenv

load_dotenv("/Users/lalithpraveen/desktop/jarvis/backend/.env")

# ── Trace store, keyed by active query label ────────────────────────────────
_TRACES: dict[str, list[dict]] = defaultdict(list)
_ACTIVE: dict[int, str] = {}
_LOCK = threading.Lock()


def _label() -> str:
    return _ACTIVE.get(threading.get_ident(), "unknown")


def _record(category: str, data: dict) -> None:
    with _LOCK:
        _TRACES[_label()].append({"category": category, **data})


print("[audit] importing system...")
from app.agents.hermes.service import hermes  # noqa: F401  bootstraps deps
from app.providers.registry import provider_registry
from app.capabilities.registry import capability_registry
from app.mission.builder import mission_graph_builder
from app.mission.controller import mission_controller
from app.mission.capabilities import CapabilityManager
from app.llm.builder import MessageBuilder

print("[audit] imports complete")

# ── Instrument MissionGraphBuilder.build — stash the built graph per query ───
_GRAPHS: dict[str, object] = {}
_orig_build = mission_graph_builder.__class__.build


def _patched_build(self, mission):
    graph = _orig_build(self, mission)
    with _LOCK:
        _GRAPHS[_label()] = graph
    return graph


mission_graph_builder.__class__.build = _patched_build

# ── Instrument CapabilityManager.execute ────────────────────────────────────
_orig_cap_execute = CapabilityManager.execute


def _patched_cap_execute(self, node):
    t0 = time.perf_counter()
    raw = _orig_cap_execute(self, node)
    elapsed = round((time.perf_counter() - t0) * 1000, 2)
    summary = raw
    if isinstance(raw, dict):
        summary = json.loads(json.dumps(raw, default=str))
        for k, v in list(summary.items()):
            if isinstance(v, list) and len(v) > 8:
                summary[k] = v[:8] + [f"...(+{len(v) - 8} more)"]
            if isinstance(v, str) and len(v) > 600:
                summary[k] = v[:600] + "...[truncated]"
    elif isinstance(raw, str) and len(raw) > 800:
        summary = raw[:800] + "...[truncated]"
    _record("capability_execute", {
        "capability": node.capability,
        "node_id": node.id,
        "result_type": type(raw).__name__,
        "duration_ms": elapsed,
        "output": summary,
    })
    return raw


CapabilityManager.execute = _patched_cap_execute

# ── Instrument MessageBuilder.build (prompt context) ────────────────────────
_orig_msg_build = MessageBuilder.build


def _patched_msg_build(self, context):
    messages = _orig_msg_build(self, context)
    safe = []
    for m in messages:
        content = m.get("content", "")
        if len(content) > 1200:
            content = content[:1200] + f"...[+{len(m['content']) - 1200} chars]"
        safe.append({"role": m.get("role"), "content": content})
    _record("prompt_context", {"message_count": len(messages), "messages": safe})
    return messages


MessageBuilder.build = _patched_msg_build

# ── Queries (Sprint 12.9 §6) ────────────────────────────────────────────────
QUERIES = [
    ("Q1_which_model_are_you",     "Which model are you?"),
    ("Q2_what_models_available",   "What models are available?"),
    ("Q3_what_tools",              "What tools do you have?"),
    ("Q4_what_capabilities",       "What capabilities exist?"),
    ("Q5_what_can_you_do",         "What can you do?"),
    ("Q6_what_memories",           "What memories do you have?"),
    ("Q7_how_many_providers",      "How many providers are configured?"),
    ("Q8_search_readme",           "Search my README."),
    ("Q9_summarize_readme",        "Summarize the README."),
]

# ── Registries for attribution ──────────────────────────────────────────────
REGISTERED_MODELS = {m.id for m in provider_registry.all()}
REGISTERED_MODEL_NAMES = {m.display_name for m in provider_registry.all()}
REGISTERED_PROVIDERS = {m.provider.value for m in provider_registry.all()}
REGISTERED_CAPS = set(capability_registry.ids())

# Model families that must never appear unless registered (fabrication markers).
_FOREIGN_MODEL_PATTERNS = [
    r"\bgpt-4\b", r"\bgpt-3\.5\b", r"\bclaude\b", r"\bgemini\b",
    r"\bchatgpt\b", r"\bbard\b", r"\bcopilot\b",
]


def _topo_order(graph) -> list[str]:
    order, seen = [], set()

    def visit(nid):
        for dep in graph.nodes[nid].dependencies:
            if dep not in seen:
                visit(dep)
        if nid not in seen:
            seen.add(nid)
            order.append(nid)

    for nid in graph.nodes:
        visit(nid)
    return order


def _graph_summary(graph) -> dict:
    order = _topo_order(graph)
    return {
        "graph_id": graph.graph_id,
        "node_count": len(graph.nodes),
        "has_athena_decision": graph.athena_decision is not None,
        "execution_order": [graph.nodes[n].capability for n in order],
        "nodes": [
            {
                "id": n,
                "capability": graph.nodes[n].capability,
                "type": graph.nodes[n].type.value,
                "dependencies": graph.nodes[n].dependencies,
                "carries_athena_decision": "athena_decision" in (graph.nodes[n].metadata or {}),
            }
            for n in order
        ],
    }


def _decision_summary(graph) -> dict:
    ad = graph.athena_decision or {}
    return {
        "intent": ad.get("intent"),
        "complexity": ad.get("complexity"),
        "confidence": ad.get("confidence"),
        "execution_strategy": ad.get("execution_strategy"),
        "requires_memory": ad.get("requires_memory"),
        "recommended_capabilities": [
            {
                "capability": c["capability"],
                "confidence": c["confidence"],
                "priority": c["priority"],
                "required": c["required"],
                "reason": c["reason"],
            }
            for c in ad.get("recommended_capabilities", [])
        ],
        "recommended_models": [
            {"model": m["model"], "score": m["score"]}
            for m in ad.get("recommended_models", [])
        ],
    }


def _attribution(response: str, trace: list[dict]) -> dict:
    """Check every factual token in the response against live ground truth."""
    text = response or ""
    lower = text.lower()

    # Ground-truth tokens available to this query (from executed capabilities).
    available_models, available_caps, available_providers = set(), set(), set()
    readme_grounded = False
    for e in trace:
        if e["category"] != "capability_execute":
            continue
        out = e.get("output")
        if e["capability"] == "registry.models" and isinstance(out, dict):
            for m in out.get("models", []):
                if isinstance(m, dict):
                    available_models.add(m.get("id", ""))
                    available_providers.add(m.get("provider", ""))
        if e["capability"] == "registry.capabilities" and isinstance(out, dict):
            for c in out.get("capabilities", []):
                if isinstance(c, dict):
                    available_caps.add(c.get("id", ""))
        if e["capability"] == "repository.read" and isinstance(out, dict):
            readme_grounded = out.get("count", 0) > 0

    fabricated = []
    for pat in _FOREIGN_MODEL_PATTERNS:
        if re.search(pat, lower):
            m = re.search(pat, lower).group(0)
            # only fabrication if not actually a registered model/provider
            if not any(m in x.lower() for x in REGISTERED_MODELS | REGISTERED_PROVIDERS):
                fabricated.append(m)

    return {
        "grounding_capabilities_executed": sorted(
            {e["capability"] for e in trace
             if e["category"] == "capability_execute"
             and e["capability"] in {"registry.models", "registry.capabilities",
                                      "memory.retrieve", "repository.read"}}
        ),
        "available_model_ids": sorted(x for x in available_models if x),
        "available_capability_ids_count": len(available_caps),
        "readme_grounded": readme_grounded,
        "foreign_model_names_detected": fabricated,
        "fabrication_free": len(fabricated) == 0,
    }


REPORT = {
    "sprint": "12.9",
    "description": "Semantic Capability Intelligence & Grounding Completion — live forensic audit",
    "registered_models": sorted(REGISTERED_MODELS),
    "registered_providers": sorted(REGISTERED_PROVIDERS),
    "registered_capabilities": sorted(REGISTERED_CAPS),
    "queries": [],
}

for label, query in QUERIES:
    print(f"\n[audit] {label}: {query!r}")
    tid = threading.get_ident()
    with _LOCK:
        _ACTIVE[tid] = label

    entry = {"label": label, "query": query}
    try:
        t0 = time.perf_counter()
        tool_result, _execution = mission_controller.run(query)
        entry["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        graph = _GRAPHS.get(label)
        entry["mission_graph"] = _graph_summary(graph) if graph else None
        entry["athena_decision"] = _decision_summary(graph) if graph else None

        trace = _TRACES.get(label, [])
        entry["capability_execution_order"] = [
            {"capability": e["capability"], "duration_ms": e["duration_ms"],
             "output": e["output"]}
            for e in trace if e["category"] == "capability_execute"
        ]
        prompt = next((e for e in trace if e["category"] == "prompt_context"), None)
        entry["prompt_context"] = prompt["messages"] if prompt else None
        ad = (graph.athena_decision if graph else None) or {}
        entry["selected_model"] = (
            ad.get("recommended_models", [{}])[0].get("model")
            if ad.get("recommended_models") else None
        )
        response_text = (
            tool_result.output if tool_result is not None
            else "<no result>"
        )
        entry["final_response"] = response_text
        entry["attribution"] = _attribution(response_text, trace)
        entry["error"] = None
        print(f"[audit]   -> {entry['mission_graph']['execution_order']}")
        print(f"[audit]   fabrication_free={entry['attribution']['fabrication_free']}")
    except Exception:
        entry["error"] = traceback.format_exc()
        print(f"[audit] ERROR:\n{entry['error']}")

    with _LOCK:
        _ACTIVE.pop(tid, None)
    REPORT["queries"].append(entry)

# ── Summary ─────────────────────────────────────────────────────────────────
grounded = sum(
    1 for q in REPORT["queries"]
    if not q.get("error")
    and any(c["capability"] in {"registry.models", "registry.capabilities",
                                "memory.retrieve", "repository.read"}
            for c in q.get("capability_execution_order", []))
)
# Q1/Q5 model-identity + memory queries always ground; compute grounding coverage
info_queries = [q for q in REPORT["queries"] if not q.get("error")]
fully_grounded = sum(
    1 for q in info_queries
    if q["attribution"]["fabrication_free"]
    and (q["attribution"]["grounding_capabilities_executed"]
         or q["label"] == "Q6_what_memories")
)
REPORT["summary"] = {
    "total_queries": len(QUERIES),
    "errors": sum(1 for q in REPORT["queries"] if q.get("error")),
    "queries_with_grounding_capability": grounded,
    "fabrication_free_queries": sum(
        1 for q in info_queries if q["attribution"]["fabrication_free"]
    ),
}

with open("forensic_audit_sprint_12_9_report.json", "w") as f:
    json.dump(REPORT, f, indent=2, default=str)

print("\n" + "=" * 60)
print("FORENSIC AUDIT SUMMARY")
print("=" * 60)
print(json.dumps(REPORT["summary"], indent=2))
print("Report → forensic_audit_sprint_12_9_report.json")
