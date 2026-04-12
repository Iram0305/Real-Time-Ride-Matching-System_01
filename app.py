# app.py — RideSync: Real-Time Road-Based Ride Matching System
# Tech: KD-Tree + Priority Queue + OpenRouteService Road Routing

import streamlit as st
import pydeck as pdk
import random
import requests
import time
import math
from streamlit_geolocation import streamlit_geolocation
from models import Driver, Passenger
from matcher import MatchingEngine

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="RideSync — Real-Time Ride Matching",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CSS — DARK PREMIUM THEME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* === ROOT === */
.stApp {
    background: linear-gradient(160deg, #0b0f1a 0%, #111827 50%, #0f172a 100%);
    font-family: 'Inter', sans-serif !important;
}
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, .stDeployButton { display: none !important; visibility: hidden !important; }

/* === TEXT COLORS === */
h1, h2, h3, h4 { color: #f1f5f9 !important; font-family: 'Inter', sans-serif !important; }
p, li, span, label { color: #cbd5e1 !important; font-family: 'Inter', sans-serif !important; }
.stMarkdown p { color: #cbd5e1; }

/* === HERO === */
.hero-box {
    padding: 30px 0 10px 0;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: -1.5px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 30%, #f093fb 70%, #667eea 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: heroGrad 5s ease infinite;
    line-height: 1.1;
}
.hero-sub {
    color: #94a3b8 !important;
    font-size: 0.95rem;
    margin-top: 6px;
    font-weight: 400;
}
@keyframes heroGrad {
    0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}
}

/* === DIVIDER === */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(102,126,234,0.35) 30%, rgba(118,75,162,0.35) 70%, transparent 100%);
    margin: 24px 0;
}

/* === SECTION TITLE === */
.sec-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f0 !important;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* === LIVE LOCATION PILL === */
.loc-pill {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(102,126,234,0.1);
    border: 1px solid rgba(102,126,234,0.2);
    border-radius: 999px;
    padding: 8px 20px;
    margin-top: 8px;
}
.loc-pill .pulse-dot {
    width: 10px; height: 10px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse 1.8s ease-in-out infinite;
    box-shadow: 0 0 6px rgba(34,197,94,0.5);
}
.loc-pill .loc-text {
    font-size: 0.85rem;
    color: #818cf8 !important;
    font-weight: 600;
    letter-spacing: 0.3px;
}
@keyframes pulse {
    0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.4;transform:scale(0.8)}
}

/* === GLASS CARD === */
.glass {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 12px;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.glass:hover {
    border-color: rgba(102,126,234,0.2);
    box-shadow: 0 4px 20px rgba(102,126,234,0.06);
}

/* === METRIC CARD === */
.metric {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 18px 14px;
    text-align: center;
    transition: all 0.25s ease;
}
.metric:hover {
    border-color: rgba(102,126,234,0.25);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102,126,234,0.08);
}
.metric .m-icon { font-size: 1.5rem; margin-bottom: 4px; }
.metric .m-val {
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric .m-lbl {
    font-size: 0.68rem;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 700;
    margin-top: 4px;
}

/* === BADGES === */
.badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.b-green  { background:rgba(34,197,94,0.12);  color:#4ade80; border:1px solid rgba(34,197,94,0.25); }
.b-yellow { background:rgba(234,179,8,0.12);  color:#facc15; border:1px solid rgba(234,179,8,0.25); }
.b-blue   { background:rgba(99,102,241,0.12); color:#818cf8; border:1px solid rgba(99,102,241,0.25); }
.b-red    { background:rgba(239,68,68,0.12);  color:#f87171; border:1px solid rgba(239,68,68,0.25); }

/* === PROGRESS BAR === */
.prog-track {
    width: 100%;
    height: 10px;
    background: rgba(255,255,255,0.06);
    border-radius: 99px;
    overflow: hidden;
    margin: 10px 0;
}
.prog-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #667eea, #8b5cf6, #d946ef);
    background-size: 200% 100%;
    animation: shimmer 2.5s ease infinite;
    transition: width 0.5s ease;
}
@keyframes shimmer {
    0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}
}

/* === TRACKING BOX === */
.track-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.06), rgba(139,92,246,0.06));
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 14px;
    padding: 20px;
    margin-top: 10px;
}
.track-status {
    font-size: 1.05rem;
    font-weight: 700;
    color: #e2e8f0 !important;
    margin-bottom: 4px;
}
.track-sub {
    font-size: 0.82rem;
    color: #94a3b8 !important;
}

