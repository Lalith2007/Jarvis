from app.memory.vault.indexer import vault_index

vault_index.build()

print(f"Indexed {len(vault_index.all_notes())} notes.")
