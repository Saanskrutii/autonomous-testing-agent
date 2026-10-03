import os 

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain unit testing in 2 sentences.",
)

print("--- Model Response ---")
print(response.text)