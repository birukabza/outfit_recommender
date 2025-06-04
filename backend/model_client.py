from autogen_ext.models.openai import OpenAIChatCompletionClient


model_client = OpenAIChatCompletionClient(
        model="gpt-4-turbo",
        temperature=0.4,
        max_tokens=1024,
        timeout=30,
)