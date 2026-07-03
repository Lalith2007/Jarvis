from app.query.service import query_processor


def test_process_north_star():
    processed = query_processor.process(
        "What is my North Star?"
    )

    assert processed.original == "What is my North Star?"
    assert processed.normalized == "north star"
    assert processed.keywords == [
        "north",
        "star",
    ]


def test_process_h3lix():
    processed = query_processor.process(
        "Tell me about H3LIX"
    )

    assert processed.normalized == "h3lix"


def test_process_isro():
    processed = query_processor.process(
        "Show me ISRO notes"
    )

    assert "isro" in processed.keywords
