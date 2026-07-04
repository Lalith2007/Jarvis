from app.runtime.manager import runtime_manager
from app.runtime.models import RuntimeStatus

def test_session_lifecycle():
    session = runtime_manager.create_session()
    assert session.id is not None
    assert session.status == RuntimeStatus.STARTING
    
    session.opened_resources.append("file.txt")
    
    runtime_manager.cleanup_session(session.id)
    assert len(session.opened_resources) == 0
    assert session.status == RuntimeStatus.CLEANED_UP
    assert runtime_manager.get_session(session.id) is None
