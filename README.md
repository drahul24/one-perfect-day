# One Perfect Day — Professional UI + Destination Suitability Gate

A Streamlit app that creates a polished, specific one-day plan in any city with exact named places, food stops, photo moments, backup options, and a map-ready list.

This version adds a destination suitability gate. If a destination appears to be under a do-not-travel style advisory or has highly restricted tourism access, the app pauses the leisure itinerary and gives a safer message instead of forcing a normal day plan.

## Files

- `app.py` — Streamlit app with professional UI and destination suitability gate
- `prompts.py` — Gemini prompt rules
- `requirements.txt` — dependencies
- `.gitignore` — avoids cache/env files

## Deploy

Upload these files to GitHub:

```text
app.py
prompts.py
requirements.txt
README.md
.gitignore
```

Do not upload:

```text
__pycache__
*.pyc
.env
```

## Streamlit Secrets

Add this for global exact-place planning:

```toml
GEMINI_API_KEY = "paste_your_key_here"
GEMINI_MODEL = "gemini-2.0-flash"
BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/yourname"
```

## Safety behavior

The app does not show a public risk score. It simply pauses leisure planning for destinations where a normal tourism itinerary may be inappropriate. It uses a controlled fallback list and a best-effort official advisory check. It does not replace official government travel advice.
