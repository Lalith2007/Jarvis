# Plugin Development Guide

All future JARVIS plugins MUST inherit from `BaseCapability`.

1. Create your class inheriting `BaseCapability`.
2. Construct a strict `CapabilityManifest`.
3. Implement the lifecycle methods: `initialize`, `validate`, `execute`, `cleanup`, `health_check`.
4. Register it dynamically via `CapabilityRegistry`.
