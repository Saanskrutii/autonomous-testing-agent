import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

# Define configuration with system instruction, temperature, and JSON output format
config = types.GenerateContentConfig(
    system_instruction="You are a strict QA Automation Engineer. You only output valid JSON.",
    temperature=0.0,
    response_mime_type="application/json",  # Forces JSON response
)

prompt = """
Analyze this function and give me 2 test cases:
def add(a, b):
    return a + b
Return a JSON object with a key 'test_cases' containing a list of objects with 'name' and 'input'.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=config,
)

print("--- Raw JSON Response ---")
print(response.text)
