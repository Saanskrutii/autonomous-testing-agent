import ast
import os

def extract_code_structure(file_path: str) -> list[dict]:
    """Parses a Python file using AST and extracts function names, args, and docstrings."""
    with open(file_path, "r") as f:
        code = f.read()

    tree = ast.parse(code)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Extract parameter names
            arg_names = [arg.arg for arg in node.args.args]
            # Extract docstring
            docstring = ast.get_docstring(node) or "No docstring"
            
            functions.append({
                "name": node.name,
                "args": arg_names,
                "docstring": docstring,
                "line_number": node.lineno
            })

    return functions

def analyze_repository(repo_dir: str) -> dict[str, list[dict]]:
    """Scans all Python files in a directory and extracts AST structures."""
    repo_structure = {}
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("test_"):
                full_path = os.path.join(root, file)
                repo_structure[full_path] = extract_code_structure(full_path)
    return repo_structure

# Quick Local Test
if __name__ == "__main__":
    structure = analyze_repository("sample_repo")
    print("--- Extracted Repository AST Structure ---")
    for file, funcs in structure.items():
        print(f"\nFile: {file}")
        for fn in funcs:
            print(f"  - Function: {fn['name']}({', '.join(fn['args'])}) -> Doc: '{fn['docstring']}'")
