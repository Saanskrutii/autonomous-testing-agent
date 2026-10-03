from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# 1. Define the Graph State (Schema)
class AgentState(TypedDict):
    repo_name: str
    files_found: list[str]
    pass_rate: float
    status: str

# 2. Define Node 1: Repo Discovery Node
def discover_repo_node(state: AgentState) -> dict:
    print(f"\n  [NODE 1] Discovering repository: '{state['repo_name']}'...")
    # Return ONLY the keys in state that you want to update
    return {
        "files_found": ["calculator.py", "test_calculator.py"],
        "status": "repo_discovered"
    }

# 3. Define Node 2: Test Execution Node
def execute_tests_node(state: AgentState) -> dict:
    print(f"  [NODE 2] Executing tests on files: {state['files_found']}...")
    return {
        "pass_rate": 100.0,
        "status": "tests_completed"
    }

# 4. Build the Graph
builder = StateGraph(AgentState)

# Add nodes to graph
builder.add_node("discover_repo", discover_repo_node)
builder.add_node("execute_tests", execute_tests_node)

# Add edges (Connect START -> discover_repo -> execute_tests -> END)
builder.add_edge(START, "discover_repo")
builder.add_edge("discover_repo", "execute_tests")
builder.add_edge("execute_tests", END)

# Compile into an executable graph app
graph_app = builder.compile()

# 5. Run the Workflow Graph with an initial state
initial_state = {
    "repo_name": "MyAwesomeProject",
    "files_found": [],
    "pass_rate": 0.0,
    "status": "initialized"
}

print("--- Invoking LangGraph Workflow ---")
final_state = graph_app.invoke(initial_state)

print("\n--- Final Graph State ---")
print(final_state)
