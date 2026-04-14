from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_core import Image as AGImage
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.base import TaskResult


from PIL import Image
from io import BytesIO
import requests


from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI model client
model_client = OpenAIChatCompletionClient(
        api_key=api_key,
        model="gpt-4o-mini"   # ✅ using mini model
    )


# Agents


situation_agent = AssistantAgent(
    name="Situation_Agent",
    model_client=model_client,
    system_message="Generate a short story situation."
)

character_agent = AssistantAgent(
    name="Character_Agent",
    model_client=model_client,
    system_message="Create characters based on the situation."
)

ending_agent = AssistantAgent(
    name="Ending_Agent",
    model_client=model_client,
    system_message="Write an ending for the story."
)



team=RoundRobinGroupChat([situation_agent, character_agent, ending_agent], max_turns=3)



    
# Async main function
async def main():
    # Console-based streaming of team responses
    print("Console bases responses:")
    await Console(team.run_stream(task="Write a story about a cat and a dog."))
   
    team_state=await team.save_state()
    print(team_state)

    await team.reset()
    print("reset done")

    await team.load_state(team_state)
    print("reloaded state")

    stream=team.run_stream(task="what was the last line of story you wrote?")
    await Console(stream)

# Run async program
if __name__ == "__main__":
    asyncio.run(main())

    # Agen Cutomization and Prompt engineering