from app.agents.hermes.context_builder import context_builder


def test_context_builder():

    context = context_builder.build("North")

    assert context.system_prompt != ""

    assert len(context.knowledge) > 0

    assert context.knowledge[0].note.title == "North Star"
