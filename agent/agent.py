import os
import asyncio
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import datetime

from livekit.agents import Agent, AgentSession, JobContext, cli, WorkerOptions
from livekit.plugins import openai, silero

from agent.web_search import search_web

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("TO_EMAIL")


# -----------------------
# EMAIL FUNCTION
# -----------------------
def send_email(content):
    try:
        msg = MIMEText(content)
        msg["Subject"] = "Top 5 College Details"
        msg["From"] = EMAIL_USER
        msg["To"] = TO_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        return "✅ Email sent successfully"
    except Exception as e:
        print("Email error:", e)
        return "❌ Failed to send email"


# -----------------------
# FILE EXPORT FUNCTION
# -----------------------
def save_to_file(content):
    try:
        filename = f"college_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return f"✅ File saved as {filename}"
    except Exception as e:
        print("File error:", e)
        return "❌ Failed to save file"


# -----------------------
# TRIM STRICTLY 5
# -----------------------
def trim_to_top5(text):
    sections = text.strip().split("\n\n")
    return "\n\n".join(sections[:5])


# -----------------------
# AGENT
# -----------------------
class VoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are a structured career assistant.

Rules:
- Always give structured output
- Never exceed 5 items
- Keep responses precise and factual
"""
        )


# -----------------------
# MAIN
# -----------------------
async def entrypoint(ctx: JobContext):
    await ctx.connect()
    print("✅ Connected to LiveKit")

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

    await session.start(room=ctx.room, agent=agent)

    await session.say("Hello! Ask me about colleges or courses.")

    # STATE VARIABLES
    user_state = "idle"
    selected_query = ""
    last_results = ""

    # -----------------------
    # EVENT HANDLER
    # -----------------------
    @session.on("user_speech_committed")
    def handle(msg):
        asyncio.create_task(process_user(msg))

    # -----------------------
    # CORE LOGIC
    # -----------------------
    async def process_user(msg):
        nonlocal user_state, selected_query, last_results

        user_text = msg.text.lower().strip()
        print("User:", user_text)

        try:

            # -----------------------
            # STEP 1: USER ASK
            # -----------------------
            if ("college" in user_text or "course" in user_text) and user_state == "idle":
                selected_query = user_text
                user_state = "awaiting_location"

                await session.say("Do you want colleges in India or abroad?")

            # -----------------------
            # STEP 2: LOCATION
            # -----------------------
            elif user_state == "awaiting_location":

                if "india" in user_text:
                    final_query = f"{selected_query} top colleges in India"
                elif "abroad" in user_text:
                    final_query = f"{selected_query} top colleges abroad"
                else:
                    await session.say("Please say India or Abroad.")
                    return

                user_state = "results_generated"

                # 🔍 SEARCH TOP 5
                results = search_web(final_query)[:5]

                results_text = "\n\n".join(
                    [
                        f"Title: {r['title']}\nSnippet: {r['snippet']}"
                        for r in results
                    ]
                )

                # 🎯 STRICT PROMPT
                prompt = f"""
You are an expert career advisor.

STRICT RULES:
- Provide EXACTLY 5 colleges
- No extra text before or after

FORMAT:

1. Name:
   Location:
   Fees:
   Entrance Exams:
   Application Dates:
   Highlights:
   - point
   - point
   Website:

Use only relevant data.

Search Data:
{results_text}
"""

                response = await session.llm.acomplete(
                    messages=[{"role": "user", "content": prompt}]
                )

                reply = response.choices[0].message.content
                reply = trim_to_top5(reply)

                last_results = reply

                print("\n===== RESULTS =====\n", reply)

                await session.say(
                    "I found top 5 colleges. Would you like me to send email or save as document?"
                )

            # -----------------------
            # STEP 3: EMAIL
            # -----------------------
            elif user_state == "results_generated" and user_text in ["email", "send email", "mail"]:
                status = send_email(last_results)
                await session.say(status)

            # -----------------------
            # STEP 4: FILE DOWNLOAD
            # -----------------------
            elif user_state == "results_generated" and user_text in ["document", "file", "save"]:
                status = save_to_file(last_results)
                await session.say(status)

            # -----------------------
            # FALLBACK CHAT
            # -----------------------
            else:
                response = await session.llm.acomplete(
                    messages=[{"role": "user", "content": user_text}]
                )

                reply = response.choices[0].message.content
                await session.say(reply)

        except Exception as e:
            print("❌ Error:", e)
            await session.say("Something went wrong.")

    await session.say("Assistant is ready.")


# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))