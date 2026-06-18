import os
import re
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

import streamlit as st
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, REFINEMENT_PROMPT

load_dotenv()

APP_TITLE = "One Perfect Day"
APP_SUBTITLE = "One city. One day. Precisely planned."

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌇",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #f6f7fb;
        --surface: #ffffff;
        --surface-soft: #fbfcfe;
        --border: #e7ebf3;
        --text: #111827;
        --muted: #667085;
        --brand: #264653;
        --brand-soft: #edf4f6;
        --accent: #d4a373;
        --shadow: 0 10px 30px rgba(16, 24, 40, 0.06);
        --radius: 18px;
    }
    html, body, [class*="css"]  {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--text);
    }
    .stApp {
        background: linear-gradient(180deg, #f7f8fb 0%, #f4f6fb 100%);
    }
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }
    h1 {
        font-size: 2.45rem !important;
        line-height: 1.08 !important;
        letter-spacing: -0.04em;
        margin-bottom: 0.25rem !important;
        color: var(--text);
    }
    h2 {
        font-size: 1.35rem !important;
        line-height: 1.25 !important;
        letter-spacing: -0.02em;
        margin-top: 0.5rem !important;
        margin-bottom: 0.35rem !important;
    }
    h3 {
        font-size: 1.04rem !important;
        line-height: 1.35 !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    p, li, label, .stMarkdown, .stTextInput, .stSelectbox, .stMultiSelect, .stTextArea, .stCaption {
        font-size: 0.96rem !important;
        line-height: 1.65 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
    }
    [data-testid="stForm"] {
        background: rgba(255,255,255,0.9);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 1rem 1rem 0.5rem 1rem;
        box-shadow: var(--shadow);
    }
    .hero {
        background: linear-gradient(135deg, rgba(38,70,83,0.96), rgba(43,76,90,0.92));
        color: white;
        border-radius: 24px;
        padding: 1.55rem 1.6rem 1.4rem 1.6rem;
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    .hero:before {
        content: "";
        position: absolute;
        right: -40px;
        top: -45px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(255,255,255,0.14), rgba(255,255,255,0));
        border-radius: 50%;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.92;
        margin-top: 0.15rem;
        margin-bottom: 0.55rem;
    }
    .hero-small {
        font-size: 0.92rem;
        color: rgba(255,255,255,0.84);
        margin-bottom: 0.7rem;
        max-width: 760px;
    }
    .pill-wrap {display: flex; gap: 0.45rem; flex-wrap: wrap; margin-top: 0.4rem;}
    .pill {
        display: inline-block;
        padding: 0.34rem 0.68rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.14);
        font-size: 0.82rem;
        font-weight: 500;
        color: white;
    }
    .mini-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1rem 0.85rem 1rem;
        box-shadow: 0 6px 18px rgba(16, 24, 40, 0.04);
        height: 100%;
    }
    .section-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 6px 18px rgba(16, 24, 40, 0.04);
        margin-bottom: 0.85rem;
    }
    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.76rem !important;
        color: var(--muted);
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .muted {color: var(--muted);}
    .map-box {
        background: var(--surface-soft);
        border: 1px dashed #cfd8e6;
        border-radius: 14px;
        padding: 0.9rem 1rem;
    }
    .section-card ul {padding-left: 1.2rem; margin-top: 0.3rem;}
    .section-card p {margin-bottom: 0.45rem;}
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-bottom: 0.6rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.72);
        border-radius: 12px;
        height: 44px;
        padding: 0 1rem;
        border: 1px solid var(--border);
        font-weight: 600;
        color: #344054;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        border-color: #d0d8e8 !important;
        box-shadow: 0 4px 14px rgba(16,24,40,0.05);
    }
    .stButton>button, .stDownloadButton>button, .stLinkButton>a {
        border-radius: 12px !important;
        font-weight: 650 !important;
        min-height: 44px;
        border: 1px solid transparent;
    }
    .stButton>button {
        background: linear-gradient(135deg, #264653 0%, #305c6c 100%);
        color: white;
    }
    .stDownloadButton>button {
        background: white;
        color: var(--text);
        border: 1px solid var(--border);
    }
    div[data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 14px;
        background: rgba(255,255,255,0.84);
    }
    .sidebar-note {
        font-size: 0.88rem;
        color: var(--muted);
    }
    .safety-card {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-left: 5px solid #f97316;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        margin: 1rem 0;
        box-shadow: 0 6px 18px rgba(16, 24, 40, 0.04);
    }
    .safety-card h3 {
        color: #9a3412;
        margin-top: 0 !important;
    }
    .safety-card p, .safety-card li {
        color: #7c2d12;
    }
    .notice-card {
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.85rem 1rem;
        color: var(--muted);
    }


    /* Streamlit Cloud can inherit a dark theme even when the app uses a light background.
       These overrides keep the interface readable and professional. */
    .stApp, .stApp p, .stApp li, .stApp span, .stApp label,
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] * {
        color: #111827 !important;
    }
    .hero, .hero *, .pill, .pill * {
        color: #ffffff !important;
    }
    .muted, .muted * {
        color: #667085 !important;
    }
    .eyebrow, .eyebrow * {
        color: #667085 !important;
    }
    .section-card, .section-card *, .mini-card, .mini-card *, .notice-card, .notice-card *, .map-box, .map-box * {
        color: #111827 !important;
    }
    .notice-card {
        background: #ffffff !important;
    }
    .safety-card, .safety-card * {
        color: #7c2d12 !important;
    }
    .safety-card h3 {
        color: #9a3412 !important;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div, .stMultiSelect div {
        color: #111827 !important;
        background-color: #ffffff !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #98a2b3 !important;
        opacity: 1 !important;
    }
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {
        color: #344054 !important;
    }
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {
        color: #111827 !important;
    }
    [data-testid="stAlert"], [data-testid="stAlert"] * {
        color: #111827 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_secret(name: str, default: str = "") -> str:
    try:
        val = st.secrets.get(name, None)
        if val is not None:
            return str(val)
    except Exception:
        pass
    return os.getenv(name, default)


def gemini_available() -> bool:
    return bool(get_secret("GEMINI_API_KEY"))


def call_gemini(prompt: str) -> str:
    api_key = get_secret("GEMINI_API_KEY")
    model_name = get_secret("GEMINI_MODEL", "gemini-2.0-flash")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT,
        generation_config={
            "temperature": 0.65,
            "top_p": 0.9,
            "max_output_tokens": 4200,
        },
    )
    response = model.generate_content(prompt)
    text = getattr(response, "text", "") or ""
    return text.strip()


