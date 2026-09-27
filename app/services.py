from google import genai
from app.config import GEMINI_API_KEY
import time

client = genai.Client(api_key=GEMINI_API_KEY)


def get_gemini_response(prompt):

    for attempt in range(3):

        try:

            response = client.models.generate_content(
               model="gemini-3.1-flash-lite",
                contents=prompt
            )

            return response.text

        except Exception as e:

            error = str(e)

            if "503" in error and attempt < 2:
                time.sleep(2)
                continue

            return f"Gemini error: {error}"