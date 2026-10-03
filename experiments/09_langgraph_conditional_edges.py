from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# 1. State
class AgentState(TypedDict):
    repo_name: str
    pass_rate: float
    iteration: int
    status: str

# 2. Nodes
def execute_tests_node(state: AgentState) -> dict:
    current_iter = state["iteration"] + 1
    # Simulate pass rate improving on iteration 2
    simulated_pass_rate = 50.0 if current_iter == 1 else 100.0
    
    print(f"\n  [NODE] Executing pytest (Attempt #{current_iter})... Pass Rate: {simulated_pass_rate}%")
    return {
        "iteration": current_iter,
        "pass_rate": simulated_pass_rate,
        "status": "tested"
    }

def refine_tests_node(state: AgentState) -> dict:
    print(f"  [NODE] Refining broken test cases... (Pass rate was {state['pass_rate']}%)")
    return {"status": "tests_refined"}

def report_node(state: AgentState) -> dict:
    print(f"\n  [NODE] Generating Final Testing Report! (Final Pass Rate: {state['pass_rate']}%)")
    return {"status": "completed"}

# 3. Router Function (Conditional Edge)
def decide_next_step(state: AgentState) -> str:
    if state["pass_rate"] >= 100.0:
        print("  [ROUTER DECISION] All tests passed! Moving to report_node.")
        return "finish"
    elif state["iteration"] >= 3:
        print("  [ROUTER DECISION] Max retries reached! Moving to report_node.")
        return "finish"
    else:
        print("  [ROUTER DECISION] Tests failed. Moving to refine_tests_node!")
        return "refine"

# 4. Build Graph
builder = StateGraph(AgentState)

builder.add_node("execute_tests", execute_tests_node)
builder.add_node("refine_tests", refine_tests_node)
builder.add_node("report", report_node)

# Flow Connections
builder.add_edge(START, "execute_tests")

# Add Conditional Edge from execute_tests
builder.add_conditional_edges(
    "execute_tests",
    decide_next_step,
    {
        "finish": "report",
        "refine": "refine_tests"
    }
)

# Loop edge: refine_tests loops back to execute_tests!
builder.add_edge("refine_tests", "execute_tests")
builder.add_edge("report", END)

# Compile Graph
graph_app = builder.compile()

# 5. Run Graph with failing initial state
initial_state = {
    "repo_name": "TestingDemo",
    "pass_rate": 0.0,
    "iteration": 0,
    "status": "start"
}

print("--- Invoking Conditional Agent Graph Loop ---")
final_state = graph_app.invoke(initial_state)

print("\n--- Final Graph State ---")
print(final_state)
