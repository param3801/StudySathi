import random
from datetime import datetime

import av
import pandas as pd
import streamlit as st
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer

from utils.state import state

# =====================================================
# PAGE CONFIGURATION & BEAUTIFICATION STYLE INJECTION
# =====================================================
st.set_page_config(
    page_title="StudySense AI",
    page_icon="📚",
    layout="wide",
)

# Custom Glassmorphism, Rounded Cards, and Button Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        color: #f3f4f6;
    }
    .main-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem !important;
    }
    .sub-title {
        font-size: 1.1rem !important;
        color: #9ca3af !important;
        margin-bottom: 2rem !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(31, 41, 55, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.2) !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">📚 StudySense AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Intelligent Real-time Student Alertness & Engagement Monitoring Ecosystem</p>', unsafe_allow_html=True)

VIDEOS = [
    "https://www.youtube.com/watch?v=c4uPfck71UY",
    "https://www.youtube.com/watch?v=1yi9bebLCUo",
    "https://www.youtube.com/watch?v=PeAdGAMBIAw",
    "https://www.youtube.com/watch?v=aN_ycRrcQ7o",
    "https://www.youtube.com/watch?v=N9rzxpZrMz4"
]

# Safe initialization of state variables
if "mode" not in st.session_state:
    st.session_state.mode = "study"
if "current_video" not in st.session_state:
    st.session_state.current_video = random.choice(VIDEOS)
if "last_break_mode" not in st.session_state:
    st.session_state.last_break_mode = False


class VideoProcessor(VideoProcessorBase):
    def recv(self, frame):
        # LAZY IMPORT: Avoids top-level circular dependency loops crashing startup
        from ai.detector import detect_face 
        
        img = frame.to_ndarray(format="bgr24")
        img = detect_face(img)
        return av.VideoFrame.from_ndarray(img, format="bgr24")


left, right = st.columns([1.6, 1.4], gap="large")

# =====================================================
# LEFT PANEL (CORE FOCUS CONTROL & BREAK HUB)
# =====================================================
with left:
    def set_ui_mode(mode_string):
        st.session_state.mode = mode_string

    @st.fragment(run_every="1s")
    def camera_panel():
        data = state.get()
        is_break = data.get("break_mode", False)

        # ⚡ EDGE TRIGGER: Auto-play state transition handler inside the loop
        if is_break and not st.session_state.last_break_mode:
            st.session_state.mode = "video"
            st.session_state.current_video = random.choice(VIDEOS)
            st.session_state.last_break_mode = True
            st.rerun()
            
        if not is_break:
            st.session_state.last_break_mode = False

        with st.container(border=True):
            if is_break:
                st.error("😴 **Break Mode Active**")
                st.markdown(f"**Current Event:** {data.get('recommendation', 'Fatigue detected.')}")

                # Grid Control Bar
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("🎥 Watch Video", use_container_width=True, 
                              type="secondary" if st.session_state.mode != "video" else "primary",
                              on_click=set_ui_mode, args=("video",))
                with col2:
                    st.button("🧩 Brain Game", use_container_width=True,
                              type="secondary" if st.session_state.mode != "game" else "primary",
                              on_click=set_ui_mode, args=("game",))
                with col3:
                    if st.button("▶ Resume Study", use_container_width=True, type="primary"):
                        st.session_state.mode = "study"
                        state.update(break_mode=False)
                        st.session_state.last_break_mode = False
                        st.rerun()

                # --- INTERACTIVE WORKSPACE VIEWPORTS ---
                if st.session_state.mode == "video":
                    st.markdown("---")
                    st.markdown("### 🎥 Mindful Relaxation Zone")
                    st.video(st.session_state.current_video, autoplay= True, loop= True, muted= False)
                    
                    if st.button("箱 Next Video", use_container_width=True):
                        st.session_state.current_video = random.choice(VIDEOS)
                        st.rerun()

                elif st.session_state.mode == "game":
                    st.markdown("---")
                    st.markdown("### 🧩 Quick Cognition Restorer")

                    if "a" not in st.session_state:
                        st.session_state.a = random.randint(10, 99)
                        st.session_state.b = random.randint(10, 99)

                    answer = st.number_input(
                        f"Solve: **{st.session_state.a} + {st.session_state.b}** = ?",
                        step=1,
                        key="math_answer"
                    )

                    if st.button("Submit Verification", use_container_width=True, type="primary"):
                        if answer == st.session_state.a + st.session_state.b:
                            st.success("🎉 Correct Answer! Mental alertness verified.")
                            del st.session_state.a
                            del st.session_state.b
                            st.rerun()
                        else:
                            st.error("❌ Mathematics mismatched. Recalculate your target input.")
            else:
                st.success("🎯 **Deep Work Engine Active**")
                st.markdown("Maintaining optimal focus metrics. Keep going, you are doing awesome!")
                st.session_state.mode = "study"

    camera_panel()

# =====================================================
# RIGHT PANEL (VISION STREAM & BIOMETRIC METRICS)
# =====================================================
with right:
    with st.container(border=True):
        st.markdown("### 📹 Intelligent Optical Stream")

        # Crucial configuration for cloud deployment (STUN servers bypass firewalls)
        RTC_CONFIGURATION = {
        "iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun2.l.google.com:19302"]},
        {"urls": ["stun:stun3.l.google.com:19302"]},
        {"urls": ["stun:stun4.l.google.com:19302"]}
        ]
            }


        # Initialize the WebRTC streamer
        webrtc_streamer(
        key="face-detection-camera",
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration=RTC_CONFIGURATION,
        )
        # FOR LOCALY DEPLOYED
        # webrtc_streamer(
        #     key="camera",
        #     video_processor_factory=VideoProcessor,
        #     media_stream_constraints={"video": True, "audio": False},
        # )

    @st.fragment(run_every="1s")
    def dashboard():
        data = state.get()

        with st.container(border=True):
            st.markdown("### 📊 Real-time Biometric Analytics")
            
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.metric("✨ Attention Status", data.get("status", "INITIALIZING"))
                st.metric("👁 Verified Blinks", f"{data.get('blink_count', 0)} count")
            with m_col2:
                st.metric("📊 Alertness Index", f"{data.get('score', 100)}%")
                st.metric("🥱 Yawn Frequency", f"{data.get('yawn_count', 0)} count")
                
            st.markdown(f"**Sleep Incidents Flagged:** `{data.get('sleep_events', 0)}`")
            st.progress(data.get("score", 100) / 100)

            score = data.get("score", 100)
            rec = data.get("recommendation", "Awaiting telemetry validation loops...")
            if score >= 80:
                st.success(f"💡 **Recommendation:** {rec}")
            elif score >= 50:
                st.warning(f"⚠️ **Recommendation:** {rec}")
            else:
                st.error(f"🚨 **Recommendation:** {rec}")

            st.caption(f"Telemetry Core Sync Time: {datetime.now().strftime('%H:%M:%S')}")

    dashboard()

# =====================================================
# LOWER BLOCK (HISTORICAL TREND GRAPHS)
# =====================================================
st.markdown("---")
with st.container(border=True):
    @st.fragment(run_every="1s")
    def alertness_graph():
        from ai.detector import analytics  # Lazy import
        st.markdown("### 📈 Chronological Alertness Architecture")
        if analytics.history:
            df = pd.DataFrame(analytics.history)
            df["time"] = pd.to_datetime(df["time"], unit="s")
            df = df.set_index("time")
            st.line_chart(df["score"], color="#60a5fa")
        else:
            st.caption("Awaiting continuous timeline dataset initialization streams...")

    alertness_graph()
