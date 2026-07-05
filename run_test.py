import pytest
import sys
sys.argv = ["pytest", "tests/agent/test_agent.py", "-s", "-v"]
pytest.main()
