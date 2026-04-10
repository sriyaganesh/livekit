import os
import asyncio
import smtplib
import traceback
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

from livekit.agents import Agent, AgentSession, JobContext, cli, WorkerOptions
from livekit.plugins import openai, silero

from web_search import search_web

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_ID = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

print(EMAIL_ID, EMAIL_PASSWORD)


# -----------------------
# TOOL: COLLEGE FETCH
# -----------------------
async def get_top_colleges(query: str, location: str):
    final_query = f"{query} top colleges in {location} fees contact admission details"

    results = search_web(final_query)[:5]

    results_text = "\n\n".join(
        [f"Title: {r['title']}\nSnippet: {r['snippet']}" for r in results]
    )

    prompt = f"""
Return EXACTLY 5 colleges.

STRICT RULES:
- Do NOT hallucinate data
- If info not available → write "Not Available"
- Keep EXACT formatting

FORMAT:

--------------------------------------------------
COLLEGE #1
--------------------------------------------------

🏫 BASIC INFORMATION
- College Name:
- University / Affiliation:
- Accreditation:
- Established Year:

📍 LOCATION DETAILS
- Address:
- City:
- State:
- Country:
- Pincode:

📞 CONTACT DETAILS
- Phone:
- Email:
- Website:

🎓 COURSE DETAILS
- Course Name:
- Degree Type (MBA/B.Tech/etc):
- Duration:
- Specializations:

💰 FEES STRUCTURE
- Total Fees:
- Tuition Fees:
- Hostel Fees:
- Other Charges:

📝 ADMISSION DETAILS
- Entrance Exam:
- Exam Dates:
- Cutoff (if available):
- Application Start Date:
- Application End Date:
- Admission Process:

📊 PLACEMENT & ROI
- Average Package:
- Highest Package:
- Top Recruiters:

🏆 RANKING & REPUTATION
- NIRF Ranking:
- Global Ranking:
- Awards / Recognition:

🌟 HIGHLIGHTS
- Point 1
- Point 2
- Point 3

⚠️ NOTES
- Any important info or disclaimer

--------------------------------------------------

DATA:
{results_text}
"""
    return prompt


# -----------------------
# FILE SAVE
# -----------------------
def save_to_file(content):
    os.makedirs("outputs", exist_ok=True)

    file_name = f"colleges_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_path = os.path.abspath(os.path.join("outputs", file_name))

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


# -----------------------
# EMAIL SEND
# -----------------------

def send_email(to_email, content):
    try:
        print("🚀 EMAIL FUNCTION CALLED")
        print("📩 Sending to:", to_email)

        if not EMAIL_ID or not EMAIL_PASSWORD:
            print("❌ Missing EMAIL credentials")
            return False

        msg = MIMEText(content)
        msg["Subject"] = "Top College Details Report"
        msg["From"] = EMAIL_ID
        msg["To"] = EMAIL_ID   # ✅ FIXED

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            print("🔐 TLS started")

            server.login(EMAIL_ID, EMAIL_PASSWORD)
            print("✅ LOGIN SUCCESS", flush=True)

            server.send_message(msg)
            print("📤 EMAIL SENT SUCCESSFULLY", flush=True)

        return True

    except Exception:
        print("❌ EMAIL ERROR:")
        print(traceback.format_exc())
        return False

# -----------------------
# AGENT
# -----------------------
class VoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are an advanced career guidance voice assistant.

FLOW:
1. Ask India or Abroad
2. Fetch top 5 colleges using strict format
3. Ask delivery mode (Email or File)

RULES:
- Always follow structured format
- Never exceed 5 colleges
"""
        )


# -----------------------
# MAIN ENTRY
# -----------------------
async def entrypoint(ctx: JobContext):
    await ctx.connect()
    print("✅ Connected")

    agent = VoiceAgent()

    session = AgentSession(
        vad=silero.VAD.load(),

        stt=openai.STT(
            model="whisper-1",
            api_key=OPENAI_API_KEY,
        ),

        llm=openai.LLM(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
        ),

        tts=openai.TTS(
            model="tts-1",
            voice="alloy",
            api_key=OPENAI_API_KEY,
        ),
    )

    await session.start(room=ctx.room, agent=agent)

    await session.say("Hello! Ask me about colleges or courses.")

    # STATE
    user_state = "idle"
    saved_query = ""
    final_result = ""

    @session.on("user_speech_committed")
    def handler(msg):
        asyncio.create_task(process(msg))

    async def process(msg):
        nonlocal user_state, saved_query, final_result

        try:
            user_text = msg.text.lower()
            print("USER:", user_text)
            print("STATE:", user_state)

            keywords = ["college", "mba", "engineering", "medical", "university", "course"]

            # -----------------------
            # STEP 1: QUERY DETECTION
            # -----------------------
            if any(k in user_text for k in keywords) and user_state == "idle":
                saved_query = user_text
                user_state = "awaiting_location"
                await session.say("Do you want colleges in India or Abroad?")
                return

            # -----------------------
            # STEP 2: LOCATION
            # -----------------------
            if user_state == "awaiting_location":

                if "india" in user_text:
                    location = "India"
                elif "abroad" in user_text:
                    location = "Abroad"
                else:
                    await session.say("Please say India or Abroad.")
                    return

                user_state = "processing"

                tool_prompt = await get_top_colleges(saved_query, location)

                response = await session.llm.acomplete(
                    messages=[{"role": "user", "content": tool_prompt}],
                    temperature=0
                )

                final_result = response.choices[0].message.content

                await session.say(final_result)

                user_state = "awaiting_delivery"
                await session.say("Do you want this via email or as a file?")
                return

            # -----------------------
            # STEP 3: DELIVERY OPTION
            # -----------------------
            if user_state == "awaiting_delivery":

                if "email" in user_text:
                    user_state = "awaiting_email"
                    await session.say("Please say your email address.")
                    return

                elif "file" in user_text:
                    file_path = save_to_file(final_result)
                    await session.say(f"I have saved your file successfully at {file_path}")
                    user_state = "idle"
                    return

                else:
                    await session.say("Please say email or file.")
                    return

            # -----------------------
            # STEP 4: EMAIL
            # -----------------------
            print(user_state, "user_state")
            if user_state == "awaiting_email":

                email = msg.text.strip()
                print("📩 EMAIL RECEIVED:", email, flush=True)

                if "@" not in email:
                    await session.say("Please provide a valid email address.")
                    return

                print("⚡ Calling send_email...", flush=True)

                success = send_email(email, final_result)

                print("📊 EMAIL RESULT:", success)

                if success:
                    await session.say("Email sent successfully!", flush=True)
                else:
                    await session.say("Email failed. Check logs.", flush=True)

                user_state = "idle"
                return
            # -----------------------
            # FALLBACK
            # -----------------------
            response = await session.llm.acomplete(
                messages=[{"role": "user", "content": user_text}]
            )

            await session.say(response.choices[0].message.content)

        except Exception:
            print("ERROR:", traceback.format_exc())
            await session.say("Something went wrong.")


    await session.say("Assistant is ready.")


# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))