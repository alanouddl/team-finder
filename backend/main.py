import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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


@app.post("/find")
async def find_team_member(request: FindRequest):
    team_json = json.dumps(TEAM_DATA, ensure_ascii=False, indent=2)

    prompt = f"""You are a helpful assistant for a software team. Given a problem or task description, recommend the best team member(s) to handle it.

Here is the team:
{team_json}

Problem: {request.problem}

Respond with a clear recommendation. Name the person (or people) best suited, explain why based on their skills and experience, and note if they are currently available. Keep the response concise and practical."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return {"recommendation": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
