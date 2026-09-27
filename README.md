# PocketSmartAI

PocketSmartAI is an AI-powered budget recommendation assistant.

It uses Google's Gemini AI to generate personalized recommendations based on the user's category, budget, and preferences.

## Features

- Home Decoration recommendations
- Party Planning recommendations
- Jewellery recommendations
- Budget-based suggestions
- Preference-based recommendations
- AI-generated recommendations using Gemini
- FastAPI backend
- Simple and user-friendly web interface

## Technologies Used

- Python
- FastAPI
- Google Gemini AI
- HTML
- CSS
- JavaScript
- Jinja2
- Uvicorn

## Project Structure

```text
PocketSmartAI/
│
├── app/
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   └── services.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## How It Works

1. User selects a category.
2. User enters a budget.
3. User enters their preference.
4. FastAPI receives the request.
5. Gemini AI generates recommendations.
6. PocketSmartAI displays the recommendations as cards.

## Categories

### Home Decoration
Provides decoration ideas based on the user's budget and style.

### Party Planning
Provides party-related suggestions based on the event and budget.

### Jewellery
Provides jewellery recommendations based on the user's preference and budget.

## How to Run

Install the required packages:

```bash
pip install -r requirements.txt
```

Add your Gemini API key to the `.env` file:

```text
GEMINI_API_KEY=your_api_key_here
```

Run the application:

```bash
python run.py
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

## Security

The Gemini API key is stored in the `.env` file and should never be uploaded to GitHub.

The `.gitignore` file prevents sensitive and unnecessary files from being uploaded.

## Future Improvements

- User login and authentication
- Recommendation history
- Product images
- Price comparison
- Database integration
- Mobile-friendly design
- More recommendation categories