import streamlit as st
import pydeck as pdk
import random
import requests
from models import Driver, Passenger
from matcher import MatchingEngine

st.set_page_config(page_title="Road-Based Ride Matching", layout="wide")

st.title("🚖 Real-Time Road-Based Ride Matching System")
st.write("KD-Tree + Priority Queue + Road Routing Engine")

# -------------------------
# INSERT YOUR API KEY HERE
# -------------------------
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjI1NDI4Y2I3NmM3NjQyM2JhZmRkY2ZhNzEwNjc0YzE3IiwiaCI6Im11cm11cjY0In0="


# -------------------------
# SESSION STATE
# -------------------------
if "engine" not in st.session_state:
    st.session_state.engine = MatchingEngine()

if "best_driver" not in st.session_state:
    st.session_state.best_driver = None

if "message" not in st.session_state:
    st.session_state.message = None

engine = st.session_state.engine


# -------------------------
# CREATE 5 DEFAULT DRIVERS
# -------------------------
if len(engine.drivers) < 5:
    base_lat = 19.0760
    base_lon = 72.8777

    for i in range(1, 6):
        lat = base_lat + random.uniform(-0.02, 0.02)
        lon = base_lon + random.uniform(-0.02, 0.02)

        driver = Driver(
            driver_id=f"Driver_{i}",
            x=lat,
            y=lon,
            rating=round(random.uniform(4.0, 5.0), 2)
        )

        engine.add_driver(driver)


# -------------------------
# GET ROAD ROUTE FUNCTION
# -------------------------
def get_road_route(start, end):

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [start[1], start[0]],
            [end[1], end[0]]
        ]
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code != 200:
        st.error(f"API Error: {response.text}")
        return None, None, None

    data = response.json()

    coords = data["features"][0]["geometry"]["coordinates"]
    distance_km = data["features"][0]["properties"]["summary"]["distance"] / 1000
    duration_min = data["features"][0]["properties"]["summary"]["duration"] / 60

    return coords, distance_km, duration_min


# -------------------------
# PASSENGER INPUT
# -------------------------
st.header("Passenger Ride Request")

user_id = st.text_input("Enter User ID", value="User_1")

pickup_lat = st.number_input("Pickup Latitude", value=19.0760, format="%.6f")
pickup_lon = st.number_input("Pickup Longitude", value=72.8777, format="%.6f")

if st.button("Request Ride"):

    passenger = Passenger(user_id, pickup_lat, pickup_lon)
    best_driver, message = engine.request_ride(passenger)

    st.session_state.best_driver = best_driver
    st.session_state.message = message


# -------------------------
# MAP PREPARATION
# -------------------------
driver_data = []
user_data = []
route_path = []

for d in engine.drivers.values():
    driver_data.append({
        "lat": d.location[0],
        "lon": d.location[1],
        "icon_data": {
            "url": "https://cdn-icons-png.flaticon.com/512/744/744465.png",
            "width": 128,
            "height": 128,
            "anchorY": 128,
        }
    })


# -------------------------
# IF RIDE ASSIGNED
# -------------------------
if st.session_state.best_driver:

    best_driver = st.session_state.best_driver

    user_data.append({
        "lat": pickup_lat,
        "lon": pickup_lon,
        "icon_data": {
            "url": "https://cdn-icons-png.flaticon.com/512/149/149071.png",
            "width": 128,
            "height": 128,
            "anchorY": 128,
        }
    })

    try:
        route_coords, road_distance, road_time = get_road_route(
            (pickup_lat, pickup_lon),
            best_driver.location
        )

        # Convert to PathLayer format
        route_path = [
            {"path": route_coords}
        ]

        st.info(f"🚗 Road Distance: {round(road_distance, 2)} km")
        st.info(f"⏱ Estimated Time: {round(road_time, 1)} minutes")

    except:
        st.error("Routing API failed. Check your API key.")


# -------------------------
# PYDECK LAYERS
# -------------------------
driver_layer = pdk.Layer(
    "IconLayer",
    driver_data,
    get_icon="icon_data",
    get_position='[lon, lat]',
    get_size=4,
    size_scale=15,
)

user_layer = pdk.Layer(
    "IconLayer",
    user_data,
    get_icon="icon_data",
    get_position='[lon, lat]',
    get_size=4,
    size_scale=15,
)

route_layer = pdk.Layer(
    "PathLayer",
    route_path,
    get_path="path",
    get_width=6,
    get_color=[255, 0, 0],
)


view_state = pdk.ViewState(
    latitude=pickup_lat,
    longitude=pickup_lon,
    zoom=12,
)

deck = pdk.Deck(
    layers=[driver_layer, user_layer, route_layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/dark-v10"
)

st.subheader("Live Road Map")
st.pydeck_chart(deck)


# -------------------------
# ASSIGNMENT MESSAGE
# -------------------------
if st.session_state.message:
    st.success(st.session_state.message)