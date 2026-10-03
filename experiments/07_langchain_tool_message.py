import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()

# 1. Define Tool
@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together and returns the exact result."""
    print(f"  [PYTHON RUNNING TOOL] multiply({a}, {b})")
    return a * b

# 2. Model & Bind Tools
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
llm_with_tools = llm.bind_tools([multiply])

# 3. Message History (State)
messages = [HumanMessage(content="What is 1234 multiplied by 5678?")]

print("Step 1: Sending HumanMessage to LLM...")
ai_message = llm_with_tools.invoke(messages)
messages.append(ai_message)

print(f"LLM Requested Tool: {ai_message.tool_calls}")

# 4. Execute the tool request manually using Python!
for tool_call in ai_message.tool_calls:
    if tool_call["name"] == "multiply":
        # Execute the tool function
        result = multiply.invoke(tool_call["args"])
        
        # Create a ToolMessage with the result and the matching tool_call_id
        tool_msg = ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        )
        messages.append(tool_msg)

print("\nStep 2: Sending tool result back to LLM...")
final_response = llm_with_tools.invoke(messages)

print("\n--- Final Response ---")
print(final_response.content)
