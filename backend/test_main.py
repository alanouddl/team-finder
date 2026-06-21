import time

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# Free-tier Gemini rate limits reject back-to-back calls; pace requests to avoid 429s.
REQUEST_DELAY_SECONDS = 2

TEST_CASES = [
    {
        "problem": "I need help setting up a CI/CD pipeline for our new service",
        "expected": "Khalid",
    },
    {
        "problem": "Our database queries are running very slowly, who can help optimize them?",
        "expected": "Ahmed",
    },
    {
        "problem": "I need to design wireframes for a new mobile feature",
        "expected": "Reem",
    },
    {
        "problem": "I don't understand the business requirements for the client onboarding process",
        "expected": "Lama",
    },
    {
        "problem": "I need to write automated tests for the payment gateway",
        "expected": "Nora",
    },
    {
        "problem": "Something broke in production and I need help debugging the deployment",
        "expected": "Khalid",
    },
    {
        "problem": "I want to add real-time charts to our dashboard, who knows frontend best?",
        "expected": "Sara",
    },
    {
        "problem": "I need help with data extraction and building a report for finance",
        "expected": "Turki",
    },
    {
        "problem": "Who should I talk to about project timelines and managing stakeholder expectations?",
        "expected": "Hessa",
    },
]


def test_find_returns_200_and_recommendation_for_each_case():
    for case in TEST_CASES:
        response = client.post("/find", json={"problem": case["problem"]})
        time.sleep(REQUEST_DELAY_SECONDS)
        assert response.status_code == 200, case["problem"]
        recommendation = response.json()["recommendation"]
        print(f"\nQ: {case['problem']}\nA: {recommendation}\n")
        assert recommendation, case["problem"]
        assert case["expected"] in recommendation, (
            f"Expected '{case['expected']}' in response for '{case['problem']}': {recommendation}"
        )


def test_find_handles_vague_problem_without_crashing():
    response = client.post("/find", json={"problem": "I need help with something but I'm not sure what the problem is yet"})
    assert response.status_code == 200
    recommendation = response.json()["recommendation"]
    assert recommendation


def test_find_rejects_missing_problem_field():
    response = client.post("/find", json={})
    assert response.status_code == 422