GENERIC_PHRASES = [
    "shopping street",
    "cultural area",
    "local market",
    "a museum",
    "a restaurant",
    "nearby cafe",
    "viewpoint",
    "park",
    "landmark",
    "explore the city",
    "walk around",
]


def needs_refinement(text: str) -> bool:
    low = text.lower()
    hits = sum(1 for phrase in GENERIC_PHRASES if phrase in low)
    return hits >= 3


COUNTRY_ALIASES = {
    "dprk": "north korea",
    "democratic people's republic of korea": "north korea",
    "democratic peoples republic of korea": "north korea",
    "north korea": "north korea",
    "korea north": "north korea",
    "russia": "russia",
    "russian federation": "russia",
    "iran": "iran",
    "islamic republic of iran": "iran",
    "iraq": "iraq",
    "syria": "syria",
    "syrian arab republic": "syria",
    "yemen": "yemen",
    "afghanistan": "afghanistan",
    "somalia": "somalia",
    "sudan": "sudan",
    "south sudan": "south sudan",
    "libya": "libya",
    "haiti": "haiti",
    "mali": "mali",
    "burkina faso": "burkina faso",
    "belarus": "belarus",
    "ukraine": "ukraine",
    "myanmar": "myanmar",
    "burma": "myanmar",
    "venezuela": "venezuela",
    "lebanon": "lebanon",
}

CITY_COUNTRY_HINTS = {
    "pyongyang": "north korea",
    "kaesong": "north korea",
    "wonsan": "north korea",
    "tehran": "iran",
    "baghdad": "iraq",
    "erbil": "iraq",
    "damascus": "syria",
    "kabul": "afghanistan",
    "sanaa": "yemen",
    "aden": "yemen",
    "mogadishu": "somalia",
    "khartoum": "sudan",
    "juba": "south sudan",
    "tripoli": "libya",
    "port-au-prince": "haiti",
    "bamako": "mali",
    "ouagadougou": "burkina faso",
    "minsk": "belarus",
    "kyiv": "ukraine",
    "kiev": "ukraine",
    "yangon": "myanmar",
    "naypyidaw": "myanmar",
    "caracas": "venezuela",
    "beirut": "lebanon",
    "moscow": "russia",
    "st petersburg": "russia",
    "saint petersburg": "russia",
}

# Controlled fallback list used when live official advisory lookups fail or are unavailable.
# The app does not show the source names to users; it only uses this to avoid creating unsafe leisure itineraries.
HIGH_RISK_FALLBACK = {
    "north korea": {
        "label": "Travel planning paused",
        "reason": "Leisure tourism access can be highly restricted, organized travel options may change suddenly, and consular support can be extremely limited.",
        "alternatives": ["Seoul", "Busan", "Jeju", "Tokyo", "Taipei"],
    },
    "iran": {"label": "Travel planning paused", "reason": "Current official guidance may indicate serious security, detention, regional conflict, or operational risks.", "alternatives": ["Istanbul", "Tbilisi", "Yerevan", "Baku", "Muscat"]},
    "iraq": {"label": "Travel planning paused", "reason": "Current official guidance may indicate elevated security and conflict-related risks.", "alternatives": ["Amman", "Istanbul", "Cairo", "Muscat", "Doha"]},
    "syria": {"label": "Travel planning paused", "reason": "Current official guidance may indicate conflict, security, and access risks.", "alternatives": ["Amman", "Beirut", "Istanbul", "Cairo", "Athens"]},
    "yemen": {"label": "Travel planning paused", "reason": "Current official guidance may indicate conflict, security, and access risks.", "alternatives": ["Muscat", "Salalah", "Doha", "Dubai", "Amman"]},
    "afghanistan": {"label": "Travel planning paused", "reason": "Current official guidance may indicate security, terrorism, detention, and access risks.", "alternatives": ["Samarkand", "Bukhara", "Tashkent", "Istanbul", "Almaty"]},
    "somalia": {"label": "Travel planning paused", "reason": "Current official guidance may indicate terrorism, kidnapping, piracy, and security risks.", "alternatives": ["Zanzibar", "Mombasa", "Nairobi", "Muscat", "Doha"]},
    "sudan": {"label": "Travel planning paused", "reason": "Current official guidance may indicate armed conflict, civil unrest, and severe disruption.", "alternatives": ["Cairo", "Luxor", "Aswan", "Amman", "Muscat"]},
    "south sudan": {"label": "Travel planning paused", "reason": "Current official guidance may indicate conflict, violent crime, and limited emergency support.", "alternatives": ["Nairobi", "Kigali", "Addis Ababa", "Zanzibar", "Doha"]},
    "libya": {"label": "Travel planning paused", "reason": "Current official guidance may indicate conflict, crime, terrorism, and limited consular support.", "alternatives": ["Tunis", "Cairo", "Malta", "Athens", "Istanbul"]},
    "haiti": {"label": "Travel planning paused", "reason": "Current official guidance may indicate civil unrest, violent crime, kidnapping, and infrastructure disruption.", "alternatives": ["Punta Cana", "San Juan", "Aruba", "Curaçao", "Cartagena"]},
    "mali": {"label": "Travel planning paused", "reason": "Current official guidance may indicate terrorism, kidnapping, and security risks.", "alternatives": ["Marrakesh", "Dakar", "Accra", "Cape Verde", "Lisbon"]},
    "burkina faso": {"label": "Travel planning paused", "reason": "Current official guidance may indicate terrorism, kidnapping, and security risks.", "alternatives": ["Accra", "Dakar", "Marrakesh", "Cape Verde", "Lisbon"]},
    "belarus": {"label": "Travel planning paused", "reason": "Current official guidance may indicate arbitrary enforcement, detention, and regional security risks.", "alternatives": ["Warsaw", "Vilnius", "Riga", "Tallinn", "Kraków"]},
    "russia": {"label": "Travel planning paused", "reason": "Current official guidance may indicate detention, regional conflict, and limited consular support risks.", "alternatives": ["Tallinn", "Helsinki", "Riga", "Warsaw", "Tbilisi"]},
    "ukraine": {"label": "Travel planning paused", "reason": "Current official guidance may indicate active conflict and severe disruption.", "alternatives": ["Kraków", "Warsaw", "Prague", "Budapest", "Vienna"]},
    "myanmar": {"label": "Travel planning paused", "reason": "Current official guidance may indicate civil unrest, conflict, and security risks.", "alternatives": ["Chiang Mai", "Luang Prabang", "Bangkok", "Siem Reap", "Hanoi"]},
    "venezuela": {"label": "Travel planning paused", "reason": "Current official guidance may indicate crime, civil unrest, detention, or infrastructure risks.", "alternatives": ["Cartagena", "Medellín", "Quito", "Panama City", "Aruba"]},
    "lebanon": {"label": "Travel planning paused", "reason": "Current official guidance may indicate regional conflict and security disruption risks.", "alternatives": ["Amman", "Cairo", "Athens", "Istanbul", "Cyprus"]},
}

