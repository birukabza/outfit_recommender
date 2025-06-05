from autogen_ext.models.openai import OpenAIChatCompletionClient
import os

model_client = OpenAIChatCompletionClient(
    model="gpt-4-turbo",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.4,
    max_tokens=1024,
    timeout=30,
)
