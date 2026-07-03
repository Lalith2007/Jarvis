from app.agents.hermes.context_builder import context_builder
from app.llm.service import llm

context = context_builder.build("North")
messages = llm._build_messages(context)

print()

for message in messages:
    print("=" * 60)
    print(message["role"])
    print("-" * 60)
    print(message["content"][:300])
    print()
