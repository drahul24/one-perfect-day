# One Perfect Day — Smart Input Build

A Streamlit app that creates one specific, realistic, premium day in any city using exact named places.

## What changed in this build

The form is now simplified. Users only need to answer:

1. City
2. What kind of day they want
3. Anything important in one natural-language box

Everything else is optional inside an expandable section. The app uses smart defaults and extracts intent from the user's free-text brief.

## Files

- `app.py` — Streamlit app
- `prompts.py` — AI instructions
- `requirements.txt` — Python dependencies
- `.gitignore` — prevents cache/env files from being uploaded

## Streamlit secrets

Add these in Streamlit Cloud → Manage app → Settings → Secrets:

```toml
GEMINI_API_KEY = "paste_your_key_here"
GEMINI_MODEL = "gemini-2.0-flash"
BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/yourname"
```

## Deploy

Upload these files to GitHub:

- `app.py`
- `prompts.py`
- `requirements.txt`
- `README.md`
- `.gitignore`

Then deploy through Streamlit Community Cloud with `app.py` as the main file.
