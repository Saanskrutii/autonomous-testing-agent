import os
import re
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.state import TestingAgentState
from src.code_analyzer import analyze_repository
from src.tools import save_test_file, run_pytest_suite, prepare_repo_for_import

# 1. Load .env into system environment
load_dotenv()

# Factory: always reads the key and model fresh from environment at call time
def get_llm():
    load_dotenv(override=True)  # re-read .env in case it changed
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # only model available on this key
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.0,
        max_retries=0  # disable internal retries; our wrapper controls all retrying
    )


def llm_invoke_with_retry(messages, max_attempts: int = 8, base_wait: int = 15):
    """
    Wraps LLM invoke with exponential backoff for 503/429 errors.
    max_retries=0 on the LLM ensures this wrapper has full control.
    """
    for attempt in range(max_attempts):
        try:
            return get_llm().invoke(messages)
        except Exception as e:
            err_str = str(e).lower()
            is_transient = any(x in err_str for x in ["503", "unavailable", "429", "resource_exhausted", "overloaded"])
            if is_transient and attempt < max_attempts - 1:
                wait = base_wait * (2 ** attempt)  # 8s, 16s, 32s, 64s...
                print(f"  ⚠️  Model busy (attempt {attempt + 1}/{max_attempts}). Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


# Helper function to extract ONLY valid python code blocks
def clean_code_block(text) -> str:
    if isinstance(text, list):
        parts = []
        for part in text:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
        text = "\n".join(parts)

    text = str(text)

    # Extract ONLY code between ```python and ``` if present
    code_match = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    text = re.sub(r"^```python\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def build_import_block(repo_structure: dict) -> str:
    """
    Converts repo AST file paths into Python import statements dynamically.
    e.g. 'uploaded_repo/utils.py' → 'from uploaded_repo.utils import func1, func2'
    """
    lines = []
    for file_path, functions in repo_structure.items():
        if not functions:
            continue
        try:
            rel = os.path.relpath(file_path)
            module = rel.replace(os.sep, '.').replace('/', '.').replace('.py', '')
            # Skip test files, __init__, __pycache__
            if any(x in module for x in ['test_', '__init__', '__pycache__', '.git']):
                continue
            func_names = [f['name'] for f in functions if not f['name'].startswith('_')]
            if func_names:
                lines.append(f"from {module} import {', '.join(func_names)}")
        except Exception:
            continue
    return '\n'.join(lines) if lines else "# No importable functions found"


# Node 1: Analyze Repository using AST
def analyze_node(state: TestingAgentState) -> dict:
    print("\n🔍 [NODE 1: ANALYZING REPOSITORY]")
    repo_path = state.get("repo_path", "sample_repo")
    structure = analyze_repository(repo_path)
    return {
        "repo_structure": structure,
        "status": "analyzed",
        "iteration": 0
    }


# Node 2: Plan Test Cases
def plan_node(state: TestingAgentState) -> dict:
    print("\n📋 [NODE 2: PLANNING TEST CASES]")
    structure_str = str(state["repo_structure"])

    prompt = f"""
    You are an expert QA Automation Lead.
    Analyze this repository AST structure:
    {structure_str}

    Create a test plan covering:
    1. Normal inputs
    2. Edge cases (zero values, negative numbers, boundary values)
    3. Exception testing (e.g. ValueError, TypeError)

    Return a concise summary list of test cases to generate.
    """

    response = llm_invoke_with_retry([HumanMessage(content=prompt)])
    print("  [PLAN GENERATED]")
    time.sleep(2)
    return {
        "test_plan": [{"plan": response.content}],
        "status": "planned"
    }


# Node 3: Generate Pytest Code
def generate_node(state: TestingAgentState) -> dict:
    print("\n✍️ [NODE 3: GENERATING PYTEST CODE]")
    structure_str = str(state["repo_structure"])
    plan_str = str(state["test_plan"])
    import_block = build_import_block(state["repo_structure"])

    prompt = f"""
    You are a Senior Python QA Engineer. Write a complete, runnable pytest file.

    Target Code AST Structure:
    {structure_str}

    Test Plan:
    {plan_str}

    STRICT RULES:
    1. Use EXACTLY these import statements (auto-detected from the repo — do NOT change them):
{import_block}
    2. Write clear `def test_...():` functions with assertions.
    3. Test normal cases, edge cases, and exception cases (pytest.raises).
    4. Output ONLY valid, executable Python code. Do not wrap in conversational text.
    """

    response = llm_invoke_with_retry([HumanMessage(content=prompt)])
    clean_code = clean_code_block(response.content)

    test_path = "tests/test_generated.py"
    save_test_file(test_path, clean_code)
    print(f"  [TEST CODE SAVED AT {test_path}]")
    time.sleep(2)
    return {
        "generated_test_code": clean_code,
        "test_file_path": test_path,
        "status": "generated"
    }


# Node 4: Execute Pytest Suite
def execute_node(state: TestingAgentState) -> dict:
    current_iter = state.get("iteration", 0) + 1
    print(f"\n🧪 [NODE 4: EXECUTING PYTEST (Iteration #{current_iter})]")

    results = run_pytest_suite(state["test_file_path"], target_repo=state.get("repo_path", "sample_repo"))
    print(f"  [RESULT] Passed: {results['passed']} | Failed: {results['failed']} | Pass Rate: {results['pass_rate']}% | Coverage: {results['coverage_percentage']}%")

    return {
        "pass_rate": results["pass_rate"],
        "coverage_percentage": results["coverage_percentage"],
        "test_output": results["output"],
        "iteration": current_iter,
        "status": "executed"
    }


# Node 5: Refine Broken Tests
def refine_node(state: TestingAgentState) -> dict:
    print(f"\n🔧 [NODE 5: REFINING BROKEN TESTS]")
    import_block = build_import_block(state["repo_structure"])

    prompt = f"""
    The generated pytest suite encountered failures!

    Current Test Code:
    {state['generated_test_code']}

    Pytest Failure Output Traceback:
    {state['test_output']}

    CORRECT IMPORT STATEMENTS (use these exactly, do NOT change them):
{import_block}

    TASK:
    Analyze the traceback error and fix the broken test functions or assertions.
    Output ONLY the corrected, complete Python pytest code without conversational text.
    """

    response = llm_invoke_with_retry([HumanMessage(content=prompt)])
    clean_code = clean_code_block(response.content)

    save_test_file(state["test_file_path"], clean_code)
    print("  [CORRECTED TEST CODE SAVED]")

    time.sleep(2)
    return {
        "generated_test_code": clean_code,
        "status": "refined"
    }


# Node 6: Final Summary Report
def report_node(state: TestingAgentState) -> dict:
    print("\n📊 [NODE 6: GENERATING FINAL REPORT]")
    print("==================================================")
    print(f" Repository Analyzed: {state.get('repo_path')}")
    print(f" Final Pass Rate:     {state.get('pass_rate')}%")
    print(f" Code Coverage:       {state.get('coverage_percentage')}%")
    print(f" Total Iterations:    {state.get('iteration')}")
    print(f" Test File Location:  {state.get('test_file_path')}")
    print("==================================================")
    return {"status": "completed"}
