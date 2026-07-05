import ast
import os
from collections import defaultdict

def analyze_backend(base_path):
    imports = defaultdict(list)
    for root, _, files in os.walk(base_path):
        for file in files:
            if not file.endswith('.py'):
                continue
            filepath = os.path.join(root, file)
            module_name = filepath.replace(base_path, 'app').replace('/', '.').replace('.py', '')
            try:
                with open(filepath, 'r') as f:
                    tree = ast.parse(f.read(), filename=filepath)
            except Exception:
                continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('app.'):
                            imports[module_name].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith('app.'):
                        imports[module_name].append(node.module)
    return imports

imports = analyze_backend('/Users/lalithpraveen/Desktop/Jarvis/backend/app/')
for mod, deps in imports.items():
    print(f"{mod} -> {set(deps)}")

