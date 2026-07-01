from app.llm.service import llm
print("=" * 60)
print("Testing GLM 5.1...")
print("=" * 60)

response = llm.chat("Who are you? Reply in one sentence.")

print("\nResponse:\n")
print(response)