TOURISM_LIMITED = {
    "north korea": "Tourism access can be limited to tightly controlled tours and can change with little notice. Independent leisure planning may not be realistic or safe.",
}


def _clean_destination(value: str) -> str:
    return re.sub(r"[^a-zA-Z\s\-']", "", value or "").strip().lower()


def infer_country(city: str, country: str = "") -> str:
    combined = f"{country} {city}".strip()
    parts = [_clean_destination(country), _clean_destination(city), _clean_destination(combined)]
    for part in parts:
        if not part:
            continue
        if part in COUNTRY_ALIASES:
            return COUNTRY_ALIASES[part]
        if part in CITY_COUNTRY_HINTS:
            return CITY_COUNTRY_HINTS[part]
    city_clean = _clean_destination(city)
    for key, val in CITY_COUNTRY_HINTS.items():
        if re.search(rf"\b{re.escape(key)}\b", city_clean):
            return val
    country_clean = _clean_destination(country)
    for key, val in COUNTRY_ALIASES.items():
        if country_clean and re.search(rf"\b{re.escape(key)}\b", country_clean):
            return val
    return country_clean or ""


@st.cache_data(ttl=6 * 60 * 60, show_spinner=False)
def fetch_official_advisory_text(country: str) -> str:
    """Best-effort official advisory lookup. Fails closed to local fallback, not to random scoring."""
    if not country:
        return ""
    urls = [
        "https://cadataapi.state.gov/api/TravelAdvisories",
        "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/" + quote_plus(country) + "-travel-advisory.html",
    ]
    chunks: List[str] = []
    for url in urls:
        try:
            req = Request(url, headers={"User-Agent": "OnePerfectDay/1.0"})
            with urlopen(req, timeout=6) as resp:
                raw = resp.read(1_500_000).decode("utf-8", errors="ignore")
            chunks.append(raw[:1_500_000])
        except Exception:
            continue
    return "\n".join(chunks)


def official_text_indicates_do_not_travel(country: str, text: str) -> bool:
    if not text:
        return False
    low = re.sub(r"\s+", " ", text.lower())
    country_low = country.lower()
    # Prefer local windows around the country name to avoid generic advisory legends.
    windows = []
    for m in re.finditer(re.escape(country_low), low):
        start = max(0, m.start() - 900)
        end = min(len(low), m.end() + 1800)
        windows.append(low[start:end])
    if not windows:
        windows = [low[:4000]]
    patterns = [
        "level 4",
        "do not travel",
        "avoid all travel",
        "against all travel",
        "against all but essential travel",
    ]
    for window in windows[:5]:
        if any(p in window for p in patterns):
            # Avoid false hits from generic legend-only text when no country-specific surrounding terms exist.
            if country_low in window or "advisory" in window or "summary" in window:
                return True
    return False


