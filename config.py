"""Application configuration and secret loading."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "Maya English Voice Tutor"
APP_ICON = "🎙️"
GEMINI_MODEL = "gemini-2.5-flash-lite"
INDIAN_FEMALE_VOICE = "en-IN-NeerjaNeural"
MAX_HISTORY_MESSAGES = 14


def get_gemini_api_key() -> str:
    """Load the API key from Streamlit secrets or a local .env file."""
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        # Streamlit raises its own missing-secrets exception when no secrets
        # file exists. Local development should then fall back to .env.
        secret_key = ""

    return str(secret_key or os.getenv("GEMINI_API_KEY", "")).strip()