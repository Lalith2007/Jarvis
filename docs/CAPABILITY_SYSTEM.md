# JARVIS Capability System

The Capability System serves as the standardized, secure, and observable execution layer for all features in JARVIS. Every action—from planning a mission to reading a file—is implemented as a `BaseCapability` and orchestrated through the `CapabilityRegistry`.

## Architecture Overview

The architecture enforces strict decoupling between graph execution and the runtime capabilities:

1. **Mission Controller / Engine**: Traverses the DAG graph.
2. **CapabilityManager**: Acts as the boundary facade, constructing `CapabilityContext` and delegating to the lifecycle executor.
3. **CapabilityRegistry**: Resolves the requested capability id, verifies dependencies, and fetches the `BaseCapability`.
4. **CapabilityExecutorLifecycle**: Drives the state machine (`initialize` -> `validate` -> `execute` -> `cleanup` -> `health_check`), ensuring deterministic resource cleanup and emitting platform events.

By standardizing around this interface, JARVIS gains the ability to seamlessly hot-load plugins, isolate sandbox execution, and provide comprehensive execution metrics.
