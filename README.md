# One Perfect Day v3 — Named Places Engine

A Streamlit app that creates a specific one-day city plan using:

- A clean 3-question form
- Built-in curated plans for popular cities
- Live OpenStreetMap/Nominatim/Overpass place lookup for unsupported cities
- Optional Gemini key for enhanced writing

## Upload files

Upload these to GitHub:

- app.py
- prompts.py
- requirements.txt
- README.md
- .gitignore
- .streamlit/config.toml

Do not upload ZIP files, `.pyc` files, or `__pycache__`.

## Streamlit secrets

Optional:

```toml
GEMINI_API_KEY = "your_key"
GEMINI_MODEL = "gemini-2.0-flash"
BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/yourname"
```

The app works without Gemini by using curated plans and live public map data.
