# One Perfect Day — v2.2 No Empty Results

A simplified Streamlit travel app that creates one realistic day in a city using exact named places, food stops, photo moments, backup plans and a map-ready list.

## What changed in v2.2

- No more empty output when Gemini is not configured.
- Built-in professional fallback plans for Delhi, Tokyo, Paris and London.
- Clean three-question input.
- Professional light UI.
- Destination suitability gate for restricted/high-risk destinations.
- Clear message when using built-in fallback vs AI mode.

## Files

Upload these to GitHub:

```text
app.py
prompts.py
requirements.txt
README.md
.gitignore
.streamlit/config.toml
```

Do not upload:

```text
*.pyc
__pycache__
.env
```

## Streamlit Secrets

Optional but recommended for global city coverage:

```toml
GEMINI_API_KEY = "paste_your_key_here"
GEMINI_MODEL = "gemini-2.0-flash"
BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/yourname"
```

## Deploy

Main file path:

```text
app.py
```

