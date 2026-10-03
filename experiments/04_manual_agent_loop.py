import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

# 1. Real Python Functions
def list_directory() -> list[str]:
    """Returns a list of filenames in the current workspace directory."""
    print("  [PYTHON EXECUTING TOOL] list_directory()")
    return [f for f in os.listdir(".") if os.path.isfile(f)]

def read_file_content(filename: str) -> str:
    """Reads and returns the contents of a specified file."""
    print(f"  [PYTHON EXECUTING TOOL] read_file_content('{filename}')")
    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

# Map tool names to Python functions
tools_map = {
    "list_directory": list_directory,
    "read_file_content": read_file_content,
}

# 2. Tool Declarations (Tells Gemini what tools exist)
tools = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="list_directory",
            description="Returns a list of filenames in the current workspace directory."
        ),
        types.FunctionDeclaration(
            name="read_file_content",
            description="Reads and returns the contents of a specified file.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "filename": types.Schema(type="STRING", description="The path to the file to read")
                },
                required=["filename"]
            )
        )
    ])
]

# 3. Agent State (Message History)
user_goal = "List the files in the directory, read '01_raw_llm.py', and give me a 1-sentence summary of what it does."
contents = [user_goal]

print(f"Goal: {user_goal}\n")
print("--- Starting Manual Agent Loop ---")

# 4. Agent Loop with Guardrails
max_iterations = 5
iteration = 0

while iteration < max_iterations:
    iteration += 1
    print(f"\n[Iteration {iteration}] Sending state to Gemini...")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(tools=tools)
    )

    # CASE A: Gemini decided to call a tool
    if response.function_calls:
        # Save model's tool decision into state
        contents.append(response.candidates[0].content)
        
        for call in response.function_calls:
            print(f"  [LLM DECISION] Requesting Tool: '{call.name}' with args: {call.args}")
            
            # Execute Python function locally
            func = tools_map[call.name]
            result = func(**call.args)
            
            print(f"  [OBSERVATION] Tool returned {len(str(result))} characters.")
            
            # Append Observation back into state
            contents.append(types.Part.from_function_response(
                name=call.name,
                response={"result": result}
            ))

    # CASE B: Gemini generated final text (Goal Achieved!)
    elif response.text:
        print("\n✅ AGENT FINISHED ITS GOAL!")
        print("Final Answer:")
        print(response.text)
        break

    # Small pause to respect free-tier rate limits
    time.sleep(1)
