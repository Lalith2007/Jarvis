from app.memory.vault.search import vault_search


results = vault_search.search("ISRO")

print(f"\nFound {len(results)} results\n")

for note in results:
    print(note.path)
