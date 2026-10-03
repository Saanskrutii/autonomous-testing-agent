# 🤖 Autonomous Software Testing Agent

An intelligent, self-healing software testing agent built with **LangGraph**, **Gemini**, and **Streamlit**. 

This agent automatically analyzes Python codebases (via AST parsing), generates comprehensive edge-case test plans, writes executable `pytest` code, runs the tests, and **self-heals** by analyzing traceback errors to fix broken tests autonomously until a 100% pass rate is achieved.

## ✨ Features

- **AST Code Analysis**: Dynamically reads and extracts functions, docstrings, and parameters from Python repositories without executing the code.
- **Dynamic Imports**: Automatically handles imports for any uploaded or cloned codebase.
- **GitHub URL Support**: Directly clone and test public GitHub repositories via the UI.
- **LLM Test Generation**: Uses Google's Gemini models to write parametrized, high-coverage `pytest` suites.
- **Self-Healing Loop**: If tests fail, the agent captures the `pytest` traceback and iteratively refines the code to fix assertions or imports.
- **Interactive UI**: A sleek Streamlit dashboard to monitor the agent's thought process, test execution logs, and coverage metrics in real-time.

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Saanskrutii/autonomous-testing-agent.git
cd autonomous-testing-agent
```

### 2. Set up the virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add your Google Gemini API key:
```env
GEMINI_API_KEY="your-google-gemini-api-key"
```

### 5. Run the Application
```bash
streamlit run app.py
```
Navigate to `http://localhost:8501` in your browser.

## 🛠️ Tech Stack
- **Agent Orchestration**: [LangGraph](https://python.langchain.com/docs/langgraph) & [LangChain](https://python.langchain.com/)
- **LLM**: Google Gemini (`gemini-2.5-flash`)
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Testing**: `pytest` & `pytest-cov`

## 💡 How it Works
1. **Analyze Node**: Parses target Python files using Python's built-in `ast` module.
2. **Plan Node**: The LLM reviews the AST and writes a natural language test plan covering normal inputs, edge cases, and exceptions.
3. **Generate Node**: The LLM writes executable `pytest` code based on the plan and dynamic import blocks.
4. **Execute Node**: Runs the test file in a safe subprocess, extracting pass rate and coverage metrics.
5. **Router Node**: If Pass Rate < 100% and Max Iterations (3) are not met, routes to the Refine Node. Otherwise, finishes.
6. **Refine Node**: The LLM analyzes the `pytest` terminal output/traceback and rewrites the test file to fix failures.

---
*Built with ❤️ for Autonomous AI workflows.*
