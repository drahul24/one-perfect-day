import json
import math
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st

APP_TITLE = "One Perfect Day"
APP_SUBTITLE = "One city. One day. Exact places. No generic itinerary."

st.set_page_config(page_title=APP_TITLE, page_icon="✨", layout="wide")

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
<style>
:root { --primary:#E94B5F; --ink:#111827; --muted:#667085; --card:#FFFFFF; --line:#E6EAF2; --bg:#F7F8FB; }
html, body, [class*="css"] { font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); }
.stApp { background: radial-gradient(circle at top left, #ffffff 0, #f7f8fb 36%, #eef2f7 100%); }
.block-container { padding-top: 2rem; max-width: 1180px; }
.hero { background: linear-gradient(135deg, #111827 0%, #273244 60%, #4B5563 100%); color: white; padding: 34px 38px; border-radius: 26px; box-shadow: 0 24px 60px rgba(17,24,39,.22); margin-bottom: 24px; }
.hero h1 { font-size: 46px; line-height: 1.04; margin: 0 0 10px 0; letter-spacing: -1.1px; font-weight: 800; }
.hero p { color: #E5E7EB; font-size: 18px; line-height: 1.55; max-width: 780px; margin: 0; }
.pill { display: inline-flex; padding: 8px 12px; border-radius: 999px; font-size: 13px; font-weight: 700; letter-spacing:.02em; margin-bottom: 16px; background: rgba(255,255,255,.12); color: #fff; border: 1px solid rgba(255,255,255,.18); }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 22px; padding: 22px 24px; box-shadow: 0 12px 34px rgba(20,30,50,.08); margin: 14px 0; }
.card h3 { margin: 0 0 12px 0; font-size: 22px; letter-spacing: -.3px; }
.muted { color: var(--muted); font-size: 14px; line-height: 1.6; }
.smallcap { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .16em; font-weight: 800; margin-bottom: 8px; }
.timeline-row { display:grid; grid-template-columns: 128px 1fr; gap:18px; padding: 18px 0; border-bottom: 1px solid #EEF1F6; }
.timeline-row:last-child { border-bottom: none; }
.time { font-weight: 800; color:#E94B5F; font-size: 16px; }
.place { font-weight: 800; font-size: 20px; margin-bottom: 6px; letter-spacing: -.2px; }
.reason { color:#4B5563; font-size:15px; line-height:1.55; }
.warning { background:#FFF7ED; border:1px solid #FED7AA; color:#7C2D12; border-radius:18px; padding:18px 20px; margin:14px 0; }
.safe { background:#ECFDF3; border:1px solid #ABEFC6; color:#064E3B; border-radius:18px; padding:18px 20px; margin:14px 0; }
.stop { background:#F9FAFB; border: 1px solid #EAECF0; border-radius:18px; padding:16px 18px; margin:12px 0; }
.stop b { color:#111827; }
.stButton > button { border-radius: 14px; background: #E94B5F; color: #fff; border: 0; padding: .75rem 1.2rem; font-weight: 800; box-shadow: 0 10px 22px rgba(233,75,95,.22); }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { border-radius: 14px !important; }
[data-testid="stTabs"] button { font-weight: 700; font-size: 16px; }
code { background:#111827 !important; color:#F9FAFB !important; border-radius: 8px; padding: 3px 7px; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Data structures
# -----------------------------
@dataclass
class Stop:
    time: str
    name: str
    reason: str
    kind: str = "place"

@dataclass
class PerfectDay:
    city: str
    summary: str
    timeline: List[Stop]
    route_logic: str
    food: List[str]
    photos: List[str]
    backup: List[str]
    map_list: List[str]
    warnings: List[str]
    source_note: str

# -----------------------------
# Curated plans: high quality fallback
# -----------------------------
CURATED: Dict[str, PerfectDay] = {
    "delhi": PerfectDay(
        city="Delhi",
        summary="A rich but realistic Delhi day around Mughal architecture, Lodhi-era calm, central dining, and a beautiful sunset finish without bouncing all over NCR.",
        timeline=[
            Stop("9:30 AM", "Humayun’s Tomb", "Start with Delhi’s most graceful Mughal monument while the light is soft and crowds are lighter."),
            Stop("11:15 AM", "Sunder Nursery", "Walk next door for gardens, restored monuments, and a calmer photo-friendly break."),
            Stop("12:45 PM", "Khan Market", "Move to a compact dining and cafe area instead of wasting time crossing the city."),
            Stop("2:15 PM", "Lodhi Garden", "A low-pressure green stop with tombs, shaded walking paths, and strong photography moments."),
            Stop("4:00 PM", "India Habitat Centre / Lodhi Art District", "Choose culture or murals depending on energy; both sit close to Lodhi Garden."),
            Stop("5:45 PM", "India Gate / Kartavya Path", "Use this as the golden-hour city landmark moment."),
            Stop("7:15 PM", "Indian Accent or Havemore Pandara Road", "Pick Indian Accent for a premium dinner, or Pandara Road for a classic Delhi food ending."),
        ],
        route_logic="This route stays largely in central-south Delhi: Nizamuddin, Lodhi, Khan Market, India Gate and Pandara Road. It avoids Old Delhi traffic and long cross-city jumps.",
        food=["Khan Market: Perch Wine & Coffee Bar, The Big Chill, Green Mantis", "Pandara Road: Havemore or Gulati", "Premium option: Indian Accent, Lodhi Road"],
        photos=["Humayun’s Tomb central arch", "Sunder Nursery gardens", "Lodhi Garden tombs", "Lodhi Art District murals", "India Gate at golden hour"],
        backup=["If it is too hot, replace Lodhi Garden with National Gallery of Modern Art.", "If traffic is heavy, skip India Gate and end around Khan Market/Lodhi Road.", "If you want Old Delhi, make it a separate half-day, not part of this route."],
        map_list=["Humayun’s Tomb", "Sunder Nursery", "Khan Market", "Lodhi Garden", "Lodhi Art District", "India Gate", "Pandara Road Market"],
        warnings=["Do not mix Old Delhi, Qutub Minar and India Gate in the same relaxed day.", "Verify monument opening hours and ticket rules before leaving.", "Plan buffer time for traffic after 5 PM."],
        source_note="Curated built-in plan",
    ),
    "colombo": PerfectDay(
        city="Colombo",
        summary="A compact Colombo day with colonial architecture, seafront walking, Sri Lankan food, shopping, and sunset without pretending the city needs an overloaded schedule.",
        timeline=[
            Stop("9:30 AM", "Gangaramaya Temple", "Begin with one of Colombo’s most distinctive cultural landmarks."),
            Stop("10:45 AM", "Seema Malaka Temple", "A short hop from Gangaramaya, giving you a calm lake-side architectural moment."),
            Stop("11:45 AM", "Colombo National Museum", "Add one strong heritage stop before lunch, without overloading the morning."),
            Stop("1:15 PM", "Upali’s by Nawaloka", "A reliable Sri Lankan lunch option close enough to the morning route."),
            Stop("2:45 PM", "Barefoot Gallery", "A polished local design, textile, books and cafe stop — better than vague 'shopping'."),
            Stop("4:15 PM", "Dutch Hospital Shopping Precinct", "Move toward Fort for restored colonial architecture, cafes and easy walking."),
            Stop("5:45 PM", "Galle Face Green", "End the day with the city’s classic seaside sunset walk."),
            Stop("7:15 PM", "Ministry of Crab or The Gallery Café", "Choose Ministry of Crab for a splurge, Gallery Café for a stylish dinner."),
        ],
        route_logic="This route moves from central cultural stops to design/shopping and then the seafront. It avoids zig-zagging across Colombo and keeps sunset near the coast.",
        food=["Upali’s by Nawaloka", "Ministry of Crab", "The Gallery Café", "Barefoot Garden Café"],
        photos=["Seema Malaka over Beira Lake", "National Museum facade", "Barefoot Gallery courtyard", "Dutch Hospital arches", "Galle Face Green at sunset"],
        backup=["If it rains, spend more time at Colombo National Museum and Barefoot Gallery.", "If you want a slower day, skip Dutch Hospital and go directly to Galle Face Green.", "If you want more shopping, add Odel Alexandra Place."],
        map_list=["Gangaramaya Temple", "Seema Malaka Temple", "Colombo National Museum", "Upali’s by Nawaloka", "Barefoot Gallery", "Dutch Hospital Shopping Precinct", "Galle Face Green", "Ministry of Crab", "The Gallery Café"],
        warnings=["Do not overpack Colombo with faraway beach towns in a one-day city plan.", "Verify restaurant reservations for Ministry of Crab.", "Keep sunset timing flexible because traffic can slow down late afternoon moves."],
        source_note="Curated built-in plan",
    ),
    "tokyo": PerfectDay(
        city="Tokyo",
        summary="A western Tokyo day built around shrine calm, design streets, gardens, skyline views and an atmospheric Shinjuku evening.",
        timeline=[
            Stop("10:00 AM", "Meiji Shrine", "Start with Tokyo’s calm forested shrine before Harajuku becomes too busy."),
            Stop("11:15 AM", "Takeshita Street", "A short walk for youth culture, snacks, and high-energy street photos."),
            Stop("12:15 PM", "Omotesando", "Shift into elegant architecture, boutiques and cafes for a smoother pace."),
            Stop("1:15 PM", "Ain Soph Journey Shinjuku", "A reliable vegetarian-friendly lunch option."),
            Stop("2:45 PM", "Shinjuku Gyoen National Garden", "A calm recovery block with beautiful seasonal scenery."),
            Stop("5:30 PM", "Tokyo Metropolitan Government Building Observatory", "Free skyline view and a strong sunset option."),
            Stop("7:15 PM", "Omoide Yokocho", "Atmospheric evening lanes near Shinjuku Station; easy to end the day."),
        ],
        route_logic="The route stays in Harajuku, Omotesando and Shinjuku, reducing train transfers and keeping the day coherent.",
        food=["Ain Soph Journey Shinjuku", "Brown Rice by Neal’s Yard Remedies", "Mr. Farmer Omotesando", "Omoide Yokocho for evening atmosphere"],
        photos=["Meiji Shrine forest approach", "Takeshita Street entrance", "Omotesando architecture", "Shinjuku Gyoen seasonal gardens", "Tokyo Metropolitan Government Building skyline"],
        backup=["If it rains, replace Shinjuku Gyoen with Mori Art Museum or The National Art Center, Tokyo.", "If Harajuku is too crowded, switch to Daikanyama and Nakameguro.", "If tired, skip Takeshita Street and spend more time in Omotesando."],
        map_list=["Meiji Shrine", "Takeshita Street", "Omotesando", "Ain Soph Journey Shinjuku", "Shinjuku Gyoen National Garden", "Tokyo Metropolitan Government Building Observatory", "Omoide Yokocho"],
        warnings=["Do not combine east Tokyo and west Tokyo in a relaxed one-day plan.", "Verify Shinjuku Gyoen opening days.", "Book restaurants ahead if dietary needs are strict."],
        source_note="Curated built-in plan",
    ),
    "paris": PerfectDay(
        city="Paris",
        summary="A left-bank-to-Seine day with one major museum, elegant streets, strong food moments and a golden-hour Eiffel view.",
        timeline=[
            Stop("9:30 AM", "Musée d’Orsay", "Start with a world-class museum that is easier to manage than trying to conquer the Louvre in one day."),
            Stop("11:30 AM", "Saint-Germain-des-Prés", "Walk through one of Paris’s most atmospheric neighborhoods."),
            Stop("12:45 PM", "Le Relais de l’Entrecôte or Le Grenier de Notre-Dame", "Choose classic steak-frites or a vegetarian-friendly Paris option."),
            Stop("2:15 PM", "Jardin du Luxembourg", "A beautiful rest and photo stop after lunch."),
            Stop("4:00 PM", "Île de la Cité and Notre-Dame exterior", "Add a central historic moment without overloading the day."),
            Stop("5:45 PM", "Pont Alexandre III", "One of the best golden-hour bridge views in Paris."),
            Stop("7:30 PM", "Rue Cler or Saint-Germain dinner", "End with a walkable dinner area rather than chasing another faraway attraction."),
        ],
        route_logic="This day keeps you around the Left Bank, central islands and the Seine, avoiding excessive Metro jumps.",
        food=["Le Grenier de Notre-Dame", "Café de Flore", "Le Relais de l’Entrecôte", "Rue Cler restaurants"],
        photos=["Musée d’Orsay clock area", "Saint-Germain side streets", "Jardin du Luxembourg chairs", "Notre-Dame exterior", "Pont Alexandre III at golden hour"],
        backup=["If it rains, add Musée de l’Orangerie instead of the bridge walk.", "If museum tickets are unavailable, switch Musée d’Orsay to Musée de l’Orangerie.", "If tired, skip Île de la Cité and keep the evening near Saint-Germain."],
        map_list=["Musée d’Orsay", "Saint-Germain-des-Prés", "Le Grenier de Notre-Dame", "Jardin du Luxembourg", "Notre-Dame de Paris", "Pont Alexandre III", "Rue Cler"],
        warnings=["Do not try to do Louvre, Eiffel Tower summit and Versailles in one day.", "Book museum tickets ahead.", "Keep valuables secure in dense tourist areas."],
        source_note="Curated built-in plan",
    ),
    "london": PerfectDay(
        city="London",
        summary="A classic London day with Westminster icons, the South Bank, Borough Market, Tate Modern and a polished evening finish.",
        timeline=[
            Stop("9:30 AM", "Westminster Bridge", "Start with Big Ben, Parliament and Thames views in one compact location."),
            Stop("10:15 AM", "Westminster Abbey exterior / St James’s Park", "Choose heritage or a calmer green walk depending on energy."),
            Stop("11:30 AM", "Trafalgar Square and The National Gallery", "A central art-and-landmark pairing with no long commute."),
            Stop("1:00 PM", "Borough Market", "A strong food stop with variety and atmosphere."),
            Stop("2:30 PM", "Tate Modern", "Add a major cultural stop on the same South Bank route."),
            Stop("4:30 PM", "Millennium Bridge to St Paul’s Cathedral", "One of London’s best short city walks."),
            Stop("6:30 PM", "Covent Garden", "Dinner, street performance and a lively but easy evening end."),
        ],
        route_logic="The plan follows Westminster to South Bank and Covent Garden, keeping transit simple and the city story coherent.",
        food=["Borough Market", "Dishoom Covent Garden", "Flat Iron Covent Garden", "The Blacklock Covent Garden"],
        photos=["Westminster Bridge", "Trafalgar Square lions", "Borough Market stalls", "Tate Modern riverside", "Millennium Bridge toward St Paul’s"],
        backup=["If it rains, spend more time inside The National Gallery and Tate Modern.", "If Borough Market is too crowded, use Flat Iron Square or South Bank Centre food options.", "If tired, skip St Paul’s and go directly to Covent Garden."],
        map_list=["Westminster Bridge", "St James’s Park", "Trafalgar Square", "The National Gallery", "Borough Market", "Tate Modern", "Millennium Bridge", "St Paul’s Cathedral", "Covent Garden"],
        warnings=["Do not add Windsor, Greenwich and Camden to the same one-day plan.", "Check Tube disruptions before moving across town.", "Book popular restaurants ahead."],
        source_note="Curated built-in plan",
    ),
}

# Add a few aliases
ALIASES = {
    "new delhi": "delhi",
    "tokyo japan": "tokyo",
    "paris france": "paris",
    "london uk": "london",
    "london england": "london",
    "colombo sri lanka": "colombo",
}

UNSUITABLE_DESTINATIONS = {
    "north korea": "Independent leisure planning is not appropriate for this destination. Tourism access is highly restricted and normal self-guided day planning may be unavailable.",
    "pyongyang": "Independent leisure planning is not appropriate for this destination. Tourism access is highly restricted and normal self-guided day planning may be unavailable.",
    "gaza": "A normal leisure itinerary is not appropriate for this destination at this time. Verify official guidance and humanitarian/security conditions before any travel planning.",
    "syria": "A normal leisure itinerary is not appropriate for this destination at this time. Verify official guidance before any travel planning.",
    "yemen": "A normal leisure itinerary is not appropriate for this destination at this time. Verify official guidance before any travel planning.",
    "afghanistan": "A normal leisure itinerary is not appropriate for this destination at this time. Verify official guidance before any travel planning.",
}

# -----------------------------
# Helpers
# -----------------------------
def clean_key(city: str) -> str:
    key = re.sub(r"\s+", " ", city.strip().lower())
    return ALIASES.get(key, key)


def infer_profile(kind_of_day: str, details: str) -> Dict[str, str]:
    text = f"{kind_of_day} {details}".lower()
    profile = {
        "start": "10:00 AM",
        "end": "8:00 PM",
        "budget": "medium",
        "food": "flexible",
        "energy": "moderate",
        "companions": "solo/couple",
    }
    m = re.search(r"(\d{1,2}\s*(?::\d{2})?\s*(?:am|pm))", text)
    if m:
        profile["start"] = m.group(1).upper().replace(" ", "")
    if "vegetarian" in text or "veg" in text:
        profile["food"] = "vegetarian"
    if "vegan" in text:
        profile["food"] = "vegan"
    if "budget" in text or "cheap" in text:
        profile["budget"] = "budget-conscious"
    if "luxury" in text or "premium" in text:
        profile["budget"] = "premium"
    if "relaxed" in text or "slow" in text:
        profile["energy"] = "relaxed"
    if "high energy" in text or "packed" in text:
        profile["energy"] = "high"
    if "couple" in text or "wife" in text or "husband" in text or "partner" in text:
        profile["companions"] = "couple"
    if "family" in text or "kids" in text or "children" in text:
        profile["companions"] = "family"
    return profile


def haversine(lat1, lon1, lat2, lon2):
    r = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@st.cache_data(ttl=86400, show_spinner=False)
def geocode_city(city: str) -> Optional[Dict]:
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city, "format": "json", "limit": 1, "addressdetails": 1}
        headers = {"User-Agent": "OnePerfectDay/1.0 (streamlit demo)"}
        r = requests.get(url, params=params, headers=headers, timeout=12)
        r.raise_for_status()
        data = r.json()
        return data[0] if data else None
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def overpass_places(lat: float, lon: float, radius: int = 6500) -> List[Dict]:
    query = f"""
    [out:json][timeout:20];
    (
      node(around:{radius},{lat},{lon})[tourism~"museum|attraction|viewpoint|gallery"]['name'];
      node(around:{radius},{lat},{lon})[historic]['name'];
      node(around:{radius},{lat},{lon})[leisure~"park|garden"]['name'];
      node(around:{radius},{lat},{lon})[amenity~"restaurant|cafe|marketplace"]['name'];
      node(around:{radius},{lat},{lon})[shop~"mall|department_store|supermarket"]['name'];
      way(around:{radius},{lat},{lon})[tourism~"museum|attraction|viewpoint|gallery"]['name'];
      way(around:{radius},{lat},{lon})[historic]['name'];
      way(around:{radius},{lat},{lon})[leisure~"park|garden"]['name'];
      way(around:{radius},{lat},{lon})[amenity~"restaurant|cafe|marketplace"]['name'];
      relation(around:{radius},{lat},{lon})[tourism~"museum|attraction|viewpoint|gallery"]['name'];
      relation(around:{radius},{lat},{lon})[historic]['name'];
      relation(around:{radius},{lat},{lon})[leisure~"park|garden"]['name'];
    );
    out center tags 80;
    """
    try:
        r = requests.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=28)
        r.raise_for_status()
        elements = r.json().get("elements", [])
    except Exception:
        return []

    places = []
    seen = set()
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name or name.lower() in seen:
            continue
        plat = el.get("lat") or el.get("center", {}).get("lat")
        plon = el.get("lon") or el.get("center", {}).get("lon")
        if plat is None or plon is None:
            continue
        seen.add(name.lower())
        category = "place"
        if tags.get("amenity") in ["restaurant", "cafe", "marketplace"]:
            category = "food"
        elif tags.get("tourism") in ["museum", "gallery"] or tags.get("historic"):
            category = "culture"
        elif tags.get("tourism") in ["viewpoint", "attraction"]:
            category = "attraction"
        elif tags.get("leisure") in ["park", "garden"]:
            category = "park"
        elif tags.get("shop"):
            category = "shopping"
        places.append({
            "name": name,
            "category": category,
            "lat": float(plat),
            "lon": float(plon),
            "dist": haversine(lat, lon, float(plat), float(plon)),
        })
    places.sort(key=lambda p: p["dist"])
    return places


def pick(places: List[Dict], categories: List[str], used: set) -> Optional[Dict]:
    for cat in categories:
        for p in places:
            if p["category"] == cat and p["name"].lower() not in used:
                used.add(p["name"].lower())
                return p
    for p in places:
        if p["name"].lower() not in used:
            used.add(p["name"].lower())
            return p
    return None


def make_osm_plan(city: str, profile: Dict[str, str]) -> Optional[PerfectDay]:
    geo = geocode_city(city)
    if not geo:
        return None
    lat, lon = float(geo["lat"]), float(geo["lon"])
    places = overpass_places(lat, lon)
    # Require at least 5 named places to avoid generic output
    if len(places) < 5:
        return None
    used = set()
    p1 = pick(places, ["culture", "attraction", "park"], used)
    p2 = pick(places, ["attraction", "shopping", "culture"], used)
    lunch = pick(places, ["food"], used)
    p4 = pick(places, ["park", "culture", "attraction"], used)
    sunset = pick(places, ["attraction", "park"], used)
    dinner = pick(places, ["food"], used)
    selected = [x for x in [p1, p2, lunch, p4, sunset, dinner] if x]
    if len(selected) < 5:
        return None

    timeline = []
    times = [profile.get("start", "10:00 AM"), "11:30 AM", "1:00 PM", "2:45 PM", "5:15 PM", "7:00 PM"]
    labels = [
        "Start with a central landmark that anchors the day.",
        "Move to a second nearby named stop instead of crossing the city too early.",
        "Use this as your lunch/rest point.",
        "Add a slower culture, park or neighborhood stop after lunch.",
        "Use this as the late-afternoon photo or sunset moment.",
        "End with food close to the same route so the day does not collapse into transit.",
    ]
    for t, p, reason in zip(times, selected, labels):
        timeline.append(Stop(t, p["name"], reason, p["category"]))

    food = [p["name"] for p in places if p["category"] == "food"][:5]
    if not food:
        food = [selected[2]["name"]] if len(selected) > 2 else []
    photos = [f"{p['name']} — best for {p['category']} shots" for p in selected[:5]]
    map_list = [p["name"] for p in selected]
    route_logic = f"The plan uses named places found in central {city} public map data and keeps the day compact. Verify opening hours and current access before leaving."
    return PerfectDay(
        city=city,
        summary=f"A specific one-day plan for {city} using named places from public map data, designed to avoid vague suggestions and unnecessary cross-city jumps.",
        timeline=timeline,
        route_logic=route_logic,
        food=food,
        photos=photos,
        backup=[
            f"If one stop is closed, replace it with another named place from the Map List tab in the same area of {city}.",
            "If weather is poor, prioritize museums, galleries, cafes and indoor markets from the plan.",
            "If energy drops, keep the first three stops and skip the late-afternoon add-on.",
        ],
        map_list=map_list,
        warnings=[
            "Verify opening hours, tickets and current access before visiting.",
            "Do not add distant attractions unless they are close to your hotel or ending point.",
            "Keep one meal and one rest stop protected so the day stays enjoyable.",
        ],
        source_note="Live public map data fallback",
    )


def try_gemini_plan(city: str, kind_of_day: str, details: str, profile: Dict[str, str]) -> Optional[str]:
    key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    if not key:
        return None
    try:
        import google.generativeai as genai
        model_name = st.secrets.get("GEMINI_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
        genai.configure(api_key=key)
        model = genai.GenerativeModel(model_name)
        prompt = f"""
Create ONE perfect day in {city}.

User wants: {kind_of_day}
Details: {details}
Profile: {json.dumps(profile)}

Rules:
- Give exact named places only.
- Never say 'shopping street', 'cultural area', 'restaurant', 'museum', or 'market' without naming the exact place.
- Build a realistic timeline from start to end.
- Keep route compact and explain why it works.
- Include food stops, photo moments, rainy/low-energy backup, map-ready list, and warnings.
- Do not invent opening hours. Say verify opening hours if needed.

Return concise, polished Markdown with headings:
Summary, Timeline, Route Logic, Food & Photos, Backup Plan, Map List, Do Not Ruin The Day.
"""
        resp = model.generate_content(prompt)
        return getattr(resp, "text", None)
    except Exception:
        return None


def render_day(day: PerfectDay):
    st.markdown(f"<div class='safe'><b>{day.city} plan generated.</b> {day.summary}<br><span class='muted'>Mode: {day.source_note}</span></div>", unsafe_allow_html=True)
    tabs = st.tabs(["Timeline", "Route Logic", "Food & Photos", "Backup Plan", "Map List", "Full Plan"])
    with tabs[0]:
        st.markdown("<div class='card'><div class='smallcap'>Main itinerary</div><h3>Exact timeline with named places</h3>", unsafe_allow_html=True)
        for stop in day.timeline:
            st.markdown(
                f"<div class='timeline-row'><div class='time'>{stop.time}</div><div><div class='place'>{stop.name}</div><div class='reason'>{stop.reason}</div></div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    with tabs[1]:
        st.markdown(f"<div class='card'><div class='smallcap'>Why this works</div><h3>Route logic</h3><p>{day.route_logic}</p></div>", unsafe_allow_html=True)
    with tabs[2]:
        st.markdown("<div class='card'><div class='smallcap'>Food</div><h3>Specific food stops</h3>", unsafe_allow_html=True)
        for item in day.food:
            st.markdown(f"<div class='stop'>{item}</div>", unsafe_allow_html=True)
        st.markdown("<div class='smallcap' style='margin-top:18px;'>Photos</div><h3>Photo moments</h3>", unsafe_allow_html=True)
        for item in day.photos:
            st.markdown(f"<div class='stop'>{item}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with tabs[3]:
        st.markdown("<div class='card'><div class='smallcap'>Backup</div><h3>If the day changes</h3>", unsafe_allow_html=True)
        for item in day.backup:
            st.markdown(f"<div class='stop'>{item}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with tabs[4]:
        map_text = "\n".join(day.map_list)
        st.markdown("<div class='card'><div class='smallcap'>Copy into maps</div><h3>Map-ready place list</h3>", unsafe_allow_html=True)
        st.code(map_text)
        st.markdown("</div>", unsafe_allow_html=True)
    with tabs[5]:
        full = [f"# One Perfect Day in {day.city}", day.summary, "\n## Timeline"]
        for s in day.timeline:
            full.append(f"- {s.time} — {s.name}: {s.reason}")
        full += ["\n## Route Logic", day.route_logic, "\n## Food", *[f"- {x}" for x in day.food], "\n## Photos", *[f"- {x}" for x in day.photos], "\n## Backup", *[f"- {x}" for x in day.backup], "\n## Map List", *[f"- {x}" for x in day.map_list], "\n## Do Not Ruin The Day", *[f"- {x}" for x in day.warnings]]
        st.text_area("Copy your plan", "\n".join(full), height=420)
    st.markdown("<div class='warning'><b>Before you go:</b> Verify opening hours, tickets, holidays, transport disruptions and weather before visiting. This is a planning assistant, not an official city guide.</div>", unsafe_allow_html=True)


def render_markdown_plan(text: str):
    st.markdown("<div class='safe'><b>AI plan generated.</b> Check opening hours and route timing before visiting.</div>", unsafe_allow_html=True)
    st.markdown(text)

# -----------------------------
# App UI
# -----------------------------
st.markdown(
    f"""
<div class='hero'>
  <div class='pill'>Specific city planning</div>
  <h1>{APP_TITLE}</h1>
  <p>{APP_SUBTITLE} Tell us the city and the kind of day you want. The result must include named places, food stops, photo moments and a map-ready list.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.container():
    col1, col2 = st.columns([0.9, 1.1], gap="large")
    with col1:
        st.markdown("<div class='card'><div class='smallcap'>Step 1</div><h3>Which city?</h3>", unsafe_allow_html=True)
        city = st.text_input("City", placeholder="Example: Colombo, Tokyo, Delhi, Paris", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><div class='smallcap'>Step 2</div><h3>What kind of day do you want?</h3>", unsafe_allow_html=True)
        kind_of_day = st.text_input("Style", placeholder="Example: culture + food + photos, relaxed, medium budget", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'><div class='smallcap'>Step 3</div><h3>Anything important?</h3>", unsafe_allow_html=True)
details = st.text_area(
    "Details",
    placeholder="Example: 10 AM to 8 PM, vegetarian, staying near Fort, avoid heavy walking, want sunset and one beautiful dinner.",
    height=110,
    label_visibility="collapsed",
)
st.markdown("<p class='muted'>Keep it natural. You do not need to fill a long form.</p></div>", unsafe_allow_html=True)

go = st.button("Create my perfect day", use_container_width=True)

if go:
    if not city.strip():
        st.error("Please enter a city first.")
        st.stop()

    key = clean_key(city)
    for blocked, msg in UNSUITABLE_DESTINATIONS.items():
        if blocked in key:
            st.markdown(f"<div class='warning'><b>Leisure itinerary paused.</b><br>{msg}<br><br>Please verify official travel guidance before planning. Consider choosing a safer nearby alternative city.</div>", unsafe_allow_html=True)
            st.stop()

    profile = infer_profile(kind_of_day, details)
    with st.spinner("Finding named places and building your day..."):
        ai_text = try_gemini_plan(city, kind_of_day, details, profile)
        if ai_text:
            render_markdown_plan(ai_text)
        else:
            day = CURATED.get(key)
            if not day:
                day = make_osm_plan(city, profile)
            if day:
                render_day(day)
            else:
                st.markdown(
                    f"<div class='warning'><b>I could not find enough reliable named places for {city}.</b><br>Try adding a more specific city/area, such as 'Colombo Fort', 'South Delhi', or 'Shinjuku Tokyo'. You can also add a Gemini key for richer global coverage.</div>",
                    unsafe_allow_html=True,
                )

coffee = st.secrets.get("BUY_ME_A_COFFEE_URL", os.getenv("BUY_ME_A_COFFEE_URL", ""))
if coffee:
    st.link_button("Support this free project", coffee)
