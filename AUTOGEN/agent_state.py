from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_core import Image as AGImage
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination


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



first_agent = AssistantAgent(
    name="my_assistant",
    model_client=model_client,
    system_message="You are a helpful assistant. Answer the question based on the conversation."
)


second_agent = AssistantAgent(
    name="my_second_assistant",
    model_client=model_client,
    system_message="You are a helpful assistant. Answer the question based on the conversation."
)


    
# Async main function
async def main():


    # Console-based streaming of team responses
    print("Console bases responses:")
    # This is to termainate after 5 messages
    response=await first_agent.on_messages(
        messages=[TextMessage(content="Tell me a joke",
                  source="user"
                   
                )], 
                cancellation_token=CancellationToken()
                )
                  
                                
    print("Final response:")
    print(response.chat_message.content)

    state_agent1=await first_agent.save_state()
    print("first agent state:")
    print(state_agent1)

    
    await second_agent.load_state(state_agent1)

    
    state_agent2=await second_agent.save_state()
    print("second_agent state:")
    print(state_agent2)

    
    

if __name__ == "__main__":
    asyncio.run(main())

    