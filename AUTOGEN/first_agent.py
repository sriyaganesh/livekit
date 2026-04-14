from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_core import Image as AGImage

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



def get_weather(city:str) -> str:
    return f"The weather in {city} is sunny with a high of 25°C and a low of 15°C."


# Create OpenAI model client
model_client = OpenAIChatCompletionClient(
        api_key=api_key,
        model="gpt-4o-mini"   # ✅ using mini model
    )

    # Create Assistant Agent
assistant = AssistantAgent(
        name="My_Assistant",
        model_client=model_client,
        description="You are a weather assistant",
        system_message="You are a helpful weather assistant, uses the weather tool to find the weather for any city. Always use the tool to get accurate weather information.",
        tools=[get_weather]
    )

img_assistant = AssistantAgent(
        name="My_Assistant",
        model_client=model_client,
        description="You are an image assistant",
        system_message="You are a helpful Assistant. Analyze    the image and provide a detailed description of the image. and answer the question related to the image."
        
    )


async def image_task():
    await asyncio.sleep(2)   # waits for 2 seconds
    response = requests.get("https://picsum.photos/seed/picsum/200/300")
    image=Image.open(BytesIO(response.content))
    ag_image=   AGImage.from_pil(image)
    multi_modal_message = MultiModalMessage(content=["What is the image about?", ag_image] , source="user")
    result = await img_assistant.run(
        task=multi_modal_message
    )
    print("\n")
    print("Calling via image message")      
    print(result.messages[-1].content)



async def text_task():
    await asyncio.sleep(2)   # waits for 2 seconds
    text_message = TextMessage(content="What is the weather in Chennai?", source="user")
    result = await assistant.run(
        task=text_message
    )
    print("\n")
    print("Calling via tesxt message")
    print(result.messages[-1].content)


# Async main function
async def main():

    
    result = await assistant.run(
        task="What is the weather in chennai?"   # ✅ correct usage
    )

    print("\n")
    print(result.messages[-1].content)
    
    await asyncio.gather(text_task(), image_task())


    # Print full response
    # print("Full Response:", result)

    # Print just the final message content
   

# Run async program
if __name__ == "__main__":
    asyncio.run(main())

    # Agen Cutomization and Prompt engineering