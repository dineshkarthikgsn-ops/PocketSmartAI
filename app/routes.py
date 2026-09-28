from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Header
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.services import get_gemini_response, client
from app.config import JWT_SECRET_KEY
from app.auth import register_user, login_user, save_history, DATABASE

router = APIRouter()

ALGORITHM = "HS256"


def get_current_user(authorization: str):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return username

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


MOCK_PLATFORMS = {
    "Home Decoration": ["Amazon", "Flipkart", "IKEA"],
    "Party Planning": ["Swiggy", "Zomato", "OYO"],
    "Jewellery": ["Amazon", "Flipkart"]
}


@router.get("/test-gemini")
def test_gemini():
    result = get_gemini_response(
        "Say hello to PocketSmartAI in one short sentence."
    )

    return {
        "response": result
    }


@router.get("/recommend")
def recommend(
    category: str,
    budget: int,
    preference: str,
    authorization: str = Header(None)
):
    username = get_current_user(authorization)

    if budget <= 0:
        raise HTTPException(
            status_code=400,
            detail="Budget must be greater than zero"
        )

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

    result = get_gemini_response(prompt, json_mode=True)

    platforms = MOCK_PLATFORMS.get(category, [])

    save_history(
        username,
        category,
        budget,
        preference,
        result
    )

    return {
        "category": category,
        "budget": budget,
        "preference": preference,
        "recommendations": result,
        "platforms": platforms
    }


@router.get("/generate-party")
def generate_party(
    budget: int,
    preference: str
):
    prompt = f"""
You are PocketSmartAI Party Planner.

Budget: ₹{budget}
Preference: {preference}

Give 5 useful party planning recommendations.

Include food, decoration, venue or entertainment where suitable.

For each recommendation, include:
1. Item
2. Estimated price
3. Short reason

Keep the total within the budget.
Keep the answer simple and practical.
"""

    result = get_gemini_response(prompt, json_mode=True)

    return {
        "category": "Party Planning",
        "budget": budget,
        "preference": preference,
        "recommendations": result
    }


@router.get("/generate-jewelry")
def generate_jewelry(
    budget: int,
    preference: str
):
    prompt = f"""
You are PocketSmartAI Jewelry Planner.

Budget: ₹{budget}
Preference: {preference}

Give 5 jewelry recommendations suitable for the user's preference.

For each recommendation, include:
1. Jewelry item
2. Estimated price
3. Short reason

Keep the total within the budget.
Keep the answer simple and practical.
"""

    result = get_gemini_response(prompt, json_mode=True)

    return {
        "category": "Jewellery",
        "budget": budget,
        "preference": preference,
        "recommendations": result
    }


@router.post("/register")
def register(
    username: str = Form(...),
    password: str = Form(...)
):
    success = register_user(username, password)

    if success:
        return {
            "message": "Registration successful"
        }

    return {
        "message": "Username already exists"
    }


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    success = login_user(username, password)

    if success:
        return {
            "message": "Login successful"
        }

    return {
        "message": "Invalid username or password"
    }


@router.post("/logout")
def logout():
    return {
        "message": "Logout successful"
    }


@router.post("/token")
def create_token(
    username: str = Form(...),
    password: str = Form(...)
):
    success = login_user(username, password)

    if not success:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        },
        JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/session-info")
def session_info(
    authorization: str = Header(None)
):
    username = get_current_user(authorization)

    return {
        "logged_in": True,
        "username": username
    }


@router.get("/session-data")
def session_data(
    authorization: str = Header(None)
):
    username = get_current_user(authorization)

    return {
        "username": username,
        "message": "Session data retrieved successfully"
    }


