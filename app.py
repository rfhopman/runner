import streamlit as st
import time
import requests
from streamlit_js_eval import get_geolocation

# --- CONFIG ---
# Change 'my_runner_topic' to something unique to you
NTFY_TOPIC = "runner-app" 

st.set_page_config(page_title="RunDash", layout="centered")

# --- Styling ---
st.markdown("""
    <style>
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    div.stButton > button { width: 100% !important; height: 3.5em !important; font-size: 18px !important; border-radius: 10px; margin-bottom: 5px; }
    .main-clock { font-size: 60px !important; font-weight: 800; text-align: center; color: #00eb1b; background-color: black; border-radius: 15px; padding: 15px; margin-bottom: 15px; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- State Management ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'elapsed' not in st.session_state:
    st.session_state.elapsed = 0.0
if 'last_time' not in st.session_state:
    st.session_state.last_time = 0.0
if 'km' not in st.session_state:
    st.session_state.km = 0.0
if 'last_pos' not in st.session_state:
    st.session_state.last_pos = None
if 'last_notified_km' not in st.session_state:
    st.session_state.last_notified_km = 0.0

def format_time(s):
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02}"

def send_ntfy_update(km, elapsed, steps):
    time_str = format_time(elapsed)
    message = f"Distance: {km:.2f} km | Steps: {steps} | Time: {time_str}"
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=message.encode('utf-8'),
                      headers={"Title": "🏃 Run Update"})
    except Exception as e:
        pass

# --- GPS Tracking ---
loc = get_geolocation()
if st.session_state.running and loc:
    curr_pos = (loc['coords']['latitude'], loc['coords']['longitude'])
    if st.session_state.last_pos:
        from math import radians, cos, sin, asin, sqrt
        lat1, lon1 = map(radians, st.session_state.last_pos)
        lat2, lon2 = map(radians, curr_pos)
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km_moved = 6371 * c
        
        if km_moved > 0.005:
            st.session_state.km += km_moved
            
            # Check for 500m (0.5 km) threshold
            if st.session_state.km - st.session_state.last_notified_km >= 0.5:
                steps = int(st.session_state.km * 1312)
                send_ntfy_update(st.session_state.km, st.session_state.elapsed, steps)
                st.session_state.last_notified_km = st.session_state.km
                
    st.session_state.last_pos = curr_pos

# --- UI Layout ---
st.markdown(f'<div class="main-clock">{format_time(st.session_state.elapsed)}</div>', unsafe_allow_html=True)

m1, m2 = st.columns(2)
m1.metric("KM", f"{st.session_state.km:.2f}")
m2.metric("Steps", int(st.session_state.km * 1312))

st.write("---")

if st.button("▶️ START"):
    st.session_state.running = True
    st.session_state.last_time = time.time()
    send_ntfy_update(st.session_state.km, st.session_state.elapsed, int(st.session_state.km * 1312))

if st.button("⏸️ PAUSE"):
    st.session_state.running = False

if st.button("⏹️ STOP"):
    st.session_state.running = False

if st.button("🔄 RESET DATA"):
    st.session_state.running = False
    st.session_state.elapsed = 0.0
    st.session_state.km = 0.0
    st.session_state.last_pos = None
    st.session_state.last_notified_km = 0.0
    st.rerun()

# --- Engine ---
if st.session_state.running:
    now = time.time()
    st.session_state.elapsed += now - st.session_state.last_time
    st.session_state.last_time = now
    time.sleep(1) 
    st.rerun()
