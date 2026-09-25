import os
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY")
HF_TOKEN=os.getenv("HF_TOKEN")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
# TODO: replace with real logic repo values
EVENT_CHECK_URL=os.getenv("EVENT_CHECK_URL","")
LIVE_STREAM_URL=os.getenv("LIVE_STREAM_URL","")
USE_GEMINI_VIDEO=os.getenv("USE_GEMINI_VIDEO","true").lower()=="true" # 1.5hr direct digest
