from app.memory.vault.reader import vault_reader

notes = vault_reader.read_notes()

print(f"\nFound {len(notes)} notes\n")

for note in notes[:10]:
    print(f"{note.path}")
