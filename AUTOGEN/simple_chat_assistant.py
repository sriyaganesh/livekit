from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env
load_dotenv()

# Get API key
api_key = os.getenv("OPENROUTER_API_KEY")



# Create OpenAI model client
model_client = OpenAIChatCompletionClient(
        base_url="https://openrouter.ai/api/v1/",
        model="mistralai/mistral-small-3.2-24b-instruct",
        api_key=api_key,
        model_info={
            "family": "mistral-small",
            "vision": True,
            "function_calling": True,
            "json_output": False
        }
    )

    # Create Assistant Agent
assistant = AssistantAgent(
        name="My_Assistant",
        model_client=model_client
    )


# Async main function
async def chat(question):
    result = await assistant.run(
        task=question  # ✅ correct usage
    )

    # Print just the final message content
    print("\n")
    print(result.messages[-1].content)

# Run async program
if __name__ == "__main__":
    asyncio.run(chat("Hello, how are you?"))