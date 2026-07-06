from app.capabilities.registry import capability_registry
from app.capabilities.builtin.analyzer_cap import AnalyzerCapability
from app.capabilities.builtin.router_cap import RouterCapability
from app.capabilities.builtin.planner_cap import PlannerCapability
from app.capabilities.builtin.executor_cap import ExecutorCapability
from app.capabilities.builtin.reflector_cap import ReflectorCapability
from app.capabilities.builtin.runtime_cap import RuntimeGenerateCapability
from app.capabilities.builtin.registry_cap import RegistryCapability
from app.capabilities.builtin.capabilities_cap import CapabilityRegistryCapability
from app.capabilities.builtin.repository_cap import RepositoryReadCapability
from app.capabilities.builtin.obsidian_cap import ObsidianNoteCapability
from app.capabilities.builtin.computer_cap import (
    ComputerFilesystemCapability,
    ComputerTerminalCapability,
    ComputerProcessCapability,
    ComputerClipboardCapability,
)
from app.capabilities.builtin.browser_cap import (
    BrowserNavigateCapability,
    BrowserExtractCapability,
    BrowserInteractCapability,
    BrowserCaptureCapability,
)
from app.capabilities.builtin.research_cap import ResearchGatherCapability
from app.capabilities.builtin.voice_cap import (
    VoiceTranscribeCapability,
    VoiceSpeakCapability,
)
from app.capabilities.builtin.social_cap import SocialPostCapability
from app.capabilities.builtin.vault_cap import VaultSearchCapability
from app.capabilities.builtin.python_cap import PythonExecuteCapability
from app.memory.capabilities import (
    MemoryReadCapability,
    MemoryWriteCapability,
    MemoryConsolidateCapability,
)


def register_builtins():
    capability_registry.register(AnalyzerCapability())
    capability_registry.register(RouterCapability())
    capability_registry.register(PlannerCapability())
    capability_registry.register(ExecutorCapability())
    capability_registry.register(ReflectorCapability())
    capability_registry.register(RuntimeGenerateCapability())
    capability_registry.register(RegistryCapability())
    capability_registry.register(CapabilityRegistryCapability())
    capability_registry.register(RepositoryReadCapability())
    capability_registry.register(ObsidianNoteCapability())
    capability_registry.register(ComputerFilesystemCapability())
    capability_registry.register(ComputerTerminalCapability())
    capability_registry.register(ComputerProcessCapability())
    capability_registry.register(ComputerClipboardCapability())
    capability_registry.register(BrowserNavigateCapability())
    capability_registry.register(BrowserExtractCapability())
    capability_registry.register(BrowserInteractCapability())
    capability_registry.register(BrowserCaptureCapability())
    capability_registry.register(ResearchGatherCapability())
    capability_registry.register(VoiceTranscribeCapability())
    capability_registry.register(VoiceSpeakCapability())
    capability_registry.register(SocialPostCapability())
    capability_registry.register(VaultSearchCapability())
    capability_registry.register(PythonExecuteCapability())
    capability_registry.register(MemoryReadCapability())
    capability_registry.register(MemoryWriteCapability())
    capability_registry.register(MemoryConsolidateCapability())
