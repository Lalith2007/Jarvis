import os

path = "/Users/lalithpraveen/Desktop/Jarvis/backend/app/executor/service.py"
with open(path, "r") as f:
    content = f.read()
    
# Replace SecurityAction.EXECUTE with a mapped action
old_exec = "action=SecurityAction.EXECUTE,"
new_exec = """action=SecurityAction.READ if 'read' in call.name or 'list' in call.name or 'search' in call.name else (SecurityAction.WRITE if 'write' in call.name else SecurityAction.EXECUTE),"""

content = content.replace(old_exec, new_exec)
with open(path, "w") as f:
    f.write(content)
