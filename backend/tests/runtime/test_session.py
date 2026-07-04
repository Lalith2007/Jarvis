from app.runtime.session import RuntimeSession
def test_session():
    s = RuntimeSession()
    assert s.id is not None
