from app.agents.hermes.context_builder import context_builder


def test_context_builder():

    from app.memory.vault.models import VaultNote, SearchResult
    
    injected = [SearchResult(note=VaultNote(path="/", title="North Star", content=""), score=1, matched_fields=[])]
    context = context_builder.build("North", injected_knowledge=injected)

    assert context.system_prompt != ""

    assert len(context.knowledge) > 0

    assert context.knowledge[0].note.title == "North Star"