/* === ARRIVAL CELEBRATION === */
.arrived {
    background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(74,222,128,0.05));
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 14px;
    padding: 24px;
    text-align: center;
    animation: arrive-pulse 2s ease-in-out infinite;
    margin-top: 12px;
}
@keyframes arrive-pulse {
    0%,100%{border-color:rgba(34,197,94,0.25)}50%{border-color:rgba(34,197,94,0.6)}
}

/* === TRAFFIC WARN === */
.traffic-note {
    background: rgba(234,179,8,0.08);
    border: 1px solid rgba(234,179,8,0.18);
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 0.82rem;
    color: #facc15 !important;
    font-weight: 500;
    margin-bottom: 12px;
}

/* === DRIVER INFO STRIP === */
.driver-strip {
    background: linear-gradient(135deg, rgba(99,102,241,0.05), rgba(139,92,246,0.05));
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 14px;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 14px;
}

/* === DRIVER MINI CARD === */
.drv-mini {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 10px;
    text-align: center;
    transition: all 0.2s ease;
}
.drv-mini:hover {
    border-color: rgba(99,102,241,0.2);
}

/* === STREAMLIT WIDGET OVERRIDES === */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 14px 32px !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.3px;
}
.stButton > button:hover {
    box-shadow: 0 8px 28px rgba(102,126,234,0.35) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}
.stCheckbox label span {
    color: #cbd5e1 !important;
    font-weight: 500 !important;
}
div[data-testid="stCheckbox"] {
    padding: 4px 0;
}
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  API KEY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjI1NDI4Y2I3NmM3NjQyM2JhZmRkY2ZhNzEwNjc0YzE3IiwiaCI6Im11cm11cjY0In0="


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SESSION STATE INIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STATE_DEFAULTS = {
    "engine": None,
    "best_driver": None,
    "passenger": None,
    "route_coords": None,
    "route_index": 0,
    "live_tracking": False,
    "road_distance": None,
    "road_time": None,
    "center_lat": 19.0760,
    "center_lon": 72.8777,
    "show_traffic": True,
    "route_traffic_segments": None,
    "total_route_coords": 0,
    "ride_requested": False,
    "last_gps_lat": None,
    "last_gps_lon": None,
}
for key, default in STATE_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Create engine if needed
if st.session_state.engine is None:
    st.session_state.engine = MatchingEngine()

