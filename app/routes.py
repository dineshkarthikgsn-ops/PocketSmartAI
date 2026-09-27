from fastapi import APIRouter
from app.services import get_gemini_response

router = APIRouter()


@router.get("/test-gemini")
def test_gemini():
    result = get_gemini_response(
        "Say hello to PocketSmartAI in one short sentence."
    )
    return {"response": result}


@router.get("/recommend")
def recommend(
    category: str,
    budget: int,
    preference: str
):
    prompt = f"""
You are PocketSmartAI, a helpful budget recommendation assistant.

Category: {category}
Budget: ₹{budget}
Preference: {preference}

Give 5 useful recommendations that fit the budget.
For each recommendation, include:
1. Item
2. Estimated price
3. Short reason

Keep the answer simple and practical.
"""

    result = get_gemini_response(prompt)

    return {
        "category": category,
        "budget": budget,
        "preference": preference,
        "recommendations": result
    }