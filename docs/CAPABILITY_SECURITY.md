# Capability Security

Capabilities operate in a constrained `CapabilityContext`.
They do not have access to JARVIS memory or root filesystems unless specific permissions are declared in the `manifest.permissions` and authorized by the registry.

Future extensions will run custom capabilities in secure, network-isolated sandboxes.
