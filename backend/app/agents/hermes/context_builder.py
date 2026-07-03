from app.agents.hermes.models import PromptContext
from app.llm.prompts.loader import prompt_loader
from app.memory.conversation.service import conversation
from app.memory.vault.service import vault
from app.query.service import query_processor


class ContextBuilder:
    def build(
        self,
        user_query: str,
        tool_results: list[dict] | None = None,
        knowledge_limit: int = 3,
    ) -> PromptContext:

        processed_query = query_processor.process(user_query)

        knowledge = vault.search(
            processed_query,
            limit=knowledge_limit,
        )

        return PromptContext(
            system_prompt=prompt_loader.load("system.md"),
            conversation=conversation.history(),
            knowledge=knowledge,
            tool_results=tool_results or [],
            user_query=user_query,
        )


context_builder = ContextBuilder()