@router.post("/generate-jewelry-image")
async def generate_jewelry_image(
    budget: int = Form(...),
    preference: str = Form(...),
    image: UploadFile = File(...),
    authorization: str = Header(None)
):
    username = get_current_user(authorization)

    import json

    if budget <= 0:
        raise HTTPException(
            status_code=400,
            detail="Budget must be greater than zero"
        )

    if image.content_type not in [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WEBP images are allowed"
        )

    image_data = await image.read()

    if len(image_data) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 5 MB"
        )

    prompt = f"""
You are PocketSmartAI, a helpful AI jewellery recommendation assistant.

Analyze the uploaded outfit image.

Budget: ₹{budget}
Preference: {preference}

Recommend jewellery that matches the outfit.

Give exactly 5 recommendations.

For each recommendation include:
1. Item
2. Estimated price
3. Short reason

Return the answer ONLY as valid JSON in this format:

{{
    "recommendations": [
        {{
            "item": "Jewellery name",
            "price": "₹price",
            "reason": "Short reason"
        }}
    ],
    "total_estimate": "₹amount",
    "tip": "One useful styling tip"
}}
"""

    image_part = __import__(
        "google.genai",
        fromlist=["types"]
    ).types.Part.from_bytes(
        data=image_data,
        mime_type=image.content_type
    )

    models = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite"
    ]

    details = None
    last_error = None

    for model in models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[
                        prompt,
                        image_part
                    ],
                    config={
                        "response_mime_type": "application/json"
                    }
                )

                result = response.text.strip()
                result = result.replace("```json", "")
                result = result.replace("```", "")
                result = result.strip()

                first_brace = result.find("{")
                last_brace = result.rfind("}")

                if first_brace != -1 and last_brace != -1:
                    result = result[first_brace:last_brace + 1]

                details = json.loads(result)
                break

            except Exception as e:
                last_error = str(e)

                if "503" in last_error or "UNAVAILABLE" in last_error:
                    if attempt < 2:
                        import time
                        time.sleep(2 ** (attempt + 1))
                        continue
                    break

                raise HTTPException(
                    status_code=500,
                    detail=f"Gemini image processing error: {last_error}"
                )

        if details is not None:
            break

    if details is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini image processing is temporarily unavailable. "
                f"Last error: {last_error}"
            )
        )

    save_history(
        username,
        "Jewellery",
        budget,
        preference,
        json.dumps(details)
    )

    return {
        "category": "Jewellery",
        "budget": budget,
        "preference": preference,
        "image_filename": image.filename,
        "image_size": len(image_data),
        "recommendations": details["recommendations"],
        "total_estimate": details.get(
            "total_estimate",
            ""
        ),
        "tip": details.get(
            "tip",
            ""
        )
    }


@router.get("/history")
def get_history(
    authorization: str = Header(None)
):
    username = get_current_user(authorization)

    import sqlite3

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            category,
            budget,
            preference,
            recommendations
        FROM history
        WHERE username = ?
        ORDER BY id DESC
    """, (username,))

    rows = cursor.fetchall()

    connection.close()

    history = []

    for row in rows:
        history.append({
            "id": row[0],
            "username": row[1],
            "category": row[2],
            "budget": row[3],
            "preference": row[4],
            "recommendations": row[5]
        })

    return {
        "history": history
    }


@router.get("/recommendations-details")
def recommendations_details(
    category: str,
    budget: int,
    preference: str,
    authorization: str = Header(None)
):
    import json

    username = get_current_user(authorization)

    if budget <= 0:
        raise HTTPException(
            status_code=400,
            detail="Budget must be greater than zero"
        )

    prompt = f"""
You are PocketSmartAI.

Category: {category}
Budget: ₹{budget}
Preference: {preference}

Generate exactly 5 practical recommendations.

Return ONLY valid JSON.

Use this exact structure:

{{
    "recommendations": [
        {{
            "item": "Item name",
            "price": "₹1,000 - ₹2,000",
            "reason": "Short practical reason"
        }}
    ],
    "total_estimate": "₹8,000 - ₹10,000",
    "tip": "One useful final tip"
}}

Rules:
- Exactly 5 recommendations.
- Keep recommendations relevant to the category.
- Keep the total within the user's budget where possible.
- Do not use Markdown.
- Do not use ```json.
- Return ONLY JSON.
"""

    result = get_gemini_response(
        prompt,
        json_mode=True
    )

    try:
        details = json.loads(result)

    except json.JSONDecodeError as e:
        raise HTTPException(
        status_code=500,
        detail=f"AI returned invalid JSON: {result}"
    )

    return {
        "username": username,
        "category": category,
        "budget": budget,
        "preference": preference,
        "recommendations": details["recommendations"],
        "total_estimate": details.get(
            "total_estimate",
            ""
        ),
        "tip": details.get(
            "tip",
            ""
        )
    }