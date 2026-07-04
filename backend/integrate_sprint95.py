import os

BASE_DIR = "/Users/lalithpraveen/Desktop/Jarvis/backend"

def modify_file(path, replacements):
    full_path = os.path.join(BASE_DIR, path)
    with open(full_path, "r") as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(full_path, "w") as f:
        f.write(content)

def main():
    # 1. Update RuntimeExecutor to avoid double-wrapping
    modify_file("app/runtime/executor.py", [
        ("return RuntimeResult(success=True, output=output, execution_time_ms=duration)",
         """if isinstance(output, RuntimeResult):
                output.execution_time_ms = duration
                return output
            return RuntimeResult(success=True, output=output, execution_time_ms=duration)""")
    ])

    # 2. Update ToolRegistry to also wrap as RuntimeProvider
    modify_file("app/tools/registry.py", [
        ("from app.tools.models import ToolCall, ToolResult",
         "from app.tools.models import ToolCall, ToolResult\nfrom app.capabilities.models import CapabilityType\nfrom app.runtime.registry import runtime_registry, RuntimeProvider, ProviderMetadata"),
        ("self.tools[tool.name] = tool",
         """self.tools[tool.name] = tool
        
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
        runtime_registry.register(provider)"""
        )
    ])

    # 3. Update RuntimeRegistry to accept provider_name
    modify_file("app/runtime/registry.py", [
        ("def get_provider(self, capability: CapabilityType) -> RuntimeProvider | None:",
         "def get_provider(self, capability: CapabilityType, provider_name: str | None = None) -> RuntimeProvider | None:"),
        ("if p.metadata.is_healthy:",
         "if p.metadata.is_healthy:\n                if provider_name and p.metadata.name != provider_name:\n                    continue")
    ])

    # 4. Update RuntimeDispatcher
    modify_file("app/runtime/dispatcher.py", [
        ("resource: str | None = None,",
         "resource: str | None = None,\n        provider_name: str | None = None,"),
        ("provider = runtime_registry.get_provider(capability)",
         "provider = runtime_registry.get_provider(capability, provider_name)")
    ])

    # 5. Update RuntimeService
    modify_file("app/runtime/service.py", [
        ("resource: str | None = None, *args, **kwargs):",
         "resource: str | None = None, provider_name: str | None = None, *args, **kwargs):"),
        ("dispatch(capability, session, action, resource, *args, **kwargs)",
         "dispatch(capability, session, action, resource, provider_name, *args, **kwargs)")
    ])

    # 6. Update Executor
    modify_file("app/executor/service.py", [
        ("def execute(\n        self,\n        plan: Plan,\n    ) -> ToolResult:",
         "def execute(\n        self,\n        plan: Plan,\n        execution=None,\n    ) -> ToolResult:"),
        ("result = tool_registry.execute(call)",
         """from app.runtime.service import runtime_service
                from app.capabilities.models import CapabilityType
                from app.runtime.models import SecurityAction
                
                # Determine capability
                def get_cap(name):
                    n = name.lower()
                    if "file" in n or "dir" in n: return CapabilityType.FILESYSTEM
                    if "terminal" in n or "shell" in n: return CapabilityType.TERMINAL
                    if "python" in n: return CapabilityType.PYTHON_RUNTIME
                    if "browser" in n or "search" in n: return CapabilityType.BROWSER
                    if "memory" in n: return CapabilityType.MEMORY
                    return CapabilityType.TOOL_USAGE
                
                cap = get_cap(call.name)
                session = execution.runtime_session if execution else runtime_service.create_session()
                
                rt_result = runtime_service.execute_capability(
                    capability=cap,
                    session=session,
                    action=SecurityAction.EXECUTE,
                    resource=call.name,
                    provider_name=call.name,
                    call_args=call.arguments
                )
                
                if execution:
                    if cap not in execution.active_capabilities:
                        execution.active_capabilities.append(cap)
                    execution.executed_capabilities.append(cap)
                    execution.runtime_results[call.name] = rt_result
                
                result = ToolResult(
                    success=rt_result.success,
                    output=rt_result.output if rt_result.success else str(rt_result.error),
                    metadata=rt_result.metadata
                )"""
        )
    ])

    # 7. Update MissionPipeline
    modify_file("app/mission/pipeline.py", [
        ("self.route(\n            mission,\n            execution,\n        )",
         """from app.runtime.service import runtime_service
        execution.runtime_session = runtime_service.create_session()
        
        self.route(
            mission,
            execution,
        )"""),
        ("        if not plan.use_tool:\n            return None",
         """        if not plan.use_tool:
            if execution.runtime_session:
                from app.runtime.service import runtime_service
                runtime_service.cleanup_session(execution.runtime_session)
                execution.runtime_session = None
            return None"""),
        ("        return result",
         """        if execution.runtime_session:
            from app.runtime.service import runtime_service
            runtime_service.cleanup_session(execution.runtime_session)
            execution.runtime_session = None
        return result"""),
        ("return executor.execute(\n            plan,\n        )",
         "return executor.execute(\n            plan,\n            execution,\n        )")
    ])

if __name__ == "__main__":
    main()
