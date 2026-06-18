# One Perfect Day — Smart Input v2.1 Visibility Fix

A clean Streamlit app that creates one specific, realistic city day using exact named places.

## What changed in v2.1

- Fixed invisible/white result text on light background.
- Forced a professional light theme through `.streamlit/config.toml`.
- Reworked result cards to use Streamlit's native bordered containers instead of fragile split HTML wrappers.
- Kept the simplified 3-question input flow.
- Kept destination suitability guardrails for places where normal leisure planning may not be appropriate.

## Upload to GitHub

Upload/replace these items:

- `app.py`
- `prompts.py`
- `requirements.txt`
- `README.md`
- `.gitignore`
- `.streamlit/config.toml`

Do not upload `__pycache__`, `.env`, or `.pyc` files.

## Streamlit Secrets

Add these in Streamlit Cloud → Manage app → Settings → Secrets:

```toml
GEMINI_API_KEY = "paste_your_key_here"
GEMINI_MODEL = "gemini-2.0-flash"
BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/yourname"
```

Without Gemini, the app runs in demo mode for selected sample cities only.
