import os
from dotenv import load_dotenv

from livekit.agents import Agent, AgentSession, JobContext, cli, WorkerOptions
from livekit.plugins import openai, silero

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class VoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are a real-time voice assistant.
- Always strictly respond in user's language
- Keep answers short and natural
"""
        )


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = VoiceAgent()

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(
            model="gpt-4o-mini-transcribe",
            api_key=OPENAI_API_KEY,
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
        ),
        tts=openai.TTS(
            model="gpt-4o-mini-tts",
            voice="alloy",
            api_key=OPENAI_API_KEY,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=agent,
    )

    await session.say("Hello! I'm your voice assistant. How can I help you?")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    )

    #cli.run_app()