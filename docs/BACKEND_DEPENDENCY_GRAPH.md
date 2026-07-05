# Backend Dependency Graph

```text
app.artifacts.builders -> {'app.artifacts.models'}
app.tools.registry -> {'app.runtime.registry', 'app.tools.base', 'app.runtime.models', 'app.tools.models', 'app.capabilities.models'}
app.tools.__init__ -> {'app.tools.filesystem.list_directory', 'app.tools.filesystem.write_file', 'app.tools.filesystem.search_files', 'app.tools.registry', 'app.tools.filesystem.read_file'}
app.tools.base -> {'app.tools.models'}
app.tools.filesystem.search_files -> {'app.tools.models', 'app.tools.base', 'app.security.permissions'}
app.tools.filesystem.read_file -> {'app.tools.models', 'app.tools.base', 'app.security.permissions'}
app.tools.filesystem.write_file -> {'app.tools.models', 'app.tools.base', 'app.security.permissions'}
app.tools.filesystem.list_directory -> {'app.tools.models', 'app.tools.base'}
app.llm.service -> {'app.platform.publisher', 'app.llm.orchestrator', 'app.athena.router', 'app.agents.hermes.models', 'app.llm.builder'}
app.llm.provider -> {'app.config.settings'}
app.llm.builder -> {'app.agents.hermes.models'}
app.llm.orchestrator -> {'app.llm.provider', 'app.athena.models'}
app.capabilities.service -> {'app.capabilities.manager', 'app.execution.models', 'app.mission.models', 'app.capabilities.models', 'app.capabilities.registry'}
app.capabilities.registry -> {'app.capabilities.models'}
app.capabilities.analyzer -> {'app.execution.models', 'app.mission.models', 'app.capabilities.models'}
app.capabilities.__init__ -> {'app.capabilities.service', 'app.capabilities.models'}
app.capabilities.manager -> {'app.execution.models', 'app.capabilities.registry', 'app.mission.models', 'app.capabilities.models', 'app.capabilities.analyzer', 'app.platform.publisher'}
app.memory.service -> {'app.memory.vault.service', 'app.memory.conversation.service', 'app.query.models', 'app.platform.publisher'}
app.memory.memory_service -> {'app.memory.service'}
app.memory.vault.service -> {'app.memory.vault.indexer', 'app.query.models', 'app.memory.vault.search', 'app.memory.vault.models'}
app.memory.vault.reader -> {'app.memory.vault.models', 'app.config.settings'}
app.memory.vault.indexer -> {'app.memory.vault.models', 'app.memory.vault.reader'}
app.memory.vault.search -> {'app.memory.vault.indexer', 'app.query.models', 'app.memory.vault.models'}
app.memory.conversation.service -> {'app.memory.conversation.models'}
app.security.permissions -> {'app.config.settings'}
app.planner.service -> {'app.planner.models', 'app.platform.publisher'}
app.providers.registry -> {'app.providers.models'}
app.providers.selector -> {'app.providers.registry', 'app.providers.models'}
app.providers.policy -> {'app.providers.models'}
app.providers.__init__ -> {'app.providers.policy', 'app.providers.selector', 'app.providers.registry'}
app.platform.subscriber -> {'app.platform.models'}
app.platform.observability -> {'app.platform.publisher'}
app.platform.event_bus -> {'app.platform.models', 'app.platform.subscriber'}
app.platform.publisher -> {'app.platform.models', 'app.platform.event_bus'}
app.runtime.dispatcher -> {'app.runtime.registry', 'app.runtime.models', 'app.runtime.executor', 'app.runtime.session', 'app.capabilities.models', 'app.runtime.security'}
app.runtime.service -> {'app.runtime.models', 'app.runtime.dispatcher', 'app.runtime.manager', 'app.runtime.session', 'app.capabilities.models', 'app.platform.publisher'}
app.runtime.models -> {'app.capabilities.models'}
app.runtime.registry -> {'app.capabilities.models'}
app.runtime.security -> {'app.runtime.models', 'app.capabilities.models'}
app.runtime.session -> {'app.runtime.models'}
app.runtime.__init__ -> {'app.runtime.service'}
app.runtime.result -> {'app.runtime.models'}
app.runtime.manager -> {'app.runtime.models', 'app.platform.publisher', 'app.runtime.session'}
app.runtime.executor -> {'app.runtime.models'}
app.agents.hermes.service -> {'app.formatters.markdown', 'app.agents.hermes.context', 'app.agents.hermes.context_builder', 'app.llm.service', 'app.mission.context', 'app.memory.conversation.service', 'app.agent.service', 'app.platform.observability', 'app.storage.service', 'app.platform.publisher'}
app.agents.hermes.models -> {'app.memory.vault.models'}
app.agents.hermes.context_builder -> {'app.llm.prompts.loader', 'app.runtime.manager', 'app.memory.vault.service', 'app.memory.conversation.service', 'app.agents.hermes.models', 'app.capabilities.registry', 'app.platform.publisher', 'app.query.service'}
app.agents.hermes.context -> {'app.agents.hermes.models'}
app.agent.service -> {'app.agent.models', 'app.mission.controller'}
app.agent.models -> {'app.tools.models'}
app.mcp.transport -> {'app.mcp.models'}
app.mcp.registry -> {'app.mcp.models'}
app.mcp.protocol -> {'app.mcp.models'}
app.mcp.client -> {'app.mcp.models', 'app.mcp.transport', 'app.mcp.protocol'}
app.mcp.manager -> {'app.mcp.client', 'app.mcp.registry', 'app.mcp.models', 'app.platform.publisher'}
app.storage.service -> {'app.storage.models', 'app.config.settings'}
app.recorders.conversation -> {'app.storage.service', 'app.storage.models'}
app.mission.service -> {'app.mission.models'}
app.mission.controller -> {'app.mission.pipeline', 'app.execution.manager', 'app.mission.service', 'app.execution.models', 'app.tools.models', 'app.mission.models', 'app.platform.publisher'}
app.mission.__init__ -> {'app.mission.pipeline', 'app.mission.state', 'app.mission.events', 'app.mission.service', 'app.mission.controller'}
app.mission.context -> {'app.execution.models', 'app.agents.hermes.models', 'app.mission.models'}
app.mission.pipeline -> {'app.executor.service', 'app.capabilities.service', 'app.mission.service', 'app.execution.manager', 'app.execution.models', 'app.llm.prompts.loader', 'app.mission.context', 'app.tools.models', 'app.athena.router', 'app.planner.service', 'app.agents.hermes.models', 'app.mission.models', 'app.platform.observability', 'app.runtime.service', 'app.platform.publisher'}
app.mission.state -> {'app.mission.models'}
app.system.service -> {'app.system.models'}
app.system.routes -> {'app.system.service', 'app.system.models', 'app.athena.registry'}
app.execution.models -> {'app.capabilities.models'}
app.execution.context -> {'app.execution.models'}
app.execution.manager -> {'app.execution.models', 'app.execution.context', 'app.execution.state'}
app.execution.state -> {'app.execution.models'}
app.api.routes -> {'app.api.endpoints.intelligence', 'app.api.endpoints.platform_ws', 'app.models.chat', 'app.system.routes', 'app.agents.hermes.service', 'app.api.endpoints.mcp', 'app.api.endpoints.dashboard', 'app.api.endpoints.missions', 'app.api.endpoints.capabilities', 'app.api.endpoints.runtime', 'app.platform.publisher'}
app.api.endpoints.platform_ws -> {'app.platform.models', 'app.platform.event_bus', 'app.platform.subscriber'}
app.api.endpoints.missions -> {'app.mission.controller', 'app.mission.models', 'app.mission.service'}
app.api.endpoints.runtime -> {'app.runtime.manager', 'app.runtime.registry'}
app.api.endpoints.dashboard -> {'app.mission.service', 'app.mcp.registry', 'app.runtime.manager', 'app.athena.registry', 'app.system.service', 'app.capabilities.registry'}
app.api.endpoints.mcp -> {'app.mcp.registry'}
app.api.endpoints.capabilities -> {'app.capabilities.registry'}
app.executor.service -> {'app.tools.registry', 'app.runtime.models', 'app.executor.models', 'app.tools.models', 'app.planner.models', 'app.capabilities.models', 'app.runtime.service', 'app.platform.publisher'}
app.executor.models -> {'app.tools.models', 'app.planner.models'}
app.documents.service -> {'app.documents.models', 'app.config.settings'}
app.query.service -> {'app.query.models', 'app.query.stopwords'}
app.athena.intent -> {'app.athena.capabilities', 'app.agents.hermes.models'}
app.athena.task_analyzer -> {'app.agents.hermes.models', 'app.athena.intent', 'app.athena.task_analysis'}
app.athena.registry -> {'app.athena.profiles', 'app.athena.models'}
app.athena.strategy -> {'app.athena.models'}
app.athena.router -> {'app.athena.scorer', 'app.agents.hermes.models', 'app.platform.publisher', 'app.athena.models'}
app.athena.profiles -> {'app.athena.capabilities', 'app.athena.models'}
app.athena.verifier -> {'app.config.settings', 'app.athena.models', 'app.athena.registry'}
app.athena.scorer -> {'app.athena.task_analysis', 'app.athena.intent', 'app.agents.hermes.models', 'app.athena.registry', 'app.athena.task_analyzer', 'app.athena.models'}
```
