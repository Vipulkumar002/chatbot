
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(Path(__file__).with_name(".env"))

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=60000)
)

print("Connecting to Gemini...", flush=True)

try:
    response = client.interactions.create(
        model=model,
        input="Reply with: Gemini API connection successful."
    )

    print("\nGemini response:", flush=True)
    print(response.output_text, flush=True)

except Exception as e:
    print("\nGemini request failed:", flush=True)
    print(type(e).__name__, flush=True)
    print(str(e), flush=True)
