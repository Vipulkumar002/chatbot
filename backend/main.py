
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google.genai.errors import ClientError

from chatbot import get_chatbot_response


app = FastAPI(title="MIPaaS Chatbot API")


# Allow the React frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Validate incoming chat messages.
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


# Home endpoint.
@app.get("/")
def home():
    return {
        "message": "MIPaaS Chatbot API is running"
    }


# Health check endpoint.
@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# Chat endpoint.
@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Please enter a message.",
        )

    try:
        # Get the response from Gemini.
        reply = get_chatbot_response(message)

        return {
            "reply": reply
        }

    except ClientError as exc:
        # Print the original Gemini error in the terminal.
        print(f"Gemini API error: {exc}")

        error_code = getattr(exc, "code", None)
        error_text = str(exc).lower()

        # Handle quota and rate-limit errors.
        if (
            error_code == 429
            or "resource_exhausted" in error_text
            or "quota" in error_text
            or "rate limit" in error_text
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini usage limit reached. "
                    "Please wait until your quota resets "
                    "or check your Gemini API usage limits."
                ),
            ) from exc

        # Handle other Gemini API errors.
        raise HTTPException(
            status_code=502,
            detail=(
                "Gemini could not process your request. "
                "Please try again later."
            ),
        ) from exc

    except Exception as exc:
        # Log unexpected errors for debugging.
        print(f"Unexpected chatbot error: {exc}")

        raise HTTPException(
            status_code=502,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            ),
        ) from exc
