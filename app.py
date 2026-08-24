"""Streamlit interface for the Maya English Voice Tutor."""

from __future__ import annotations

import hashlib

import streamlit as st

from config import APP_ICON, APP_TITLE, GEMINI_MODEL, get_gemini_api_key
from gemini_agent import GeminiTutor, GeminiTutorError
from speech_utils import SpeechServiceError, speech_to_text, text_to_speech

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 72% 8%, rgba(249,115,22,.16), transparent 28%),
            radial-gradient(circle at 20% 20%, rgba(14,165,233,.13), transparent 30%),
            #071226;
    }
    .block-container {max-width: 1050px; padding-top: 2.2rem;}
    [data-testid="stSidebar"] {background: #0b1930; border-right: 1px solid #203554;}
    .designer-credit {
        position: fixed;
        right: 1.2rem;
        top: 4.2rem;
        z-index: 999999;
        padding: .55rem .9rem;
        color: #e2e8f0;
        background: rgba(11,25,48,.92);
        border: 1px solid #334a6d;
        border-radius: 999px;
        font-size: .82rem;
        box-shadow: 0 8px 30px rgba(0,0,0,.28);
    }
    .hero-card {
        padding: 1.2rem 1.4rem;
        border: 1px solid #203554;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(15,35,65,.96), rgba(10,23,44,.96));
        box-shadow: 0 18px 50px rgba(0,0,0,.25);
        margin-bottom: 1rem;
    }
    .maya-orb {
        display: inline-grid;
        place-items: center;
        width: 74px;
        height: 74px;
        margin-right: 14px;
        border-radius: 50%;
        font-size: 34px;
        vertical-align: middle;
        background: linear-gradient(135deg, #fb923c, #f97316 48%, #38bdf8);
        box-shadow: 0 0 0 8px rgba(249,115,22,.09), 0 0 38px rgba(56,189,248,.25);
        animation: pulse 2.4s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% {transform: scale(1);}
        50% {transform: scale(1.045);}
    }
    .hero-title {font-size: 2rem; font-weight: 750; color: #f8fafc; vertical-align: middle;}
    .hero-sub {color: #a9bad1; margin: .7rem 0 0 .2rem;}
    .status-dot {color: #4ade80; font-size: .78rem; letter-spacing: .04em;}
    .small-note {color: #91a4bf; font-size: .86rem;}
    </style>
    <div class="designer-credit">Designed by ER Pradeep Mavai</div>
    """,
    unsafe_allow_html=True,
)


def initialize_state() -> None:
    defaults = {
        "messages": [],
        "message_audio": {},
        "autoplay_message": None,
        "last_audio_hash": "",
        "session_started": False,
        "session_report": "",
        "turn_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def make_agent() -> GeminiTutor:
    return GeminiTutor(api_key=get_gemini_api_key())


def greeting(name: str, level: str, topic: str) -> str:
    learner = name.strip() or "there"
    return (
        f"Hello {learner}! I am Maya, your English speaking partner. "
        f"We will practise {topic.lower()} at a {level.lower()} level. "
        "How are you feeling today?"
    )


def add_maya_message(text: str, autoplay: bool = True) -> None:
    st.session_state.messages.append({"role": "assistant", "content": text})
    message_index = len(st.session_state.messages) - 1
    try:
        st.session_state.message_audio[message_index] = text_to_speech(text)
        if autoplay:
            st.session_state.autoplay_message = message_index
    except SpeechServiceError as exc:
        st.toast(str(exc), icon="⚠️")


def start_session(name: str, level: str, topic: str) -> None:
    st.session_state.messages = []
    st.session_state.message_audio = {}
    st.session_state.last_audio_hash = ""
    st.session_state.session_report = ""
    st.session_state.turn_count = 0
    st.session_state.session_started = True
    add_maya_message(greeting(name, level, topic))


def handle_user_turn(
    user_text: str,
    name: str,
    level: str,
    topic: str,
    correction_mode: str,
) -> bool:
    clean_text = user_text.strip()
    if not clean_text:
        return False

    st.session_state.messages.append({"role": "user", "content": clean_text})
    st.session_state.turn_count += 1
    st.session_state.session_report = ""

    try:
        reply = make_agent().reply(
            messages=st.session_state.messages,
            learner_name=name,
            level=level,
            topic=topic,
            correction_mode=correction_mode,
        )
        add_maya_message(reply)
        return True
    except GeminiTutorError as exc:
        st.session_state.messages.pop()
        st.session_state.turn_count = max(0, st.session_state.turn_count - 1)
        st.error(str(exc))
        return False


initialize_state()

with st.sidebar:
    st.header("Practice settings")
    learner_name = st.text_input("Your name", value="Pradeep")
    level = st.selectbox("English level", ["Beginner", "Intermediate", "Advanced"])
    topic = st.selectbox(
        "Conversation topic",
        [
            "Daily life",
            "Job interview",
            "Office conversation",
            "Travel",
            "Customer meeting",
            "Technology",
            "Free conversation",
        ],
    )
    correction_mode = st.radio(
        "Correction style",
        ["Gentle corrections", "Conversation only", "Detailed coaching"],
    )

    if st.button("Start / Restart session", type="primary", use_container_width=True):
        start_session(learner_name, level, topic)
        st.rerun()

    st.divider()
    st.caption(f"AI model: {GEMINI_MODEL}")
    st.caption("Voice: Indian English female (Neerja)")
    st.caption("Microphone language: English (India)")

st.markdown(
    """
    <div class="hero-card">
      <span class="maya-orb">🎙️</span>
      <span class="hero-title">Maya English Voice Tutor</span>
      <div class="hero-sub">
        <span class="status-dot">● ONLINE</span> &nbsp; Speak naturally, receive a reply, and practise with confidence.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not get_gemini_api_key():
    st.warning(
        "GEMINI_API_KEY अभी set नहीं है। पहले `.env.example` की copy बनाकर उसका "
        "नाम `.env` रखें और अपनी Gemini API key paste करें।"
    )

if not st.session_state.session_started:
    st.info("बाईं तरफ settings चुनें और **Start / Restart session** दबाएँ।")
    st.markdown(
        "**कैसे काम करता है:** Record करें → English में बोलें → Maya आपकी बात "
        "समझकर English में जवाब बोलेगी → अगला प्रश्न पूछेगी।"
    )
    st.stop()

for index, message in enumerate(st.session_state.messages):
    avatar = "👤" if message["role"] == "user" else "🎙️"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message["role"] == "assistant" and index in st.session_state.message_audio:
            st.audio(
                st.session_state.message_audio[index],
                format="audio/mp3",
                autoplay=index == st.session_state.autoplay_message,
            )

st.session_state.autoplay_message = None

voice_tab, typing_tab = st.tabs(["🎤 Speak to Maya", "⌨️ Type instead"])

with voice_tab:
    recorded_audio = st.audio_input(
        "Record your English message",
        sample_rate=16000,
        help="Record दबाएँ, English में बोलें, फिर recording रोकें।",
    )
    st.caption("पहले Maya का जवाब पूरा सुनें, फिर अपनी अगली recording करें।")

    if recorded_audio is not None:
        audio_bytes = recorded_audio.getvalue()
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()
        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash
            try:
                with st.spinner("आपकी आवाज़ समझी जा रही है..."):
                    transcript = speech_to_text(audio_bytes)
                with st.spinner("Maya जवाब तैयार कर रही है..."):
                    reply_created = handle_user_turn(
                        transcript,
                        learner_name,
                        level,
                        topic,
                        correction_mode,
                    )
                if reply_created:
                    st.rerun()
            except SpeechServiceError as exc:
                st.error(str(exc))

with typing_tab:
    with st.form("typed_message_form", clear_on_submit=True):
        typed_message = st.text_input(
            "Your message in English",
            placeholder="Example: I want to practise a job interview.",
        )
        typed_submit = st.form_submit_button("Send to Maya", type="primary")
    if typed_submit and typed_message.strip():
        with st.spinner("Maya जवाब तैयार कर रही है..."):
            reply_created = handle_user_turn(
                typed_message,
                learner_name,
                level,
                topic,
                correction_mode,
            )
        if reply_created:
            st.rerun()

st.divider()
left, right = st.columns([1, 2])
with left:
    st.metric("Practice turns", st.session_state.turn_count)
with right:
    if st.button(
        "Generate my session feedback",
        disabled=st.session_state.turn_count < 2,
        use_container_width=True,
    ):
        try:
            with st.spinner("Feedback report बन रही है..."):
                st.session_state.session_report = make_agent().session_report(
                    st.session_state.messages,
                    learner_name,
                    level,
                )
        except GeminiTutorError as exc:
            st.error(str(exc))

if st.session_state.session_report:
    with st.expander("Your English practice report", expanded=True):
        st.markdown(st.session_state.session_report)

st.markdown(
    '<p class="small-note">Voice recognition and AI replies require an internet connection. '
    'Do not speak passwords or other sensitive information.</p>',
    unsafe_allow_html=True,
)