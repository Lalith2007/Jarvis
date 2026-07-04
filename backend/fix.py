import os

BASE_DIR = "/Users/lalithpraveen/Desktop/Jarvis/backend"

def fix():
    # Fix execution models string literal issue
    exec_models_path = os.path.join(BASE_DIR, "app/execution/models.py")
    with open(exec_models_path, "r") as f:
        content = f.read()
    
    content = content.replace("\\n", "\n")
    with open(exec_models_path, "w") as f:
        f.write(content)
        
    # Fix pytest import file mismatch
    os.makedirs(os.path.join(BASE_DIR, "tests/mcp"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "tests/runtime"), exist_ok=True)
    
    with open(os.path.join(BASE_DIR, "tests/mcp/__init__.py"), "w") as f:
        f.write("")
        
    with open(os.path.join(BASE_DIR, "tests/runtime/__init__.py"), "w") as f:
        f.write("")

if __name__ == "__main__":
    fix()
