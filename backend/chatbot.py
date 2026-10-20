
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

load_dotenv(Path(__file__).with_name(".env"))

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=API_KEY)

# Define system instructions cleanly
instructions = """
You are the MIPaaS medical information assistant.
Explain medical information in simple, clear language.
Do not claim to diagnose diseases or prescribe medicines.
Encourage users to consult qualified healthcare professionals.
If a user describes a possible medical emergency, advise
them to seek emergency medical care immediately.
Do not claim to analyze medical images unless an image
analysis system has actually analyzed them.
"""

# Initialize a stateful chat session with system instructions
chat_session = client.chats.create(
    model=MODEL,
    config=GenerateContentConfig(
        system_instruction=instructions,
        temperature=0.7,
    )
)

def get_chatbot_response(message: str) -> str:
    print("Sending request to Gemini...")
    
    # Send the message inside the managed chat session
    response = chat_session.send_message(message)

    print("Gemini responded successfully.")

    return response.text or (
        "Sorry, I couldn't generate a response. Please try again."
    )