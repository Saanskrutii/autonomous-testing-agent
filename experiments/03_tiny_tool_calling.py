import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

# 1. Define real Python functions (tools)
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together and returns the exact result."""
    print(f"\n[TOOL EXECUTION] Running multiply({a}, {b}) in Python...")
    return a * b

# 2. Pass the function to the model in the tools list
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is 98765 multiplied by 43210?",
    config={"tools": [multiply]},  # Registering our tool!
)

# 3. Check what the model returned
print("--- Model Output ---")
for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.function_call:
            print(f"Tool Requested: {part.function_call.name}")
            print(f"Arguments: {part.function_call.args}")
        elif part.text:
            print(f"Text Response: {part.text}")
