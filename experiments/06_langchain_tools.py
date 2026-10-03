import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

load_dotenv()

# 1. Define a tool using the @tool decorator
@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together and returns the exact result."""
    print(f"\n[TOOL CALLED IN PYTHON] multiply({a}, {b})")
    return a * b

# 2. Inspect how LangChain converted the tool to a schema
print("--- Tool Name & Description ---")
print("Name:", multiply.name)
print("Description:", multiply.description)
print("Args Schema:", multiply.args)

# 3. Create model and bind tools
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
llm_with_tools = llm.bind_tools([multiply])

# 4. Invoke model with a prompt requiring math
response = llm_with_tools.invoke("What is 1234 multiplied by 5678?")

print("\n--- AIMessage Output ---")
print("Content:", response.content)
print("Tool Calls:", response.tool_calls)