engine = st.session_state.engine


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon points in km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_road_route(start_latlon, end_latlon):
    """
    Get a driving route that follows actual roads.
    Priority: OSRM (free, no key) → ORS → straight-line fallback.
    Returns (coords_list_of_[lon,lat], dist_km, dur_min).
    """
    # --- 1) Try OSRM (free, no API key, follows real roads) ---
    try:
        osrm_url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{start_latlon[1]},{start_latlon[0]};{end_latlon[1]},{end_latlon[0]}"
            f"?overview=full&geometries=geojson"
        )
        resp = requests.get(osrm_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "Ok" and data.get("routes"):
                route = data["routes"][0]
                coords = route["geometry"]["coordinates"]  # [[lon,lat], ...]
                dist_km = route["distance"] / 1000
                dur_min = route["duration"] / 60
                return coords, dist_km, dur_min
    except Exception:
        pass

    # --- 2) Try ORS ---
    try:
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
        body = {"coordinates": [
            [start_latlon[1], start_latlon[0]],
            [end_latlon[1], end_latlon[0]],
        ]}
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            coords = data["features"][0]["geometry"]["coordinates"]
            dist_km = data["features"][0]["properties"]["summary"]["distance"] / 1000
            dur_min = data["features"][0]["properties"]["summary"]["duration"] / 60
            return coords, dist_km, dur_min
    except Exception:
        pass

    # --- 3) Straight-line fallback ---
    st.warning("⚠️ Could not connect to routing services. Using straight-line route.")
    coords = []
    for i in range(50):
        t = i / 49
        lat = start_latlon[0] + t * (end_latlon[0] - start_latlon[0])
        lon = start_latlon[1] + t * (end_latlon[1] - start_latlon[1])
        coords.append([lon, lat])
    dist_km = haversine_km(*start_latlon, *end_latlon)
    dur_min = (dist_km / 30) * 60
    return coords, dist_km, dur_min


def build_route_traffic(route_coords):
    """
    Split the route into segments and assign each a traffic color + condition.
    Returns a list of dicts: {'path', 'color', 'condition', 'start_idx', 'end_idx'}.
    The start/end indices let us look up traffic at any route position.
    """
    if not route_coords or len(route_coords) < 2:
        return []

    COLORS = {
        "free":     [0, 175, 80, 230],     # green
        "moderate": [255, 195, 0, 230],    # yellow
        "slow":     [255, 110, 0, 230],    # orange
        "heavy":    [215, 35, 35, 230],    # red
    }

    n = len(route_coords)
    chunk_size = max(3, n // 12)
    segments = []

    for i in range(0, n - 1, chunk_size):
        end_i = min(i + chunk_size, n - 1)
        chunk = route_coords[i : end_i + 1]
        if len(chunk) < 2:
            continue
        condition = random.choices(
            ["free", "moderate", "slow", "heavy"],
            weights=[45, 28, 17, 10],
            k=1,
        )[0]
        segments.append({
            "path": chunk,
            "color": COLORS[condition],
            "condition": condition,
            "start_idx": i,
            "end_idx": end_i,
        })

    return segments


def get_traffic_at_index(segments, idx):
    """Look up the traffic condition at a given route index."""
    if not segments:
        return "free"
    for seg in segments:
        if seg["start_idx"] <= idx <= seg["end_idx"]:
            return seg["condition"]
    return "free"


# Speed multiplier: how many route coords to advance per tick
# free=fast, heavy=very slow
TRAFFIC_SPEED = {
    "free": 2,       # 2 coordinates per tick
    "moderate": 1,   # 1 coordinate per tick
    "slow": 1,       # 1 coordinate per tick
    "heavy": 1,      # 1 coordinate per tick (+ longer delay at rerun)
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SPAWN DRIVERS (once)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if len(engine.drivers) < 5:
    for i in range(1, 6):
        d = Driver(
            driver_id=f"Driver_{i}",
            x=st.session_state.center_lat + random.uniform(-0.02, 0.02),
            y=st.session_state.center_lon + random.uniform(-0.02, 0.02),
            rating=round(random.uniform(4.0, 5.0), 2),
        )
        engine.add_driver(d)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HERO HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="hero-box">
    <div class="hero-title">🚖 RideSync</div>
    <div class="hero-sub">Real-Time Road-Based Ride Matching — KD-Tree · Priority Queue · Road Routing</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 1 — LIVE LOCATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="sec-title">📍 Step 1 — Set Your Location</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📡 Auto (GPS)", "✏️ Manual Entry"])

new_lat, new_lon = None, None

with tab1:
    location = streamlit_geolocation()
    if location and location.get("latitude") is not None and location.get("longitude") is not None:
        gps_lat = location["latitude"]
        gps_lon = location["longitude"]
        # Only update if the GPS actually delivered a NEW location, 
        # so it doesn't overwrite manual inputs randomly on reruns.
        if gps_lat != st.session_state.last_gps_lat or gps_lon != st.session_state.last_gps_lon:
            new_lat = gps_lat
            new_lon = gps_lon
            st.session_state.last_gps_lat = gps_lat
            st.session_state.last_gps_lon = gps_lon

with tab2:
    col_lat, col_lon = st.columns(2)
    with col_lat:
        manual_lat = st.number_input("Latitude", value=float(st.session_state.center_lat), format="%.5f", step=0.001)
    with col_lon:
        manual_lon = st.number_input("Longitude", value=float(st.session_state.center_lon), format="%.5f", step=0.001)
    if st.button("Set Location"):
        new_lat = manual_lat
        new_lon = manual_lon

if new_lat is not None and new_lon is not None:
    # If location changed significantly, reset the matching state
    if round(st.session_state.center_lat, 4) != round(new_lat, 4) or round(st.session_state.center_lon, 4) != round(new_lon, 4):
        st.session_state.center_lat = new_lat
        st.session_state.center_lon = new_lon
        st.session_state.engine = MatchingEngine()
        engine = st.session_state.engine
        st.session_state.best_driver = None
        st.session_state.passenger = None
        st.session_state.route_coords = None
        st.session_state.route_traffic_segments = None
        st.session_state.ride_requested = False
        st.session_state.total_route_coords = 0
        st.session_state.route_index = 0
        st.rerun()

st.markdown(f"""
<div class="loc-pill">
    <div class="pulse-dot"></div>
    <span class="loc-text">{st.session_state.center_lat:.5f}° N, {st.session_state.center_lon:.5f}° E</span>
</div>
""", unsafe_allow_html=True)


st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 2 — REQUEST RIDE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="sec-title">🚕 Step 2 — Request a Ride</div>', unsafe_allow_html=True)

if st.button("🚀  Request Ride", use_container_width=True):
    passenger = Passenger("Rider", st.session_state.center_lat, st.session_state.center_lon)
    st.session_state.passenger = passenger
    best_driver, msg = engine.request_ride(passenger)
    st.session_state.best_driver = best_driver
    st.session_state.ride_requested = True

    if best_driver:
        route_coords, road_dist, road_time = get_road_route(
            best_driver.location, passenger.location
        )
        st.session_state.route_coords = route_coords
        st.session_state.route_index = 0
        st.session_state.road_distance = road_dist
        st.session_state.road_time = road_time
        st.session_state.total_route_coords = len(route_coords) if route_coords else 0
        # Build traffic overlay for this route
        st.session_state.route_traffic_segments = build_route_traffic(route_coords)
    st.rerun()


st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONTROLS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="sec-title">⚙️ Controls</div>', unsafe_allow_html=True)

col_ctrl1, col_ctrl2 = st.columns(2)
with col_ctrl1:
    live_track = st.checkbox("🔴 Enable Live Tracking", value=st.session_state.live_tracking)
    st.session_state.live_tracking = live_track
with col_ctrl2:
    show_traffic = st.checkbox("🚦 Show Traffic Layer", value=st.session_state.show_traffic)
    st.session_state.show_traffic = show_traffic


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LIVE TRACKING — UPDATE POSITIONS (traffic-aware speed)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
current_traffic_condition = "free"  # default

if st.session_state.live_tracking:
    for d_id, d in engine.drivers.items():
        if st.session_state.best_driver and d.id == st.session_state.best_driver.id:
            coords = st.session_state.route_coords
            idx = st.session_state.route_index
            if coords and idx < len(coords):
                # Look up traffic at current position
                current_traffic_condition = get_traffic_at_index(
                    st.session_state.route_traffic_segments, idx
                )
                # Advance by traffic-dependent number of steps
                step = TRAFFIC_SPEED.get(current_traffic_condition, 1)
                new_idx = min(idx + step, len(coords) - 1)
                new_lon, new_lat = coords[new_idx]
                engine.update_location(d.id, new_lat, new_lon)
                st.session_state.route_index = new_idx
        else:
            engine.update_location(
                d.id,
                d.location[0] + random.uniform(-0.0005, 0.0005),
                d.location[1] + random.uniform(-0.0005, 0.0005),
            )


st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAP SECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="sec-title">🗺️ Live Map</div>', unsafe_allow_html=True)

if st.session_state.show_traffic and st.session_state.route_traffic_segments:
    st.markdown(
        '<div class="traffic-note">🚦 Route traffic — 🟢 Free &nbsp; 🟡 Moderate &nbsp; 🟠 Slow &nbsp; 🔴 Heavy</div>',
        unsafe_allow_html=True,
    )

# ---- Prepare data for map ----
p_lat = st.session_state.center_lat
p_lon = st.session_state.center_lon
if st.session_state.passenger:
    p_lat = st.session_state.passenger.location[0]
    p_lon = st.session_state.passenger.location[1]

# Driver markers
driver_points = []
for d in engine.drivers.values():
    driver_points.append({
        "lat": d.location[0],
        "lon": d.location[1],
        "name": d.id,
        "rating": str(d.rating),
        "icon_data": {
            "url": "https://cdn-icons-png.flaticon.com/512/744/744465.png",
            "width": 128,
            "height": 128,
            "anchorY": 128,
        },
    })

# Passenger marker
passenger_point = [{
    "lat": p_lat,
    "lon": p_lon,
    "name": "You",
    "rating": "",
    "icon_data": {
        "url": "https://cdn-icons-png.flaticon.com/512/149/149071.png",
        "width": 128,
        "height": 128,
        "anchorY": 128,
    },
}]

# ---- Build pydeck layers ----
layers = []

# 1) Driver icon layer
layers.append(pdk.Layer(
    "IconLayer",
    data=driver_points,
    get_icon="icon_data",
    get_position="[lon, lat]",
    get_size=4,
    size_scale=15,
    pickable=True,
))

# 2) Passenger icon layer
layers.append(pdk.Layer(
    "IconLayer",
    data=passenger_point,
    get_icon="icon_data",
    get_position="[lon, lat]",
    get_size=4,
    size_scale=15,
    pickable=True,
))

# 3) Route layers (only when ride is active)
if st.session_state.route_coords and st.session_state.best_driver:
    all_route = st.session_state.route_coords
    idx = st.session_state.route_index

    # --- Show traffic-colored route or plain blue route ---
    if st.session_state.show_traffic and st.session_state.route_traffic_segments:
        # TRAFFIC MODE: route colored by traffic (green/yellow/orange/red)
        # Dark outline underneath
        layers.append(pdk.Layer(
            "PathLayer",
            data=[{"path": all_route}],
            get_path="path",
            get_color=[30, 30, 50, 90],
            get_width=14,
            width_min_pixels=8,
            rounded=True,
            billboard=False,
        ))
        # Traffic-colored segments on top
        layers.append(pdk.Layer(
            "PathLayer",
            data=st.session_state.route_traffic_segments,
            get_path="path",
            get_color="color",
            get_width=8,
            width_min_pixels=5,
            rounded=True,
            billboard=False,
        ))
        # Gray out traveled portion
        if idx > 0:
            traveled = all_route[: idx + 1]
            if len(traveled) > 1:
                layers.append(pdk.Layer(
                    "PathLayer",
                    data=[{"path": traveled}],
                    get_path="path",
                    get_color=[100, 100, 120, 180],
                    get_width=8,
                    width_min_pixels=5,
                    rounded=True,
                    billboard=False,
                ))
    else:
        # NORMAL MODE: blue route with gray traveled
        # Dark outline
        layers.append(pdk.Layer(
            "PathLayer",
            data=[{"path": all_route}],
            get_path="path",
            get_color=[30, 30, 50, 90],
            get_width=14,
            width_min_pixels=8,
            rounded=True,
            billboard=False,
        ))
        # Traveled — gray
        if idx > 0:
            traveled = all_route[: idx + 1]
            if len(traveled) > 1:
                layers.append(pdk.Layer(
                    "PathLayer",
                    data=[{"path": traveled}],
                    get_path="path",
                    get_color=[140, 140, 160, 170],
                    get_width=8,
                    width_min_pixels=5,
                    rounded=True,
                    billboard=False,
                ))
        # Remaining — Google Maps blue
        remaining = all_route[idx:]
        if len(remaining) > 1:
            layers.append(pdk.Layer(
                "PathLayer",
                data=[{"path": remaining}],
                get_path="path",
                get_color=[66, 133, 244, 255],
                get_width=8,
                width_min_pixels=5,
                rounded=True,
                billboard=False,
            ))

    # Route endpoint markers (both modes)
    if len(all_route) >= 2:
        endpoints = [
            {"lon": all_route[0][0], "lat": all_route[0][1], "color": [66, 133, 244], "radius": 80},
            {"lon": all_route[-1][0], "lat": all_route[-1][1], "color": [34, 197, 94], "radius": 80},
        ]
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=endpoints,
            get_position="[lon, lat]",
            get_fill_color="color",
            get_radius="radius",
            radius_min_pixels=7,
            radius_max_pixels=12,
        ))

# ---- View state ----
view_state = pdk.ViewState(
    latitude=p_lat,
    longitude=p_lon,
    zoom=13,
    pitch=0,
)

# ---- Render map ONCE ----
st.pydeck_chart(
    pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="road",
        tooltip={"text": "{name}\n⭐ {rating}"},
    ),
    use_container_width=True,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  RIDE INFO PANEL (shown after ride request)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if st.session_state.best_driver and st.session_state.ride_requested:
    bd = st.session_state.best_driver
    rd = st.session_state.road_distance or 0
    rt = st.session_state.road_time or 0
    total_c = st.session_state.total_route_coords
    cur_idx = st.session_state.route_index

    # Progress calculation
    if total_c > 1:
        pct = min((cur_idx / (total_c - 1)) * 100, 100)
        frac_left = max(1 - cur_idx / (total_c - 1), 0)
    else:
        pct = 0
        frac_left = 1

    dist_left = rd * frac_left
    time_left = rt * frac_left

    # Status determination
    if pct >= 99:
        s_text, s_badge_cls, s_badge_txt = "🎉 Driver Has Arrived!", "b-green", "ARRIVED"
    elif dist_left < 0.3 and pct > 10:
        s_text, s_badge_cls, s_badge_txt = "🚗 Almost there!", "b-green", "ARRIVING"
    elif pct > 50:
        s_text, s_badge_cls, s_badge_txt = "🚗 Driver is nearby", "b-yellow", "NEARBY"
    elif pct > 0:
        s_text, s_badge_cls, s_badge_txt = "🚗 On the way", "b-blue", "IN ROUTE"
    else:
        s_text, s_badge_cls, s_badge_txt = "🚗 Driver assigned", "b-blue", "MATCHED"

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📋 Ride Information</div>', unsafe_allow_html=True)

    # Driver info strip
    st.markdown(f"""
    <div class="driver-strip">
        <div>
            <div style="font-size:1.05rem; font-weight:700; color:#f1f5f9 !important;">🚘 {bd.id}</div>
            <div style="font-size:0.82rem; color:#94a3b8 !important; margin-top:2px;">
                ⭐ {bd.rating} &nbsp;·&nbsp; 📍 {bd.location[0]:.4f}°, {bd.location[1]:.4f}°
            </div>
        </div>
        <span class="badge {s_badge_cls}">{s_badge_txt}</span>
    </div>
    """, unsafe_allow_html=True)

    # Metric cards
    eta_m = int(time_left)
    eta_s = int((time_left - eta_m) * 60)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric">
            <div class="m-icon">📏</div>
            <div class="m-val">{dist_left:.2f} km</div>
            <div class="m-lbl">Distance Left</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric">
            <div class="m-icon">⏱️</div>
            <div class="m-val">{eta_m}m {eta_s}s</div>
            <div class="m-lbl">Arrival ETA</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric">
            <div class="m-icon">⭐</div>
            <div class="m-val">{bd.rating}</div>
            <div class="m-lbl">Driver Rating</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric">
            <div class="m-icon">📊</div>
            <div class="m-val">{pct:.0f}%</div>
            <div class="m-lbl">Trip Progress</div>
        </div>""", unsafe_allow_html=True)

    # Tracking progress panel
    st.markdown(f"""
    <div class="track-box">
        <div class="track-status">{s_text}</div>
        <div class="prog-track">
            <div class="prog-fill" style="width:{pct:.1f}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:6px;">
            <span class="track-sub">🏁 Total: {rd:.2f} km / {rt:.1f} min</span>
            <span class="track-sub">📍 Remaining: {dist_left:.2f} km / {time_left:.1f} min</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Arrival celebration
    if pct >= 99:
        st.markdown("""
        <div class="arrived">
            <div style="font-size:2rem;">🎉</div>
            <div style="font-size:1.15rem; font-weight:700; color:#4ade80 !important; margin:8px 0;">
                Driver Has Arrived!
            </div>
            <div style="font-size:0.85rem; color:#94a3b8 !important;">
                Your ride is here. Have a great trip!
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.ride_requested and not st.session_state.best_driver:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="glass" style="text-align:center;">
        <span style="color:#f87171 !important; font-weight:600;">No drivers available right now. Try again shortly.</span>
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ALL DRIVERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="sec-title">🚗 All Drivers</div>', unsafe_allow_html=True)

driver_list = list(engine.drivers.values())
cols = st.columns(len(driver_list))
for i, d in enumerate(driver_list):
    with cols[i]:
        is_assigned = st.session_state.best_driver and d.id == st.session_state.best_driver.id
        badge = (
            '<span class="badge b-red">ASSIGNED</span>'
            if is_assigned
            else '<span class="badge b-green">AVAILABLE</span>'
        )
        st.markdown(f"""
        <div class="drv-mini">
            <div style="font-size:1.5rem;">🚘</div>
            <div style="font-weight:700; color:#e2e8f0 !important; font-size:0.85rem; margin:4px 0;">{d.id}</div>
            <div style="font-size:0.75rem; color:#94a3b8 !important;">⭐ {d.rating}</div>
            <div style="margin-top:6px;">{badge}</div>
        </div>
        """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FOOTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding: 16px 0 32px 0;">
    <span style="color:#475569 !important; font-size:0.78rem;">
        RideSync — Built with KD-Tree, Priority Queue & OpenRouteService
    </span>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  AUTO RERUN (traffic-aware delay)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if st.session_state.live_tracking and st.session_state.best_driver:
    # Delay varies by traffic: fast in green, slow in red (made even slower per user request)
    TRAFFIC_DELAY = {"free": 0.8, "moderate": 1.2, "slow": 1.8, "heavy": 2.5}
    delay = TRAFFIC_DELAY.get(current_traffic_condition, 1.2)
    time.sleep(delay)
    st.rerun()
