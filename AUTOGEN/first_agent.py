from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")


# Async main function
async def main():

# Create OpenAI model client
    model_client = OpenAIChatCompletionClient(
        api_key=api_key,
        model="gpt-4o-mini"   # ✅ using mini model
    )

    # Create Assistant Agent
    assistant = AssistantAgent(
        name="My_Assistant",
        model_client=model_client
    )

    result = await assistant.run(
        task="What is the capital of France?"   # ✅ correct usage
    )


    # Print full response
    print("Full Response:", result)

    # Print just the final message content
    print("\n")
    print(result.messages[-1].content)

# Run async program
if __name__ == "__main__":
    asyncio.run(main())