import streamlit as st
import time
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="RunDash Pro", layout="centered")

# --- THE FIX: Custom CSS to force columns to stay horizontal on mobile ---
st.markdown("""
    <style>
    /* Force columns to stay side-by-side on mobile */
    [data-testid="column"] {
        width: 25% !important;
        flex: 1 1 25% !important;
        min-width: 25% !important;
    }
    
    /* Center the button text/emojis */
    div.stButton > button {
        width: 100%;
        height: 3.5em;
        font-size: 20px !important;
        border-radius: 10px;
        background-color: #262730;
        color: white;
        border: 1px solid #444;
    }

    .main-clock {
        font-size: 65px !important;
        font-weight: 800;
        text-align: center;
        color: #00eb1b;
        background-color: black;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        font-family: monospace;
    }
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
        
        # Jitter filter (ignore movement < 5 meters)
        if km_moved > 0.005:
            st.session_state.km += km_moved
    st.session_state.last_pos = curr_pos

# --- UI Layout ---
st.markdown(f'<div class="main-clock">{format_time(st.session_state.elapsed)}</div>', unsafe_allow_html=True)

# Metrics in 2 columns
m_col1, m_col2 = st.columns(2)
# We force metrics to stay side-by-side too
with m_col1:
    st.metric("Dist.", f"{st.session_state.km:.2f} km")
with m_col2:
    st.metric("Steps", int(st.session_state.km * 1312))

st.write("")

# --- The 4-Button Row ---
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
    time.sleep(1) 
    st.rerun()
