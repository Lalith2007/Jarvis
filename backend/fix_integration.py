import os

BASE_DIR = "/Users/lalithpraveen/Desktop/Jarvis/backend"

# Fix executor SecurityAction
exec_path = os.path.join(BASE_DIR, "app/executor/service.py")
with open(exec_path, "r") as f:
    content = f.read()

content = content.replace("action=SecurityAction.EXECUTE,", "action=SecurityAction.READ if 'read' in call.name or 'list' in call.name or 'search' in call.name else (SecurityAction.WRITE if 'write' in call.name else SecurityAction.EXECUTE),")

with open(exec_path, "w") as f:
    f.write(content)


# Fix test_dispatch_success
test_path = os.path.join(BASE_DIR, "tests/runtime/test_dispatcher.py")
with open(test_path, "r") as f:
    content = f.read()
    
content = content.replace(
    "result = runtime_dispatcher.dispatch(CapabilityType.FILESYSTEM, session, SecurityAction.READ)",
    "result = runtime_dispatcher.dispatch(CapabilityType.FILESYSTEM, session, SecurityAction.READ, provider_name='TestFS')"
)

with open(test_path, "w") as f:
    f.write(content)
