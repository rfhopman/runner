import streamlit as st
import time
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="RunDash", layout="centered")

# --- THE "FLEX-FIT" FIX ---
st.markdown("""
    <style>
    /* Force the container to be a single row that fits the screen width */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 5px !important; /* Space between buttons */
    }
    
    /* Make each column take up equal space without overflowing */
    [data-testid="column"] {
        flex: 1 !important;
        min-width: 0 !important; /* Allows buttons to shrink to fit */
    }
    
    /* Button Styling: slimmed down to prevent overflow */
    div.stButton > button {
        width: 100% !important;
        height: 55px !important;
        padding: 0px !important;
        font-size: 20px !important;
        border-radius: 8px !important;
        background-color: #262730;
        border: 1px solid #444;
    }

    .main-clock {
        font-size: 55px !important;
        font-weight: 800;
        text-align: center;
        color: #00eb1b;
        background-color: black;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 5px;
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
        if km_moved > 0.005:
            st.session_state.km += km_moved
    st.session_state.last_pos = curr_pos

# --- UI Layout ---
st.markdown(f'<div class="main-clock">{format_time(st.session_state.elapsed)}</div>', unsafe_allow_html=True)

# Metrics
m1, m2 = st.columns(2)
m1.metric("KM", f"{st.session_state.km:.2f}")
m2.metric("Steps", int(st.session_state.km * 1312))

st.write("")

# --- The 4-Button Row (Auto-Scaling) ---
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
