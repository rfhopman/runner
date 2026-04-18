import streamlit as st
import time

# --- APP CONFIG ---
st.set_page_config(page_title="Runner Pro", layout="centered")

# --- STYLING (Mobile Optimization) ---
st.markdown("""
    <style>
    .big-font { font-size:40px !important; font-weight: bold; color: #FF4B4B; }
    .stat-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZING SESSION STATE ---
# This ensures data isn't lost when the app reruns
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0.0
if 'running' not in st.session_state:
    st.session_state.running = False
if 'steps' not in st.session_state:
    st.session_state.steps = 0
if 'distance' not in st.session_state:
    st.session_state.distance = 0.0

# --- LOGIC ---
def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f"{int(hours):02}:{int(mins):02}:{int(secs):02}"

# Update time if stopwatch is running
if st.session_state.running:
    current_now = time.time()
    st.session_state.elapsed_time += current_now - st.session_state.last_check
    st.session_state.last_check = current_now
    # Mock data calculation: ~2 steps per second, ~8km/h pace
    st.session_state.steps += 2 
    st.session_state.distance += 0.002
    time.sleep(0.1)
    st.rerun()

# --- UI LAYOUT ---
st.title("🏃 Runner Stopwatch")

# Display Stats
col1, col2 = st.columns(2)
with col1:
    st.metric("Distance (KM)", f"{st.session_state.distance:.2f}")
with col2:
    st.metric("Steps", st.session_state.steps)

st.markdown(f'<p class="big-font">{format_time(st.session_state.elapsed_time)}</p>', unsafe_allow_html=True)

# --- CONTROLS ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("Start"):
        if not st.session_state.running:
            st.session_state.running = True
            st.session_state.last_check = time.time()
            st.rerun()

with c2:
    if st.button("Pause"):
        st.session_state.running = False

with c3:
    if st.button("Stop"):
        st.session_state.running = False
        # Data is NOT reset here per your requirement

with c4:
    if st.button("Reset"):
        st.session_state.running = False
        st.session_state.elapsed_time = 0.0
        st.session_state.steps = 0
        st.session_state.distance = 0.0
        st.rerun()

st.info("Note: To view this on your lock screen, use a browser that supports 'Add to Home Screen' (PWA) and keep the tab active.")
