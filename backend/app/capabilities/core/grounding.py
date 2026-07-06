"""
Canonical set of grounding capability IDs — single source of truth.

A "grounding" capability produces authoritative system data (models, providers,
capabilities, memory, repository files) that runtime.generate must treat as
ground truth.  When such a capability is marked `required` in the
AthenaDecision, runtime.generate refuses to answer from prior knowledge if its
output is missing (see runtime_cap._validate_grounding), and the prompt builder
injects the grounding-enforcement directive.

Import this set everywhere instead of re-declaring literal sets — divergent
copies previously caused repository.read grounding to skip enforcement.
"""

GROUNDING_CAPABILITY_IDS: frozenset[str] = frozenset(
    {
        "registry.models",
        "registry.capabilities",
        "memory.retrieve",
        "repository.read",
        "vault.search",
    }
)
