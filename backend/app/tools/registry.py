from app.tools.base import BaseTool
from app.tools.models import ToolCall, ToolResult
from app.capabilities.models import CapabilityType
from app.runtime.registry import runtime_registry, RuntimeProvider, ProviderMetadata


class ToolRegistry:
    """
    Registry for all available tools.
    """

    def __init__(self):
        self.tools: dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool,
    ) -> None:

        self.tools[tool.name] = tool
        
        def tool_handler(session, call_args=None, **kwargs):
            call = ToolCall(name=tool.name, arguments=call_args or {})
            res = tool.execute(call)
            from app.runtime.models import RuntimeResult
            if res.success:
                return RuntimeResult(success=True, output=res.output, metadata=res.metadata)
            return RuntimeResult(success=False, error=res.output, metadata=res.metadata)
            
        def get_cap(name):
            n = name.lower()
            if "file" in n or "dir" in n: return CapabilityType.FILESYSTEM
            if "terminal" in n or "shell" in n: return CapabilityType.TERMINAL
            if "python" in n: return CapabilityType.PYTHON_RUNTIME
            if "browser" in n or "search" in n: return CapabilityType.BROWSER
            if "memory" in n: return CapabilityType.MEMORY
            return CapabilityType.TOOL_USAGE
            
        provider = RuntimeProvider(
            capability=get_cap(tool.name),
            handler=tool_handler,
            metadata=ProviderMetadata(name=tool.name, version="1.0", description=tool.description if hasattr(tool, 'description') else "Tool")
        )
        runtime_registry.register(provider)

    def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:

        tool = self.tools.get(call.name)

        if tool is None:
            return ToolResult(
                success=False,
                output=f"Unknown tool: {call.name}",
            )

        return tool.execute(call)


tool_registry = ToolRegistry()
