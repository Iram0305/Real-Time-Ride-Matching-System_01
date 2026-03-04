# app.py

import streamlit as st
import pydeck as pdk
import random
import requests
import time
from streamlit_geolocation import streamlit_geolocation
from models import Driver, Passenger
from matcher import MatchingEngine

st.set_page_config(page_title="Road-Based Ride Matching", layout="wide")

st.title("🚖 Real-Time Road-Based Ride Matching System")
st.write("KD-Tree + Priority Queue + Road Routing Engine with Live Tracking")

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
if "passenger" not in st.session_state:
    st.session_state.passenger = None
if "message" not in st.session_state:
    st.session_state.message = None
if "route_coords" not in st.session_state:
    st.session_state.route_coords = None
if "route_index" not in st.session_state:
    st.session_state.route_index = 0
if "live_tracking" not in st.session_state:
    st.session_state.live_tracking = False
if "road_distance" not in st.session_state:
    st.session_state.road_distance = None
if "road_time" not in st.session_state:
    st.session_state.road_time = None
if "center_lat" not in st.session_state:
    st.session_state.center_lat = 19.0760  # Default fallback
if "center_lon" not in st.session_state:
    st.session_state.center_lon = 72.8777


# -------------------------
# GET LIVE BROWSER LOCATION
# -------------------------
st.header("Passenger Ride Request")
st.write("📍 **Step 1: Get your live location**")
location = streamlit_geolocation()

# If the browser successfully grabs the GPS location
if location and location.get('latitude') is not None and location.get('longitude') is not None:
    # Check if the location is new (prevents resetting on every single app refresh)
    if round(st.session_state.center_lat, 4) != round(location['latitude'], 4):
        st.session_state.center_lat = location['latitude']
        st.session_state.center_lon = location['longitude']
        
        # Reset the matching engine to clear old drivers and spawn new ones here
        st.session_state.engine = MatchingEngine()
        st.session_state.best_driver = None
        st.session_state.passenger = None
        st.session_state.route_coords = None
        st.session_state.message = "Location updated! New drivers have been spawned near you."

engine = st.session_state.engine


# -------------------------
# CREATE 5 LOCAL DRIVERS
# -------------------------
if len(engine.drivers) < 5:
    base_lat = st.session_state.center_lat
    base_lon = st.session_state.center_lon

    for i in range(1, 6):
        # Spawn drivers dynamically around whatever the center location is
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
st.write("🚕 **Step 2: Request a Ride**")
user_id = st.text_input("Enter User ID", value="User_1")

# Automatically pull from the live GPS fetch (or defaults if not fetched yet)
pickup_lat = st.session_state.center_lat
pickup_lon = st.session_state.center_lon

if st.button("Request Ride"):
    passenger = Passenger(user_id, pickup_lat, pickup_lon)
    st.session_state.passenger = passenger
    
    best_driver, message = engine.request_ride(passenger)
    st.session_state.best_driver = best_driver
    st.session_state.message = message

    if best_driver:
        try:
            route_coords, road_distance, road_time = get_road_route(
                best_driver.location, 
                passenger.location
            )
            if route_coords:
                st.session_state.route_coords = route_coords
                st.session_state.route_index = 0
                st.session_state.road_distance = road_distance
                st.session_state.road_time = road_time
        except Exception as e:
            st.error("Routing API failed. Check your API key or connection.")


# -------------------------
# LIVE TRACKING LOGIC
# -------------------------
st.subheader("Live Tracking Controls")
live_track = st.checkbox("Enable Live Location Tracking", value=st.session_state.live_tracking)
st.session_state.live_tracking = live_track

if live_track:
    for d_id, d in engine.drivers.items():
        if st.session_state.best_driver and d.id == st.session_state.best_driver.id:
            coords = st.session_state.route_coords
            idx = st.session_state.route_index
            if coords and idx < len(coords):
                new_lon, new_lat = coords[idx]
                engine.update_location(d.id, new_lat, new_lon)
                st.session_state.route_index += 1
        else:
            new_lat = d.location[0] + random.uniform(-0.0005, 0.0005)
            new_lon = d.location[1] + random.uniform(-0.0005, 0.0005)
            engine.update_location(d.id, new_lat, new_lon)

    if st.session_state.passenger:
        p = st.session_state.passenger
        new_p_lat = p.location[0] + random.uniform(-0.0002, 0.0002)
        new_p_lon = p.location[1] + random.uniform(-0.0002, 0.0002)
        p.update_location(new_p_lat, new_p_lon)


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

current_p_lat = st.session_state.passenger.location[0] if st.session_state.passenger else pickup_lat
current_p_lon = st.session_state.passenger.location[1] if st.session_state.passenger else pickup_lon

user_data.append({
    "lat": current_p_lat,
    "lon": current_p_lon,
    "icon_data": {
        "url": "https://cdn-icons-png.flaticon.com/512/149/149071.png",
        "width": 128,
        "height": 128,
        "anchorY": 128,
    }
})

# -------------------------
# IF RIDE ASSIGNED
# -------------------------
if st.session_state.best_driver and st.session_state.passenger:
    if st.session_state.route_coords:
        remaining_route = st.session_state.route_coords[st.session_state.route_index:]
        if len(remaining_route) > 1:
            route_path = [{"path": remaining_route}]
        elif len(remaining_route) <= 1 and st.session_state.route_coords:
            st.success("Driver has arrived at your location!")

    if st.session_state.road_distance is not None:
        st.info(f"🚗 Initial Road Distance: {round(st.session_state.road_distance, 2)} km")
        st.info(f"⏱ Initial Estimated Time: {round(st.session_state.road_time, 1)} minutes")


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
    latitude=current_p_lat,
    longitude=current_p_lon,
    zoom=13,
)

deck = pdk.Deck(
    layers=[driver_layer, user_layer, route_layer],
    initial_view_state=view_state,
    map_style="road"
)

st.subheader("Live Road Map")
st.pydeck_chart(deck)


# -------------------------
# ASSIGNMENT MESSAGE
# -------------------------
if st.session_state.message:
    st.success(st.session_state.message)


# -------------------------
# LOOP RERUN FOR MOVEMENT
# -------------------------
if st.session_state.live_tracking:
    time.sleep(0.5) 
    st.rerun()
