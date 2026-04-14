from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_core import Image as AGImage
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import MaxMessageTermination


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

termination = MaxMessageTermination(max_messages=5)

# Agents



first_agent = AssistantAgent(
    name="add1_agent_1",
    model_client=model_client,
    system_message="Add 1 to the number. First number is 0. Give result number as output."
)

second_agent = AssistantAgent(
    name="add1_agent_2",
    model_client=model_client,
    system_message="Take the last number mentioned in the conversation and add 1. Give result number as output."
)

third_agent = AssistantAgent(
    name="add1_agent_3",
    model_client=model_client,
    system_message="Take the last number mentioned in the conversation and add 1. Give result number as output."
)



team=RoundRobinGroupChat([first_agent, second_agent, third_agent],
                         # max_turns=3
                         termination_condition=termination
                         )



    
# Async main function
async def main():


    # Console-based streaming of team responses
    print("Console bases responses:")
    # This is to termainate after 5 messages
    await Console(team.run_stream())

    #await Console(team.run_stream(task="First number is 4"))

    # # Resume Team
    # await Console(team.run_stream())
    # await Console(team.run_stream(task="what is the last number you have got in the result?"))

    # # reset team
    # await team.reset()

if __name__ == "__main__":
    asyncio.run(main())

    