def destination_safety_gate(data: Dict[str, str]) -> Optional[Dict[str, object]]:
    country = infer_country(data.get("city", ""), data.get("country", ""))
    city_clean = _clean_destination(data.get("city", ""))
    if not country and city_clean in CITY_COUNTRY_HINTS:
        country = CITY_COUNTRY_HINTS[city_clean]

    if not country:
        return None

    country_key = COUNTRY_ALIASES.get(country, country)
    live_text = fetch_official_advisory_text(country_key)
    live_block = official_text_indicates_do_not_travel(country_key, live_text)
    fallback = HIGH_RISK_FALLBACK.get(country_key)
    tourism_note = TOURISM_LIMITED.get(country_key, "")

    if live_block or fallback or tourism_note:
        info = fallback or {
            "label": "Travel planning paused",
            "reason": "Current official travel guidance may indicate that leisure travel is not recommended or is subject to serious restrictions.",
            "alternatives": [],
        }
        return {
            "country": country_key.title(),
            "label": info.get("label", "Travel planning paused"),
            "reason": info.get("reason", "Leisure travel may not be appropriate right now."),
            "alternatives": info.get("alternatives", []),
            "tourism_note": tourism_note,
            "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
    return None


def render_destination_pause(gate: Dict[str, object]) -> None:
    alternatives = gate.get("alternatives", []) or []
    tourism_note = gate.get("tourism_note", "")
    alt_text = ""
    if alternatives:
        alt_items = "".join(f"<li>{a}</li>" for a in alternatives[:5])
        alt_text = f"<p><strong>Safer idea:</strong> Try a nearby or culturally similar city instead:</p><ul>{alt_items}</ul>"
    tourism_html = f"<p>{tourism_note}</p>" if tourism_note else ""
    st.markdown(
        f"""
        <div class="safety-card">
            <h3>{gate.get('label', 'Travel planning paused')}</h3>
            <p><strong>{gate.get('country', 'This destination')}</strong> may not be suitable for a leisure one-day itinerary at the moment.</p>
            <p>{gate.get('reason', '')}</p>
            {tourism_html}
            <p>Before planning anything, verify the latest government travel advice, entry rules, tour availability, insurance coverage, and consular support for your nationality.</p>
            {alt_text}
            <p style="font-size:0.86rem; opacity:0.85;">Status checked: {gate.get('checked_at', '')}. This tool does not replace official travel advice.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


CITY_FALLBACKS: Dict[str, Dict[str, List[str]]] = {
    "tokyo": {
        "timeline": [
            "10:00 — Meiji Shrine: start with the forest walk and shrine approach.",
            "11:15 — Takeshita Street, Harajuku: quick street culture and snack/photo stop.",
            "12:15 — Omotesando: architecture, boutiques, and a calmer city walk.",
            "13:15 — Brown Rice by Neal's Yard Remedies or Mr. Farmer Omotesando: vegetarian-friendly lunch options; verify menu before visiting.",
            "14:45 — Shinjuku Gyoen National Garden: recovery block and soft walking.",
            "16:45 — Blue Bottle Coffee Shinjuku: rest and recharge.",
            "17:45 — Tokyo Metropolitan Government Building Observatory: skyline/sunset option; verify opening hours.",
            "19:15 — Omoide Yokocho, Shinjuku: atmospheric evening walk and dinner area.",
            "20:30 — Godzilla Head, Kabukicho: quick night-photo finish before returning.",
        ],
        "food": ["Brown Rice by Neal's Yard Remedies", "Mr. Farmer Omotesando", "Ain Soph Journey Shinjuku", "Omoide Yokocho"],
        "photos": ["Meiji Shrine forest approach", "Takeshita Street", "Omotesando Avenue", "Tokyo Metropolitan Government Building Observatory", "Godzilla Head, Kabukicho"],
    },
    "paris": {
        "timeline": [
            "09:30 — Jardin du Luxembourg: gentle start with classic Paris atmosphere.",
            "10:45 — Saint-Germain-des-Prés: bookshops, galleries, and streets around Rue Bonaparte.",
            "12:00 — Café de Flore or Les Deux Magots: iconic coffee stop; expect premium pricing.",
            "13:00 — Musée d'Orsay: focused art stop; verify ticket availability.",
            "15:30 — Walk along the Seine to Pont Alexandre III: scenic photo route.",
            "16:30 — Rue Cler: relaxed food street and market-style browsing.",
            "18:00 — Trocadéro Gardens: Eiffel Tower photo moment.",
            "19:30 — Le Grenier de Notre-Dame or Breizh Café Le Marais: dinner options; verify menu and reservations.",
        ],
        "food": ["Café de Flore", "Les Deux Magots", "Rue Cler", "Le Grenier de Notre-Dame", "Breizh Café Le Marais"],
        "photos": ["Jardin du Luxembourg", "Musée d'Orsay clock area", "Pont Alexandre III", "Trocadéro Gardens", "Rue Cler"],
    },
    "london": {
        "timeline": [
            "09:30 — Covent Garden: coffee, performers, and elegant start.",
            "10:45 — Neal's Yard: colourful courtyard photo stop.",
            "11:30 — The National Gallery, Trafalgar Square: focused culture stop; verify opening hours.",
            "13:00 — Dishoom Covent Garden or Mildreds Soho: lunch options; verify wait times.",
            "14:30 — Carnaby Street and Liberty London: specific shopping/photo route.",
            "16:00 — Fortnum & Mason, Piccadilly: premium food hall and gift browsing.",
            "17:30 — South Bank walk from Westminster Bridge to London Eye: golden-hour route.",
            "19:00 — Borough Market area or Flat Iron Covent Garden: dinner zone depending appetite.",
        ],
        "food": ["Dishoom Covent Garden", "Mildreds Soho", "Fortnum & Mason", "Borough Market", "Flat Iron Covent Garden"],
        "photos": ["Neal's Yard", "Trafalgar Square", "Carnaby Street", "Liberty London", "Westminster Bridge", "London Eye"],
    },
    "bangkok": {
        "timeline": [
            "09:00 — Wat Pho: start early at the Reclining Buddha temple; dress modestly.",
            "10:45 — Tha Maharaj: riverside coffee/rest stop.",
            "11:30 — Grand Palace exterior area or Museum Siam: choose based on heat and energy; verify opening hours.",
            "13:00 — Supanniga Eating Room Tha Tian or Ethos Vegetarian Restaurant: lunch options; verify menu.",
            "14:30 — ICONSIAM: air-conditioned shopping and river views.",
            "17:00 — Chao Phraya River ferry ride: sunset movement without heavy walking.",
            "18:30 — Asiatique The Riverfront: evening walk and dinner area.",
            "20:30 — Return by taxi/Grab or river connection depending location.",
        ],
        "food": ["Supanniga Eating Room Tha Tian", "Ethos Vegetarian Restaurant", "ICONSIAM", "Asiatique The Riverfront"],
        "photos": ["Wat Pho", "Tha Maharaj", "Chao Phraya River", "ICONSIAM riverside", "Asiatique The Riverfront"],
    },
    "dubai": {
        "timeline": [
            "10:00 — Al Fahidi Historical Neighbourhood: cultural start and photos.",
            "11:30 — Arabian Tea House, Al Fahidi: brunch/tea stop; verify reservations.",
            "12:45 — Dubai Creek abra ride from Bur Dubai to Deira: short classic crossing.",
            "13:30 — Gold Souk and Spice Souk: focused browsing, not all-day shopping.",
            "15:30 — Dubai Mall: indoor reset, aquarium viewing area, shopping.",
            "17:45 — Burj Khalifa / Dubai Fountain area: sunset and fountain timing; verify show schedule.",
            "19:30 — Time Out Market Dubai or Souk Al Bahar: dinner with views.",
        ],
        "food": ["Arabian Tea House", "Time Out Market Dubai", "Souk Al Bahar", "Dubai Mall dining areas"],
        "photos": ["Al Fahidi Historical Neighbourhood", "Dubai Creek abra", "Gold Souk", "Burj Khalifa", "Dubai Fountain"],
    },
    "singapore": {
        "timeline": [
            "09:30 — Tiong Bahru Bakery Foothills or Tiong Bahru Market: breakfast start.",
            "10:45 — National Gallery Singapore: focused culture stop; verify opening hours.",
            "12:45 — Lau Pa Sat or Maxwell Food Centre: lunch options with local food variety.",
            "14:15 — Chinatown: Buddha Tooth Relic Temple exterior/interior if open and Pagoda Street.",
            "16:00 — Gardens by the Bay Flower Dome/Cloud Forest: climate-controlled highlight; verify tickets.",
            "18:30 — Marina Bay Sands Boardwalk: skyline and golden hour.",
            "20:00 — Satay Street at Lau Pa Sat or Makansutra Gluttons Bay: dinner options.",
        ],
        "food": ["Tiong Bahru Bakery", "Tiong Bahru Market", "Lau Pa Sat", "Maxwell Food Centre", "Makansutra Gluttons Bay"],
        "photos": ["National Gallery Singapore", "Buddha Tooth Relic Temple", "Gardens by the Bay", "Marina Bay Sands Boardwalk", "Supertree Grove"],
    },
    "seoul": {
        "timeline": [
            "10:00 — Gyeongbokgung Palace: classic cultural start; verify opening day.",
            "11:30 — Bukchon Hanok Village: heritage streets and photos; be respectful of residents.",
            "12:45 — Insadong: lunch and tea-house browsing.",
            "14:30 — Ikseon-dong Hanok Street: cafes, design shops, and soft walking.",
            "16:30 — Cheonggyecheon Stream: rest and city walk.",
            "18:00 — Myeongdong: street food and shopping energy.",
            "20:00 — N Seoul Tower or Namsan Cable Car area: night view; verify timing.",
        ],
        "food": ["Insadong restaurants", "Ikseon-dong cafes", "Myeongdong street food", "Osegye Hyang vegetarian restaurant"],
        "photos": ["Gyeongbokgung Palace", "Bukchon Hanok Village", "Ikseon-dong Hanok Street", "Cheonggyecheon Stream", "N Seoul Tower"],
    },
    "rome": {
        "timeline": [
            "09:00 — Pantheon: early iconic start; verify entry process.",
            "10:00 — Piazza Navona: classic square and coffee stop.",
            "11:15 — Campo de' Fiori: market browsing if active.",
            "12:30 — Roscioli Salumeria con Cucina or Emma Pizzeria: lunch options; book ahead.",
            "14:00 — Largo di Torre Argentina and Jewish Ghetto: history-focused walk.",
            "15:30 — Capitoline Hill viewpoint: Roman Forum view without overloading.",
            "17:00 — Trevi Fountain: photo stop; expect crowds.",
            "18:30 — Spanish Steps and Via Condotti: evening finish and premium shopping view.",
        ],
        "food": ["Roscioli Salumeria con Cucina", "Emma Pizzeria", "Campo de' Fiori", "Jewish Ghetto restaurants"],
        "photos": ["Pantheon", "Piazza Navona", "Capitoline Hill viewpoint", "Trevi Fountain", "Spanish Steps"],
    },
    "new york": {
        "timeline": [
            "09:00 — Bryant Park and New York Public Library: calm Midtown start.",
            "10:30 — Grand Central Terminal: architecture and photos.",
            "11:30 — MoMA: focused museum stop; verify tickets.",
            "13:30 — Joe's Pizza Broadway or Le Botaniste Midtown: lunch options.",
            "15:00 — Central Park, Bethesda Terrace: scenic walking reset.",
            "16:30 — The Met steps/exterior or inside if energy allows; verify hours.",
            "18:30 — Top of the Rock or Summit One Vanderbilt: skyline option; book ahead.",
            "20:00 — Times Square quick photo finish or dinner in Hell's Kitchen.",
        ],
        "food": ["Joe's Pizza Broadway", "Le Botaniste Midtown", "Hell's Kitchen restaurants", "Bryant Park cafes"],
        "photos": ["New York Public Library", "Grand Central Terminal", "Bethesda Terrace", "Top of the Rock", "Times Square"],
    },
}


def fallback_plan(data: Dict[str, str]) -> str:
    city_key = data["city"].strip().lower()
    base = CITY_FALLBACKS.get(city_key)
    if not base:
        return f"""
## Perfect Day Summary
Exact place planning for **{data['city']}** needs the AI model to be configured. Add a Gemini API key in Streamlit Secrets to generate named places for any city globally.

## Exact Timeline With Named Places
Add `GEMINI_API_KEY` in Streamlit Secrets and rerun the plan to receive a specific timeline with named streets, restaurants, landmarks, viewpoints, museums, cafes, and backup options.

## Why This Route Works
The current app is running in demo mode. The UI is fully functional, but personalized city planning for unsupported cities requires the AI model.

## Food Stops
No city-specific list available in demo mode.

## Photo Moments
No city-specific list available in demo mode.

## Backup Plan
- Add a Gemini API key to unlock customized route design.
- Use one of the sample cities to preview the full layout.

## Map-Ready Place List
No city-specific list available in demo mode.

## Do Not Ruin The Day
- Avoid overpacking your first version.
- Verify opening hours before visiting.
""".strip()

    timeline = "\n".join([f"- {item}" for item in base["timeline"]])
    food = "\n".join([f"- {item}" for item in base["food"]])
    photos = "\n".join([f"- {item}" for item in base["photos"]])
    map_list = "\n".join(base["photos"] + base["food"])
    return f"""
## Perfect Day Summary
A specific one-day route for **{data['city']}** built around named places. This is a demo fallback plan. For a fully personalized plan based on every preference, add a Gemini API key.

## Exact Timeline With Named Places
{timeline}

## Why This Route Works
The plan groups nearby places and avoids turning one day into a city-wide sprint. It includes food, rest, photos, and a clear evening finish.

## Food Stops
{food}

## Photo Moments
{photos}

## Backup Plan
- If it rains: prioritize indoor museums, food halls, covered markets, and cafes from the named list above.
- If you feel tired: remove the most crowded middle stop and keep the skyline/evening finish.
- If something is closed: verify opening hours before visiting and switch to the nearest named backup.

## Map-Ready Place List
{map_list}

## Do Not Ruin The Day
- Do not add more than two extra attractions.
- Verify opening hours before visiting.
- Keep at least one rest stop between the main afternoon and evening plan.
""".strip()


def build_prompt(data: Dict[str, str]) -> str:
    return USER_PROMPT_TEMPLATE.format(**data)


def render_header() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>{APP_TITLE}</h1>
            <div class="hero-subtitle">{APP_SUBTITLE}</div>
            <div class="hero-small">A polished city-day planner that creates realistic routes with exact named places. Just enter the city, choose your vibe, and add anything important in one sentence.</div>
            <div class="pill-wrap">
                <span class="pill">Specific named places</span>
                <span class="pill">Professional layout</span>
                <span class="pill">Map-ready list</span>
                <span class="pill">Backup options</span>
                <span class="pill">Simple 3-step input</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_cards() -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="mini-card">
                <div class="eyebrow">Precision</div>
                <h3>Named places only</h3>
                <p class="muted">Museums, streets, cafes, viewpoints, markets, neighborhoods and restaurants are listed specifically — not vaguely.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="mini-card">
                <div class="eyebrow">Usability</div>
                <h3>Route that actually works</h3>
                <p class="muted">The plan is designed to stay coherent, reduce backtracking and fit the time window you have available.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="mini-card">
                <div class="eyebrow">Output</div>
                <h3>Beautiful and practical</h3>
                <p class="muted">Get a summary, timeline, food stops, photo moments, backup plan, and a clean list you can copy into maps.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _infer_budget(text: str) -> str:
    low = text.lower()
    if any(w in low for w in ["luxury", "5 star", "five star", "premium", "fine dining", "splurge"]):
        return "Premium"
    if any(w in low for w in ["budget", "cheap", "low cost", "backpacker", "free"]):
        return "Budget"
    return "Medium"


def _infer_food(text: str) -> str:
    low = text.lower()
    food_terms = [
        "vegetarian", "vegan", "halal", "kosher", "jain", "seafood", "street food", "no pork",
        "no beef", "gluten", "indian food", "local food", "fine dining", "cafe", "coffee"
    ]
    found = [term for term in food_terms if term in low]
    return ", ".join(found) if found else "No specific restriction"


def _infer_energy(text: str) -> str:
    low = text.lower()
    if any(w in low for w in ["relaxed", "slow", "easy", "light", "elderly", "kids", "low walking", "less walking"]):
        return "Low"
    if any(w in low for w in ["packed", "high energy", "adventure", "lots", "maximum", "intense"]):
        return "High"
    return "Moderate"


def _infer_travelling_with(text: str) -> str:
    low = text.lower()
    if any(w in low for w in ["wife", "husband", "partner", "girlfriend", "boyfriend", "anniversary", "romantic", "couple"]):
        return "Couple"
    if any(w in low for w in ["kids", "children", "child", "parents", "family"]):
        return "Family"
    if any(w in low for w in ["friends", "group"]):
        return "Friends"
    if any(w in low for w in ["business", "work trip", "conference"]):
        return "Business traveler"
    return "Solo"


def _infer_times(text: str) -> Tuple[str, str]:
    # Best effort only. The full free-text brief is still sent to the model.
    low = text.lower()
    times = re.findall(r"(?:[01]?\d|2[0-3])(?::[0-5]\d)?\s*(?:am|pm)?", low)
    clean = [t.upper().replace(" ", "") for t in times if not re.fullmatch(r"\d{1,2}", t)]
    if len(clean) >= 2:
        return clean[0], clean[1]
    if "morning" in low and "evening" in low:
        return "10:00 AM", "8:00 PM"
    if "half day" in low:
        return "10:00 AM", "4:00 PM"
    return "10:00 AM", "9:00 PM"


def _infer_month_or_date(text: str) -> str:
    month_match = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)", text.lower())
    if month_match:
        return month_match.group(0).title()
    for phrase in ["today", "tomorrow", "this weekend", "next weekend", "winter", "summer", "spring", "autumn", "fall", "rainy season"]:
        if phrase in text.lower():
            return phrase
    return "Not specified"


def collect_inputs() -> Dict[str, str]:
    st.markdown(
        """
        <div class="notice-card">
            <strong>Keep it simple:</strong> enter the city, choose the vibe, and optionally write everything else in one natural sentence. You do not need to fill a long form.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("perfect_day_form"):
        st.markdown("### Create your day")
        city = st.text_input("1. Which city? *", placeholder="Tokyo, Paris, Bangkok, London, Dubai...")

        travel_styles = st.multiselect(
            "2. What kind of day do you want?",
            [
                "Culture",
                "Food",
                "Photography",
                "Shopping",
                "Luxury",
                "Budget",
                "Romantic",
                "Family-friendly",
                "Hidden gems",
                "Relaxed",
                "Iconic landmarks",
                "Nature/parks",
                "Night views",
            ],
            default=["Culture", "Food", "Photography", "Relaxed"],
            help="Pick 2–5. The app will build a specific route with named places.",
        )

        user_brief = st.text_area(
            "3. Anything important?",
            placeholder=(
                "Example: 10 AM to 9 PM, vegetarian, medium budget, staying near Shinjuku, "
                "want culture + food + photos, avoid nightlife and heavy walking."
            ),
            height=105,
            help="Write naturally. Put timings, food, budget, starting area, must-see places, or things to avoid here.",
        )

        with st.expander("Optional: improve accuracy", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                country = st.text_input("Country", placeholder="Japan, France, Thailand...")
                date_or_month = st.text_input("Date / month", placeholder="April, tomorrow, this weekend...")
                start_time = st.text_input("Start time", placeholder="10:00 AM")
            with c2:
                end_time = st.text_input("End time", placeholder="9:00 PM")
                budget_level = st.selectbox("Budget", ["Auto-detect", "Budget", "Medium", "Premium", "Luxury"], index=0)
                food_preference = st.text_input("Food preference", placeholder="Vegetarian, halal, vegan, seafood...")
            with c3:
                energy_level = st.selectbox("Pace", ["Auto-detect", "Low", "Moderate", "High"], index=0)
                travelling_with = st.selectbox("Travelling with", ["Auto-detect", "Solo", "Couple", "Friends", "Family", "Business traveler", "Parents/kids"], index=0)
                weather_context = st.text_input("Weather", placeholder="Rainy, hot, cold, unknown...")

            c4, c5 = st.columns(2)
            with c4:
                starting_area = st.text_input("Starting area / hotel area", placeholder="Shinjuku, Eiffel Tower area, Marina Bay...")
                must_include = st.text_area("Must include", placeholder="Specific places or experiences you really want", height=70)
            with c5:
                ending_area = st.text_input("Ending area", placeholder="Hotel, airport, station, dinner area...")
                avoid = st.text_area("Avoid", placeholder="Crowds, nightlife, stairs, expensive restaurants...", height=70)
            special_occasion = st.text_input("Special occasion", placeholder="Birthday, anniversary, proposal, first solo trip...")
            mobility_notes = st.text_input("Mobility notes", placeholder="No stairs, stroller, elderly parent, limited walking...")

        submitted = st.form_submit_button("Create my perfect day", use_container_width=True)

    start_auto, end_auto = _infer_times(user_brief)
    inferred_budget = _infer_budget(user_brief)
    inferred_food = _infer_food(user_brief)
    inferred_energy = _infer_energy(user_brief)
    inferred_travel_with = _infer_travelling_with(user_brief)
    inferred_date = _infer_month_or_date(user_brief)

    return {
        "submitted": submitted,
        "city": city.strip(),
        "country": country.strip() or "Not specified",
        "date_or_month": date_or_month.strip() or inferred_date,
        "start_time": start_time.strip() or start_auto,
        "end_time": end_time.strip() or end_auto,
        "travel_styles": ", ".join(travel_styles) if travel_styles else "Balanced city day",
        "budget_level": inferred_budget if budget_level == "Auto-detect" else budget_level,
        "food_preference": food_preference.strip() or inferred_food,
        "energy_level": inferred_energy if energy_level == "Auto-detect" else energy_level,
        "travelling_with": inferred_travel_with if travelling_with == "Auto-detect" else travelling_with,
        "starting_area": starting_area.strip() or "Use the most route-efficient central starting point unless the user brief says otherwise",
        "ending_area": ending_area.strip() or "Not specified",
        "must_include": must_include.strip() or "Infer from the user brief and selected styles",
        "avoid": avoid.strip() or "Infer from the user brief; otherwise avoid overpacking and unnecessary backtracking",
        "mobility_notes": mobility_notes.strip() or "Not specified",
        "weather_context": weather_context.strip() or "Not specified",
        "special_occasion": special_occasion.strip() or "Not specified",
        "user_brief": user_brief.strip() or "No extra brief provided",
    }


def generate_plan(data: Dict[str, str]) -> str:
    if not data["city"]:
        raise ValueError("Please enter a city.")

    gate = destination_safety_gate(data)
    if gate:
        return "__DESTINATION_PAUSE__" + json.dumps(gate)

    if gemini_available():
        prompt = build_prompt(data)
        text = call_gemini(prompt)
        if needs_refinement(text):
            refinement = f"{REFINEMENT_PROMPT}\n\nUSER DETAILS:\n{prompt}\n\nPREVIOUS ANSWER:\n{text}"
            try:
                text = call_gemini(refinement)
            except Exception:
                pass
        return text

    return fallback_plan(data)


def parse_sections(plan: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    current = None
    buffer: List[str] = []
    for raw_line in plan.splitlines():
        line = raw_line.rstrip()
        heading_match = re.match(r"^##\s+(.+)$", line)
        if heading_match:
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = heading_match.group(1).strip()
            buffer = []
        else:
            buffer.append(line)
    if current:
        sections[current] = "\n".join(buffer).strip()
    if not sections:
        sections["Plan"] = plan.strip()
    return sections


def render_markdown_card(title: str, content: str, eyebrow: str = "") -> None:
    """Render a clean readable card without split open/close HTML blocks.

    Streamlit does not reliably keep custom HTML containers open across
    separate st.markdown calls. Using bordered native containers avoids the
    invisible-text bug seen when a dark Streamlit theme meets a light custom UI.
    """
    with st.container(border=True):
        if eyebrow:
            st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
        st.markdown(f"### {title}")
        st.markdown(content or "Not available.")

def render_results(city: str, plan: str) -> None:
    if plan.startswith("__DESTINATION_PAUSE__"):
        try:
            gate = json.loads(plan.replace("__DESTINATION_PAUSE__", "", 1))
        except Exception:
            gate = {"label": "Travel planning paused", "country": city, "reason": "This destination may not be suitable for leisure planning at the moment.", "alternatives": []}
        render_destination_pause(gate)
        return

    sections = parse_sections(plan)
    summary = sections.get("Perfect Day Summary", "")
    timeline = sections.get("Exact Timeline With Named Places", "")
    route_logic = sections.get("Why This Route Works", "")
    food = sections.get("Food Stops", "")
    photos = sections.get("Photo Moments", "")
    backup = sections.get("Backup Plan", "")
    map_list = sections.get("Map-Ready Place List", "")
    warnings = sections.get("Do Not Ruin The Day", "")

    st.markdown("---")
    st.markdown(f"## Your perfect day in {city}")

    top1, top2, top3 = st.columns([1.2, 1, 1])
    with top1:
        with st.container(border=True):
            st.markdown('<div class="eyebrow">Summary</div>', unsafe_allow_html=True)
            st.markdown(summary or "A polished one-day plan is ready below.")
    with top2:
        with st.container(border=True):
            st.markdown('<div class="eyebrow">Output quality</div>', unsafe_allow_html=True)
            st.markdown("### Specific route")
            st.markdown("The result is structured around exact places and practical pacing.")
    with top3:
        with st.container(border=True):
            st.markdown('<div class="eyebrow">Use this next</div>', unsafe_allow_html=True)
            st.markdown("### Copy into maps")
            st.markdown("Use the map-ready list tab to quickly create your route in Google Maps or Apple Maps.")

    tabs = st.tabs(["Timeline", "Route Logic", "Food & Photos", "Backup Plan", "Map List", "Full Plan"])

    with tabs[0]:
        render_markdown_card("Exact timeline with named places", timeline or "No timeline available.", "Main itinerary")
        if warnings:
            render_markdown_card("Do not ruin the day", warnings, "Keep in mind")

    with tabs[1]:
        render_markdown_card("Why this route works", route_logic or "No route explanation available.", "Planning logic")

    with tabs[2]:
        col_a, col_b = st.columns(2)
        with col_a:
            render_markdown_card("Food stops", food or "No food stops available.", "Where to eat")
        with col_b:
            render_markdown_card("Photo moments", photos or "No photo moments available.", "What to capture")

    with tabs[3]:
        render_markdown_card("Backup plan", backup or "No backup plan available.", "If the day changes")

    with tabs[4]:
        with st.container(border=True):
            st.markdown('<div class="eyebrow">Copy list</div>', unsafe_allow_html=True)
            st.markdown("### Map-ready place list")
            st.markdown(map_list or "No map-ready list available.")

    with tabs[5]:
        with st.container(border=True):
            st.markdown(plan)

def main() -> None:
    render_header()
    render_feature_cards()

    with st.expander("What makes a high-quality result?", expanded=False):
        st.write(
            "A strong result names exact places: streets, restaurants, museums, cafes, parks, viewpoints and markets. "
            "It should avoid vague output like 'visit a cultural area' or 'go shopping nearby'. "
            "If the destination appears unsuitable for leisure travel, the app pauses the itinerary instead of forcing a day plan."
        )

    data = collect_inputs()

    if data["submitted"]:
        try:
            with st.spinner("Designing one specific, realistic day..."):
                plan = generate_plan(data)
            st.session_state["last_plan"] = plan
            st.session_state["last_city"] = data["city"]
        except Exception as exc:
            st.error("The plan could not be generated.")
            st.caption(str(exc))

    if "last_plan" in st.session_state:
        render_results(st.session_state.get("last_city", "the city"), st.session_state["last_plan"])

        file_name = f"one-perfect-day-{st.session_state.get('last_city', 'city').lower().replace(' ', '-')}.md"
        c1, c2 = st.columns([1, 1])
        with c1:
            st.download_button(
                "Download plan",
                data=st.session_state["last_plan"],
                file_name=file_name,
                mime="text/markdown",
                use_container_width=True,
            )
        with c2:
            coffee_url = get_secret("BUY_ME_A_COFFEE_URL", "")
            if coffee_url:
                st.link_button("Support this free tool", coffee_url, use_container_width=True)

    with st.sidebar:
        st.markdown("### Setup")
        if gemini_available():
            st.success("Gemini key configured")
        else:
            st.info("Demo mode: built-in sample cities only. Add GEMINI_API_KEY for global exact-place planning.")
        st.markdown('<p class="sidebar-note">The app stays clean: no public risk score and no noisy live-feed dashboard. It simply pauses leisure planning when a destination appears unsuitable for tourism and focuses on one elegant day when travel is appropriate.</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
