# Capability Registry

The central component managing the lifecycle and discovery of all system capabilities.

## Dependency Resolution
Capabilities declare dependencies inside their `CapabilityManifest`. Upon registration, the registry:
1. Validates that all dependencies are currently loaded.
2. Constructs a dependency DAG to check for cyclic dependencies.
3. Automatically aborts registration if constraints are violated.

## Hot-Reloading & Plugins
The registry implements `register`, `unregister`, `reload`, and `discover` methods. This isolates capability loading from system startup, ensuring JARVIS can load community-authored plugins securely at runtime.
