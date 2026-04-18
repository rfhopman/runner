import streamlit as st
import time
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="RunDash Pro", layout="centered")

# Custom CSS for the "Locked Screen" look
st.markdown("""
    <style>
    .main-clock {
        font-size: 70px !important;
        font-weight: 800;
        text-align: center;
        color: #00eb1b;
        background-color: black;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        font-family: 'Courier New', monospace;
    }
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
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

def format_time(s):
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02}"

# --- GPS Tracking ---
# This will trigger a "Allow Location" popup on your iPhone
loc = get_geolocation()

if st.session_state.running and loc:
    curr_pos = (loc['coords']['latitude'], loc['coords']['longitude'])
    
    if st.session_state.last_pos:
        # Simple distance math (Haversine approximation for small distances)
        from math import radians, cos, sin, asin, sqrt
        lat1, lon1 = map(radians, st.session_state.last_pos)
        lat2, lon2 = map(radians, curr_pos)
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km_moved = 6371 * c
        
        # Only add if moved more than 5 meters (to avoid GPS "jitter" while standing still)
        if km_moved > 0.005:
            st.session_state.km += km_moved
            
    st.session_state.last_pos = curr_pos

# --- UI Layout ---
st.markdown(f'<div class="main-clock">{format_time(st.session_state.elapsed)}</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
col1.metric("Distance", f"{st.session_state.km:.2f} km")
# Note: Step counting in browsers is highly restricted; 
# we'll approximate 1300 steps per km for a "Real feel"
steps = int(st.session_state.km * 1312) 
col2.metric("Est. Steps", steps)

st.write("")

# Single row for all buttons
btn_cols = st.columns(4)
with btn_cols[0]:
    if st.button("▶️"):
        st.session_state.running = True
        st.session_state.last_time = time.time()
with btn_cols[1]:
    if st.button("⏸️"):
        st.session_state.running = False
with btn_cols[2]:
    if st.button("⏹️"):
        st.session_state.running = False
with btn_cols[3]:
    if st.button("🔄"):
        st.session_state.running = False
        st.session_state.elapsed = 0.0
        st.session_state.km = 0.0
        st.session_state.last_pos = None
        st.rerun()

# --- Engine ---
if st.session_state.running:
    now = time.time()
    st.session_state.elapsed += now - st.session_state.last_time
    st.session_state.last_time = now
    time.sleep(1) # Refresh every second
    st.rerun()
