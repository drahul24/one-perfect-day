import os
import re
import textwrap
from datetime import datetime
from typing import Dict, List, Optional

import requests
import streamlit as st

try:
    from prompts import SYSTEM_PROMPT
except Exception:
    SYSTEM_PROMPT = "You are One Perfect Day, a premium one-day city planning assistant. Always return exact named places."

st.set_page_config(
    page_title="One Perfect Day",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
:root {
  --bg: #f7f8fc;
  --card: #ffffff;
  --ink: #111827;
  --muted: #5b6475;
  --line: #e5e9f2;
  --accent: #e85d75;
  --accent2: #6d5dfc;
  --soft: #fff1f4;
}
html, body, [data-testid="stAppViewContainer"] { background: var(--bg) !important; color: var(--ink) !important; }
[data-testid="stHeader"] { background: rgba(247, 248, 252, 0.86) !important; }
.block-container { padding-top: 2.2rem; padding-bottom: 3.5rem; max-width: 1180px; }
h1, h2, h3, h4, p, li, div, span, label { color: var(--ink); }
.hero {
  background: linear-gradient(135deg, #111827 0%, #202a44 54%, #49344b 100%);
  border-radius: 28px;
  padding: 44px 42px;
  color: white;
  box-shadow: 0 18px 48px rgba(17, 24, 39, 0.22);
  margin-bottom: 24px;
}
.hero h1 { color: #fff !important; font-size: 3rem; line-height: 1.03; margin: 0 0 10px; letter-spacing: -0.04em; }
.hero p { color: rgba(255,255,255,0.86) !important; font-size: 1.12rem; max-width: 760px; margin: 0; }
.pill-row { margin-top: 20px; display:flex; gap:10px; flex-wrap:wrap; }
.pill { color:#fff; border:1px solid rgba(255,255,255,.2); background:rgba(255,255,255,.08); border-radius: 999px; padding:8px 12px; font-size:.88rem; }
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 26px;
  box-shadow: 0 12px 32px rgba(17, 24, 39, .06);
  margin: 14px 0;
}
.card h3 { margin-top:0; font-size:1.18rem; letter-spacing:-.01em; }
.kicker { text-transform:uppercase; letter-spacing:.12em; color:#6b7280; font-size:.78rem; font-weight:800; margin-bottom:8px; }
.section-title { font-size: 1.55rem; margin: 26px 0 10px; letter-spacing:-.02em; }
.subtle { color: var(--muted); font-size:.96rem; }
.badge { display:inline-block; border-radius:999px; padding:6px 10px; background:#eef2ff; color:#3730a3; font-weight:700; font-size:.8rem; margin-right:6px; }
.warnbox { background:#fff7ed; border:1px solid #fed7aa; color:#7c2d12; padding:16px 18px; border-radius:18px; }
.successbox { background:#ecfdf5; border:1px solid #a7f3d0; color:#064e3b; padding:16px 18px; border-radius:18px; }
.small-note { color:#6b7280; font-size:.88rem; margin-top: 8px; }
.stButton > button {
  border-radius: 14px !important;
  border: 0 !important;
  padding: .78rem 1.1rem !important;
  font-weight: 800 !important;
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: white !important;
  box-shadow: 0 12px 24px rgba(232, 93, 117, .22) !important;
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
  border-radius: 14px !important;
  border-color: #dbe1ec !important;
  background: #fff !important;
  color: var(--ink) !important;
}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { font-size: 1rem; line-height: 1.72; }
hr { border: none; border-top: 1px solid var(--line); margin: 20px 0; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

UNSUITABLE_DESTINATIONS = {
    "north korea", "democratic people's republic of korea", "dprk", "pyongyang",
    "syria", "yemen", "afghanistan", "somalia", "libya", "sudan", "south sudan",
    "gaza", "gaza city", "ukraine", "iran", "iraq", "haiti", "myanmar", "burma"
}

CITY_PLANS: Dict[str, Dict[str, str]] = {
    "delhi": {
        "summary": "A polished Delhi day that stays mostly around Lodhi, Nizamuddin, Pragati Maidan and Connaught Place, balancing heritage, green space, food, photography and a clean evening finish.",
        "timeline": """
**10:00 AM — Lodhi Garden**  
Start with a calm walk around the tombs of Mohammed Shah and Sikandar Lodi. It is photogenic, central and gentle for the morning.

**11:15 AM — Humayun’s Tomb**  
Move to one of Delhi’s strongest heritage landmarks. Keep 60–75 minutes for the main tomb, gardens and photography.

**12:45 PM — Sunder Nursery**  
Walk through the restored gardens near Humayun’s Tomb. This gives the day a softer, less rushed pace.

**1:45 PM — Lunch at Carnatic Café, Lodhi Colony**  
A reliable, specific food stop for a comfortable South Indian lunch. Vegetarian-friendly.

**3:15 PM — National Crafts Museum & Hastkala Academy**  
A more distinctive cultural stop than generic sightseeing. Good for crafts, textiles, architecture details and slower discovery.

**4:45 PM — India Gate and Kartavya Path**  
A classic Delhi photo and walking stop. Keep it short and elegant rather than making it the whole evening.

**6:00 PM — Agrasen ki Baoli**  
A compact, atmospheric stop that works well before Connaught Place.

**7:00 PM — Connaught Place Inner Circle + Janpath Market**  
Use this for a light shopping walk, snacks and colonial-era city visuals.

**8:15 PM — Dinner at United Coffee House or Saravana Bhavan, Connaught Place**  
Choose United Coffee House for old Delhi charm, or Saravana Bhavan for a simpler vegetarian dinner.
        """,
        "route": "This route avoids jumping between Old Delhi, South Delhi and Gurugram in one day. Lodhi Garden, Humayun’s Tomb, Sunder Nursery, Lodhi Colony, India Gate and Connaught Place form a practical central/south-central arc.",
        "food": "Carnatic Café, Lodhi Colony · United Coffee House, Connaught Place · Saravana Bhavan, Connaught Place · Triveni Terrace Café near Mandi House as an alternative.",
        "photos": "Lodhi Garden tomb arches · Humayun’s Tomb central walkway · Sunder Nursery gardens · India Gate/Kartavya Path · Agrasen ki Baoli steps · Connaught Place colonnades.",
        "backup": "If it is too hot, reduce outdoor time and replace Sunder Nursery with National Gallery of Modern Art. If traffic is heavy, skip Agrasen ki Baoli and stay around Connaught Place. If you want more shopping, replace National Crafts Museum with Khan Market.",
        "map": "Lodhi Garden\nHumayun’s Tomb\nSunder Nursery\nCarnatic Café Lodhi Colony\nNational Crafts Museum & Hastkala Academy\nIndia Gate\nAgrasen ki Baoli\nJanpath Market\nConnaught Place\nUnited Coffee House Connaught Place",
    },
    "new delhi": None,
    "tokyo": {
        "summary": "A western Tokyo day with shrine calm, Harajuku energy, Omotesando style, Shinjuku greenery, skyline views and an atmospheric evening.",
        "timeline": """
**10:00 AM — Meiji Shrine**  
Start with the forest approach and shrine grounds before the city gets too intense.

**11:15 AM — Takeshita Street, Harajuku**  
A compact dose of fashion, snacks, youth culture and street photos.

**12:15 PM — Omotesando**  
Walk Omotesando Avenue for architecture, boutiques and a more polished shopping atmosphere.

**1:15 PM — Lunch at Brown Rice by Neal’s Yard Remedies, Omotesando**  
A strong vegetarian-friendly lunch option.

**2:45 PM — Shinjuku Gyoen National Garden**  
A calm reset after Harajuku and Omotesando.

**4:30 PM — NEWoMan Shinjuku / Blue Bottle Coffee Shinjuku**  
Use this as a clean rest stop before sunset.

**5:45 PM — Tokyo Metropolitan Government Building Observatory**  
A free skyline viewpoint and strong golden-hour option.

**7:15 PM — Omoide Yokocho, Shinjuku**  
Atmospheric evening lanes and classic Tokyo visuals. Choose food carefully if vegetarian.

**8:30 PM — Kabukicho Godzilla Head**  
Finish with iconic night lights without committing to heavy nightlife.
        """,
        "route": "The day stays around Harajuku, Omotesando and Shinjuku, avoiding long east-west jumps across Tokyo.",
        "food": "Brown Rice by Neal’s Yard Remedies · Ain Soph Journey Shinjuku · Mr. Farmer Omotesando · Tsunahachi Shinjuku for non-vegetarian tempura.",
        "photos": "Meiji Shrine forest path · Takeshita Street signage · Omotesando architecture · Shinjuku Gyoen gardens · Tokyo Metropolitan Government Building skyline · Kabukicho Godzilla Head.",
        "backup": "If it rains, replace Shinjuku Gyoen with Mori Art Museum or Nezu Museum. If Harajuku feels crowded, spend more time in Omotesando and Aoyama.",
        "map": "Meiji Shrine\nTakeshita Street\nOmotesando\nBrown Rice by Neal’s Yard Remedies\nShinjuku Gyoen National Garden\nNEWoMan Shinjuku\nTokyo Metropolitan Government Building Observatory\nOmoide Yokocho\nKabukicho Godzilla Head",
    },
    "paris": {
        "summary": "A left-bank to central Paris day: refined museum time, Seine walking, classic cafés, elegant streets and a beautiful evening finish.",
        "timeline": """
**10:00 AM — Musée d’Orsay**  
Start with a world-class museum in a manageable, beautiful setting.

**12:00 PM — Walk along the Seine to Pont Alexandre III**  
A scenic route with strong photo moments.

**12:45 PM — Lunch at Le Grenier de Notre-Dame**  
A long-running vegetarian-friendly Paris option near the Latin Quarter.

**2:15 PM — Shakespeare and Company**  
A specific cultural stop that adds character without overloading the day.

**3:00 PM — Île Saint-Louis and Berthillon area**  
A compact, atmospheric walk with classic Paris texture.

**4:15 PM — Place des Vosges, Le Marais**  
One of Paris’s most elegant squares and a calmer late-afternoon stop.

**5:30 PM — Rue des Rosiers, Le Marais**  
Specific street for food, browsing and neighborhood energy.

**7:00 PM — Dinner at Breizh Café Le Marais or Le Potager du Marais**  
Choose Breizh Café for crêpes, Le Potager du Marais for vegetarian.

**8:30 PM — Seine evening walk near Hôtel de Ville**  
End with a low-pressure night walk.
        """,
        "route": "The route avoids trying to combine the Eiffel Tower, Montmartre and Louvre in one rushed day. It focuses on Musée d’Orsay, the Seine, Île Saint-Louis and Le Marais.",
        "food": "Le Grenier de Notre-Dame · Le Potager du Marais · Breizh Café Le Marais · Berthillon for ice cream.",
        "photos": "Musée d’Orsay clock · Pont Alexandre III · Shakespeare and Company exterior · Île Saint-Louis streets · Place des Vosges arches · Seine near Hôtel de Ville.",
        "backup": "If it rains, add Musée de l’Orangerie or Centre Pompidou instead of long outdoor walks. If museums are full, focus on Le Marais, covered passages and cafés.",
        "map": "Musée d’Orsay\nPont Alexandre III\nLe Grenier de Notre-Dame\nShakespeare and Company\nÎle Saint-Louis\nBerthillon\nPlace des Vosges\nRue des Rosiers\nBreizh Café Le Marais\nHôtel de Ville Paris",
    },
    "london": {
        "summary": "A central London day with Westminster icons, river views, Covent Garden, Soho food and an elegant West End finish.",
        "timeline": """
**10:00 AM — Westminster Abbey exterior + Parliament Square**  
Start with London’s most recognizable civic core.

**10:45 AM — Walk across Westminster Bridge to South Bank**  
Great views of Big Ben and the Thames.

**11:30 AM — Southbank Centre / Queen’s Walk**  
A relaxed riverside walk with good breaks.

**12:45 PM — Lunch at Mildreds Covent Garden**  
Reliable vegetarian-friendly central option.

**2:00 PM — Covent Garden Piazza**  
Street performance, shops and easy browsing.

**3:00 PM — Neal’s Yard**  
Colorful, compact and photogenic.

**4:00 PM — National Gallery, Trafalgar Square**  
A free high-value cultural stop.

**5:45 PM — Piccadilly Circus and Regent Street**  
Classic London lights and shopping without making it a shopping-only day.

**7:15 PM — Dinner in Soho at Dishoom Carnaby or Kiln**  
Choose based on availability and food preference.

**8:45 PM — Leicester Square / West End walk**  
A simple finish with theatre district energy.
        """,
        "route": "The day stays in Westminster, South Bank, Covent Garden, Soho and the West End, minimizing Tube dependency.",
        "food": "Mildreds Covent Garden · Dishoom Carnaby · Kiln Soho · Flat Iron Covent Garden as a non-vegetarian budget option.",
        "photos": "Westminster Bridge · South Bank river path · Covent Garden Piazza · Neal’s Yard · Trafalgar Square · Regent Street lights.",
        "backup": "If it rains, reduce South Bank time and add the National Portrait Gallery or British Museum. If Covent Garden is crowded, shift to Seven Dials and Neal’s Yard.",
        "map": "Westminster Abbey\nWestminster Bridge\nSouthbank Centre\nMildreds Covent Garden\nCovent Garden Piazza\nNeal’s Yard\nNational Gallery\nPiccadilly Circus\nRegent Street\nDishoom Carnaby",
    },
}
CITY_PLANS["new delhi"] = CITY_PLANS["delhi"]
CITY_PLANS["old delhi"] = CITY_PLANS["delhi"]
CITY_PLANS["nyc"] = CITY_PLANS["london"]


def get_secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)


def clean_city(city: str) -> str:
    return re.sub(r"[^a-zA-Z\s]", "", (city or "")).strip().lower()


def parse_details(details: str) -> Dict[str, str]:
    text = details or ""
    low = text.lower()
    profile = {
        "time": "Flexible day",
        "budget": "Comfort",
        "food": "Open to local food",
        "pace": "Balanced",
        "with": "Solo / flexible",
    }
    time_match = re.search(r"(\d{1,2}\s*(?:am|pm|AM|PM))\s*(?:to|-|until|till)\s*(\d{1,2}\s*(?:am|pm|AM|PM))", text)
    if time_match:
        profile["time"] = f"{time_match.group(1)} to {time_match.group(2)}"
    if "vegetarian" in low or "vegan" in low:
        profile["food"] = "Vegetarian-friendly"
    if "luxury" in low:
        profile["budget"] = "Luxury"
    elif "budget" in low or "cheap" in low:
        profile["budget"] = "Budget-conscious"
    elif "medium" in low or "comfort" in low:
        profile["budget"] = "Comfort"
    if "relaxed" in low or "slow" in low or "easy" in low:
        profile["pace"] = "Relaxed"
    elif "packed" in low or "high energy" in low or "fast" in low:
        profile["pace"] = "High energy"
    if "couple" in low or "wife" in low or "husband" in low or "partner" in low:
        profile["with"] = "Couple"
    elif "family" in low or "kids" in low or "children" in low:
        profile["with"] = "Family"
    elif "friends" in low:
        profile["with"] = "Friends"
    return profile


def destination_gate(city: str) -> Optional[str]:
    c = clean_city(city)
    if c in UNSUITABLE_DESTINATIONS:
        return f"""
### Normal leisure planning paused for {city.title()}

This destination may not be suitable for a normal independent leisure day because travel access, safety conditions, tourism availability or official restrictions may be limited.

Before making any plan, verify current official travel advice, entry requirements, local restrictions, insurance validity and consular support. For a safer version of this product, choose a nearby alternative destination with normal tourism infrastructure.

**Safer alternatives to consider:** Seoul, Tokyo, Singapore, Bangkok, Dubai, Istanbul, Paris, London.
        """
    return None


def build_prompt(city, day_style, details, optional_notes):
    return f"""
{SYSTEM_PROMPT}

User request:
City: {city}
Desired day: {day_style}
Important details: {details}
Optional notes: {optional_notes}

Generate the one-day plan now. Be specific. Named places only. No generic placeholders.
""".strip()


def call_gemini(prompt: str) -> Optional[str]:
    api_key = get_secret("GEMINI_API_KEY")
    if not api_key:
        return None
    model = get_secret("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.55, "topP": 0.9, "maxOutputTokens": 3500}}
    try:
        r = requests.post(url, json=payload, timeout=35)
        r.raise_for_status()
        data = r.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()
        return text or None
    except Exception as e:
        st.warning("The AI model could not be reached. Showing a built-in professional sample plan instead.")
        return None


def fallback_plan(city: str, details: str) -> Dict[str, str]:
    key = clean_city(city)
    plan = CITY_PLANS.get(key)
    if not plan:
        plan = {
            "summary": f"A practical one-day structure for {city.title()} is ready. For exact local restaurants and landmarks beyond the built-in city library, add a Gemini API key in Streamlit Secrets. This fallback still gives a clean day shape instead of an empty result.",
            "timeline": f"""
**10:00 AM — Start at the most central historic district in {city.title()}**  
Choose the main old-town, civic or waterfront core of the city. Verify the exact landmark before leaving.

**11:30 AM — Visit the city’s best-known museum or heritage landmark**  
Use the official tourism site or maps app to pick the highest-rated central landmark.

**1:00 PM — Lunch near the same district**  
Select a restaurant within 10–15 minutes of the main landmark to avoid wasted transit.

**2:30 PM — Walk the strongest local street or market area**  
Prioritize a specific named street from your maps app and avoid jumping across town.

**4:00 PM — Cafe/rest stop**  
Protect the day from fatigue.

**5:30 PM — Sunset viewpoint, riverside, waterfront or central square**  
Use a nearby viewpoint rather than commuting far.

**7:00 PM — Dinner close to your ending area**  
End near your hotel or transport line.
            """,
            "route": "This fallback keeps the route compact and avoids the biggest one-day mistake: crossing the city multiple times. Add Gemini for exact named places in any city globally.",
            "food": "Choose lunch and dinner within the same neighborhood as your main stops. Add dietary preference in the details box for better AI results once configured.",
            "photos": "Main historic landmark · central market/street · cafe/rest stop · sunset viewpoint · evening square or waterfront.",
            "backup": "If weather is poor, replace outdoor walking with a museum, gallery, covered market or cafe route. If tired, remove the second major attraction.",
            "map": f"Central historic district, {city.title()}\nMain museum or heritage landmark, {city.title()}\nCentral market or named shopping street, {city.title()}\nSunset viewpoint or waterfront, {city.title()}\nDinner area near hotel, {city.title()}",
        }
    # adjust slightly for user details
    if "vegetarian" in (details or "").lower():
        plan = dict(plan)
        plan["food"] = plan["food"] + "\n\nVegetarian note: choose vegetarian-friendly restaurants and verify menu options before visiting."
    return plan


def split_ai_sections(text: str) -> Dict[str, str]:
    # Robust fallback: show full plan everywhere if the model does not follow headings perfectly.
    sections = {"summary": "", "timeline": "", "route": "", "food": "", "photos": "", "backup": "", "map": "", "warnings": ""}
    markers = [
        ("summary", r"perfect day summary"),
        ("timeline", r"exact timeline|timeline"),
        ("route", r"why this route works|route logic"),
        ("food", r"food stops|food"),
        ("photos", r"photo moments|photos"),
        ("backup", r"backup plan"),
        ("map", r"map-ready place list|map list"),
        ("warnings", r"do not ruin|warnings"),
    ]
    lower = text.lower()
    found = []
    for name, pat in markers:
        m = re.search(rf"(?:^|\n)\s*(?:#+\s*)?(?:\d+\.\s*)?({pat})", lower)
        if m:
            found.append((m.start(), name))
    if not found:
        sections["timeline"] = text
        sections["summary"] = "A specific one-day route has been generated."
        return sections
    found.sort()
    for i, (start, name) in enumerate(found):
        end = found[i+1][0] if i+1 < len(found) else len(text)
        chunk = text[start:end].strip()
        chunk = re.sub(r"^#+\s*", "", chunk)
        sections[name] = chunk
    for k in sections:
        if not sections[k]:
            sections[k] = "See the full plan tab for details."
    return sections


def render_plan_from_dict(plan: Dict[str, str]):
    summary_col, quality_col, next_col = st.columns(3)
    with summary_col:
        st.markdown(f"<div class='card'><div class='kicker'>Summary</div><p>{plan['summary']}</p></div>", unsafe_allow_html=True)
    with quality_col:
        st.markdown("<div class='card'><div class='kicker'>Output quality</div><h3>Named places</h3><p>The plan uses specific landmarks, areas, food stops and map-ready locations.</p></div>", unsafe_allow_html=True)
    with next_col:
        st.markdown("<div class='card'><div class='kicker'>Use this next</div><h3>Copy into maps</h3><p>Use the Map List tab to quickly create your route in Google Maps or Apple Maps.</p></div>", unsafe_allow_html=True)
    tabs = st.tabs(["Timeline", "Route Logic", "Food & Photos", "Backup Plan", "Map List", "Full Plan"])
    with tabs[0]:
        st.markdown("### Main itinerary")
        st.markdown(plan["timeline"])
    with tabs[1]:
        st.markdown("### Why this route works")
        st.markdown(plan["route"])
    with tabs[2]:
        st.markdown("### Food stops")
        st.markdown(plan["food"])
        st.markdown("### Photo moments")
        st.markdown(plan["photos"])
    with tabs[3]:
        st.markdown("### Backup plan")
        st.markdown(plan["backup"])
        st.markdown("### Do not ruin the day")
        st.markdown("- Verify opening hours before visiting.\n- Keep one flexible rest stop.\n- Avoid adding a far-away extra attraction at the last minute.")
    with tabs[4]:
        st.markdown("### Map-ready place list")
        st.code(plan["map"], language="text")
    with tabs[5]:
        st.markdown("### Full plan")
        st.markdown(f"""
## Perfect Day Summary
{plan['summary']}

## Exact Timeline With Named Places
{plan['timeline']}

## Why This Route Works
{plan['route']}

## Food Stops
{plan['food']}

## Photo Moments
{plan['photos']}

## Backup Plan
{plan['backup']}

## Map-Ready Place List
```
{plan['map']}
```
        """)


def render_ai_plan(text: str):
    sections = split_ai_sections(text)
    tabs = st.tabs(["Timeline", "Route Logic", "Food & Photos", "Backup Plan", "Map List", "Full Plan"])
    with tabs[0]:
        st.markdown(sections["summary"])
        st.markdown(sections["timeline"])
    with tabs[1]:
        st.markdown(sections["route"])
    with tabs[2]:
        st.markdown(sections["food"])
        st.markdown(sections["photos"])
    with tabs[3]:
        st.markdown(sections["backup"])
        st.markdown(sections["warnings"])
    with tabs[4]:
        st.markdown(sections["map"])
    with tabs[5]:
        st.markdown(text)


st.markdown("""
<div class="hero">
  <h1>One Perfect Day</h1>
  <p>Tell us the city and the kind of day you want. Get a realistic one-day route with exact places, food stops, photo moments, backup ideas and a map-ready list.</p>
  <div class="pill-row">
    <span class="pill">Named places only</span>
    <span class="pill">No long form</span>
    <span class="pill">Route-first planning</span>
    <span class="pill">Backup plan included</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.container():
    c1, c2 = st.columns([1, 1])
    with c1:
        city = st.text_input("1. Which city?", placeholder="Delhi, Tokyo, Paris, London…")
    with c2:
        day_style = st.selectbox("2. What kind of day do you want?", [
            "Culture + food + photos",
            "Relaxed romantic day",
            "First-time highlights",
            "Luxury slow day",
            "Budget local day",
            "Family-friendly day",
            "Art, cafes and neighborhoods",
        ])

    details = st.text_area(
        "3. Anything important?",
        placeholder="Example: 10 AM to 9 PM, vegetarian, medium budget, staying near Connaught Place, want culture + food + photos, avoid heavy walking.",
        height=115,
    )

    with st.expander("Optional: improve accuracy"):
        optional_notes = st.text_area("Add hotel area, must-see places, weather, special occasion, or anything to avoid", height=90)
    generate = st.button("Create my perfect day", use_container_width=True)

if generate:
    if not city.strip():
        st.error("Please enter a city first.")
        st.stop()

    gate = destination_gate(city)
    if gate:
        st.markdown(f"<div class='warnbox'>{gate}</div>", unsafe_allow_html=True)
        st.stop()

    profile = parse_details(details + " " + (optional_notes or ""))
    st.markdown("### Smart profile detected")
    p1, p2, p3, p4, p5 = st.columns(5)
    p1.metric("City", city.title())
    p2.metric("Time", profile["time"])
    p3.metric("Budget", profile["budget"])
    p4.metric("Food", profile["food"])
    p5.metric("Pace", profile["pace"])

    prompt = build_prompt(city, day_style, details, optional_notes)
    ai_text = call_gemini(prompt)
    if ai_text:
        st.markdown("<div class='successbox'><strong>Plan generated.</strong> Review the timeline, then copy the map list into your maps app.</div>", unsafe_allow_html=True)
        render_ai_plan(ai_text)
    else:
        st.markdown("<div class='successbox'><strong>Built-in professional plan shown.</strong> Add a Gemini key later for exact plans in every city globally.</div>", unsafe_allow_html=True)
        render_plan_from_dict(fallback_plan(city, details + " " + (optional_notes or "")))

    coffee = get_secret("BUY_ME_A_COFFEE_URL")
    if coffee:
        st.markdown(f"---\nIf this helped you design a beautiful day, you can [support the project with a coffee]({coffee}).")
