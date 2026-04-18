import streamlit as st
import time

# Set page to be wide enough for buttons but narrow for mobile feel
st.set_page_config(page_title="RunDash", layout="centered")

# Custom CSS for high-visibility mobile buttons
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
    }
    .main-clock {
        font-size: 60px !important;
        font-weight: 800;
        text-align: center;
        color: #00eb1b;
        background-color: black;
        border-radius: 10px;
        padding: 10px;
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
if 'steps' not in st.session_state:
    st.session_state.steps = 0
if 'km' not in st.session_state:
    st.session_state.km = 0.0

# --- Timer Logic ---
def format_time(s):
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02}"

# --- UI Layout ---
st.title("🏃 Mobile Runner")

# Big Clock Display
st.markdown(f'<div class="main-clock">{format_time(st.session_state.elapsed)}</div>', unsafe_allow_html=True)

# Stats Row
col_a, col_b = st.columns(2)
col_a.metric("Kilometers", f"{st.session_state.km:.2f} km")
col_b.metric("Total Steps", st.session_state.steps)

st.write("---")

# Buttons in a single row (4 columns)
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
        st.session_state.steps = 0
        st.session_state.km = 0.0
        st.rerun()

# --- The "Engine" ---
# This loop forces the app to update while 'running' is True
if st.session_state.running:
    now = time.time()
    dt = now - st.session_state.last_time
    st.session_state.elapsed += dt
    st.session_state.last_time = now
    
    # Simple calculation for movement
    st.session_state.steps += 1 # Mock step
    st.session_state.km += 0.001 # Mock distance
    
    time.sleep(0.1) # Prevents over-taxing the processor
    st.rerun()
