from app.memory.memory_service import memory

print("=" * 60)
print("Reading Obsidian Vault...")
print("=" * 60)

content = memory.read("brain/North Star.md")

print(content)
