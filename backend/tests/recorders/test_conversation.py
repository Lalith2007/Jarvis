from app.recorders.conversation import conversation_recorder


def test_record_conversation():
    conversation_recorder.record(
        "Hello",
        "Hi! I am JARVIS.",
    )

