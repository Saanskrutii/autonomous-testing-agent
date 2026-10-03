import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from src.state import TestingAgentState
from src.nodes import (
    analyze_node,
    plan_node,
    generate_node,
    execute_node,
    refine_node,
    report_node
)

load_dotenv()

# 1. Router Function (Conditional Edge)
def should_refine_or_finish(state: TestingAgentState) -> str:
    pass_rate = state.get("pass_rate", 0.0)
    iteration = state.get("iteration", 0)

    if pass_rate >= 100.0:
        print("\n✨ [ROUTER] 100% Pass Rate Achieved! Moving to final report.")
        return "finish"
    elif iteration >= 3:
        print(f"\n⚠️ [ROUTER] Max retries ({iteration}) reached. Stopping loop and generating report.")
        return "finish"
    else:
        print(f"\n🔄 [ROUTER] Pass rate is {pass_rate}%. Retrying and refining tests...")
        return "refine"


# 2. Build the LangGraph Workflow
builder = StateGraph(TestingAgentState)

# Add Nodes
builder.add_node("analyze", analyze_node)
builder.add_node("plan", plan_node)
builder.add_node("generate", generate_node)
builder.add_node("execute", execute_node)
builder.add_node("refine", refine_node)
builder.add_node("report", report_node)

# Flow Edges
builder.add_edge(START, "analyze")
builder.add_edge("analyze", "plan")
builder.add_edge("plan", "generate")
builder.add_edge("generate", "execute")

# Conditional Edge from execute
builder.add_conditional_edges(
    "execute",
    should_refine_or_finish,
    {
        "finish": "report",
        "refine": "refine"
    }
)

# Refine loops back to execute!
builder.add_edge("refine", "execute")
builder.add_edge("report", END)

# Compile Executable Graph
testing_agent_app = builder.compile()


# 3. Main CLI Entrypoint
def run_agent(repo_directory: str = "sample_repo"):
    print("==================================================")
    print("🤖 AUTONOMOUS SOFTWARE TESTING AGENT STARTING")
    print(f" Target Repository: {repo_directory}")
    print("==================================================")

    initial_state = {
        "repo_path": repo_directory,
        "repo_structure": {},
        "test_plan": [],
        "generated_test_code": "",
        "test_file_path": "",
        "test_output": "",
        "pass_rate": 0.0,
        "failed_tests": [],
        "coverage_percentage": 0.0,
        "iteration": 0,
        "status": "started"
    }

    final_state = testing_agent_app.invoke(initial_state)
    return final_state


if __name__ == "__main__":
    run_agent("sample_repo")
