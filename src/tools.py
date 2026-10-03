import os
import re
import shutil
import subprocess


def save_test_file(test_file_path: str, code_content: str) -> str:
    """Safely saves generated test code to disk, creating directories if needed."""
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    with open(test_file_path, "w") as f:
        f.write(code_content)
    return f"Test file saved successfully at: {test_file_path}"


def prepare_repo_for_import(repo_dir: str) -> None:
    """
    Creates __init__.py files in all subdirectories of a repo so they
    are importable as Python packages (e.g. from uploaded_repo.utils import ...).
    """
    for root, dirs, files in os.walk(repo_dir):
        # Skip hidden dirs and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        init_path = os.path.join(root, '__init__.py')
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                pass  # empty __init__.py is enough


def clone_github_repo(url: str, target_dir: str = "cloned_repo") -> tuple[bool, str]:
    """
    Clones a public GitHub repository using git clone --depth=1.
    Returns (success: bool, message: str).
    """
    url = url.strip().rstrip('/')
    # Normalize: remove trailing .git if present
    if url.endswith('.git'):
        url = url[:-4]

    # Remove existing cloned dir
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    try:
        result = subprocess.run(
            ['git', 'clone', '--depth=1', url, target_dir],
            capture_output=True,
            text=True,
            timeout=90
        )
        if result.returncode == 0:
            # Count Python source files found
            py_files = []
            for root, dirs, files in os.walk(target_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                for f in files:
                    if f.endswith('.py') and not f.startswith('test_'):
                        py_files.append(f)
            return True, f"Repository cloned successfully! Found {len(py_files)} Python source file(s)."
        else:
            err = result.stderr.strip() or result.stdout.strip()
            return False, f"Git clone failed: {err}"
    except subprocess.TimeoutExpired:
        return False, "Clone timed out after 90s. The repository may be too large or unavailable."
    except FileNotFoundError:
        return False, "git is not installed or not in PATH. Please install git and try again."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def run_pytest_suite(test_file_path: str, target_repo: str = "sample_repo", timeout: int = 30) -> dict:
    """
    Executes pytest with coverage on the specified test file.
    Coverage target is dynamic — based on the actual target_repo directory.
    Parses output to compute pass rate and coverage percentage.
    """
    if not os.path.exists(test_file_path):
        return {
            "pass_rate": 0.0,
            "passed": 0,
            "failed": 1,
            "coverage_percentage": 0.0,
            "output": f"Error: File {test_file_path} does not exist."
        }
    try:
        # Dynamic coverage target based on whichever repo is active
        cov_target = target_repo.rstrip('/').rstrip('\\')
        result = subprocess.run(
            ["pytest", test_file_path, f"--cov={cov_target}", "--cov-report=term-missing", "-v"],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = result.stdout + "\n" + result.stderr

        # Parse passed / failed counts
        passed = 0
        failed = 0
        passed_match = re.search(r"(\d+)\s+passed", output)
        if passed_match:
            passed = int(passed_match.group(1))
        failed_match = re.search(r"(\d+)\s+failed", output)
        if failed_match:
            failed = int(failed_match.group(1))
        total = passed + failed
        pass_rate = (passed / total * 100.0) if total > 0 else (100.0 if result.returncode == 0 else 0.0)

        # Parse coverage percentage
        coverage_pct = 0.0
        cov_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        if cov_match:
            coverage_pct = float(cov_match.group(1))

        return {
            "pass_rate": pass_rate,
            "passed": passed,
            "failed": failed,
            "coverage_percentage": coverage_pct,
            "output": output
        }
    except subprocess.TimeoutExpired:
        return {
            "pass_rate": 0.0,
            "passed": 0,
            "failed": 1,
            "coverage_percentage": 0.0,
            "output": f"Execution timed out after {timeout} seconds!"
        }
    except Exception as e:
        return {
            "pass_rate": 0.0,
            "passed": 0,
            "failed": 1,
            "coverage_percentage": 0.0,
            "output": f"Failed to execute pytest: {str(e)}"
        }


# Quick Local Test
if __name__ == "__main__":
    dummy_code = """
def test_sample_pass():
    assert 1 + 1 == 2

def test_sample_fail():
    assert 1 + 1 == 3
"""
    test_path = "tests/test_dummy.py"
    save_test_file(test_path, dummy_code)

    print("--- Running Pytest Suite Tool ---")
    res = run_pytest_suite(test_path)
    print(f"Passed: {res['passed']}")
    print(f"Failed: {res['failed']}")
    print(f"Pass Rate: {res['pass_rate']}%")
    print("\n--- Raw Pytest Terminal Output ---")
    print(res['output'])
