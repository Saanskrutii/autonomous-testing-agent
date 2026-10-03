import os
from dotenv import load_dotenv

# 1. Import LangChain's Google Gemini model wrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# 2. Initialize the model wrapper
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
)

# 3. Create a list of standard LangChain messages
messages = [
    SystemMessage(content="You are a helpful Python mentor. Keep answers under 20 words."),
    HumanMessage(content="What is LangChain?")
]

# 4. Invoke the model
response = llm.invoke(messages)

# Print the full response object to inspect it
print("--- Type of Response ---")
print(type(response))

print("\n--- Response Content ---")
print(response.content)

print("\n--- Response Metadata ---")
print(response.response_metadata)
