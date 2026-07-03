from app.memory.vault.service import vault
from app.query.service import query_processor


def test_vault_search():

    query = query_processor.process("North")

    results = vault.search(query)

    assert len(results) > 0

    assert results[0].note.title == "North Star"
