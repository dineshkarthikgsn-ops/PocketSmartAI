from google import genai
from app.config import GEMINI_API_KEY
import time


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite"
]


def clean_json_response(result):
    """
    Clean common formatting Gemini may add around JSON.
    """

    if not result:
        return result

    result = result.strip()

    # Remove Markdown JSON fences
    if result.startswith("```json"):
        result = result[7:]

    if result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    result = result.strip()

    # If Gemini added text before/after JSON,
    # extract the JSON object.
    first_brace = result.find("{")
    last_brace = result.rfind("}")

    if first_brace != -1 and last_brace != -1:
        result = result[first_brace:last_brace + 1]

    return result.strip()


def get_gemini_response(prompt, json_mode=False):

    last_error = None

    for model in MODELS:

        for attempt in range(3):

            try:

                config = None

                if json_mode:
                    config = {
                        "response_mime_type": "application/json"
                    }

                if config:

                    response = client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=config
                    )

                else:

                    response = client.models.generate_content(
                        model=model,
                        contents=prompt
                    )

                result = response.text

                if not result:
                    raise Exception(
                        "Gemini returned an empty response."
                    )

                # Clean JSON responses
                if json_mode:
                    result = clean_json_response(result)

                return result

            except Exception as e:

                last_error = str(e)

                print(
                    f"Gemini error using {model}, "
                    f"attempt {attempt + 1}/3: {last_error}"
                )

                if (
                    "503" in last_error
                    or "UNAVAILABLE" in last_error
                ):

                    if attempt < 2:

                        wait_time = 2 ** (attempt + 1)

                        print(
                            f"Retrying in {wait_time} seconds..."
                        )

                        time.sleep(wait_time)

                        continue

                    print(
                        f"{model} unavailable. "
                        "Trying fallback model..."
                    )

                    break

                return f"Gemini error: {last_error}"

    return (
        "Gemini error: AI service is temporarily unavailable. "
        f"Last error: {last_error}"
    )