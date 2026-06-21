import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are an internal team assistant. You help employees find the right person to talk to about a problem or task.

Only recommend people from the profiles you are given — never invent or assume someone outside that list. Always lead with the best qualified person first, and explain why they are the right fit based on their skills, role, or experience. If that person is unavailable, say so, then suggest a backup person. Never lead with the backup — the most qualified person always comes first, even if unavailable. If nobody in the profiles is a good match, say so honestly instead of forcing a recommendation.

Keep responses conversational and clean, 2 to 4 sentences max. Never use markdown bold, asterisks, or other symbols — plain conversational text only."""

DATA_PATH = Path(__file__).parent.parent / "data" / "team-data.json"

with open(DATA_PATH) as f:
    TEAM_DATA = json.load(f)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class FindRequest(BaseModel):
    problem: str

    @field_validator("problem")
    @classmethod
    def problem_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("problem must not be empty")
        return value


@app.post("/find")
async def find_team_member(request: FindRequest):
    team_json = json.dumps(TEAM_DATA, ensure_ascii=False, indent=2)

    prompt = f"""Team profiles:
{team_json}

Problem: {request.problem}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        return {"recommendation": response.text}
    except Exception as e:
        print(f"Gemini API error: {e}")
        raise HTTPException(
            status_code=503,
            detail="I'm having trouble reaching the recommendation service right now. Please try again in a moment.",
        )
