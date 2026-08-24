"""Speech-to-text and Indian female text-to-speech helpers."""

from __future__ import annotations

import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import edge_tts
import speech_recognition as sr

from config import INDIAN_FEMALE_VOICE


class SpeechServiceError(RuntimeError):
    """Raised when speech recognition or synthesis fails."""


def speech_to_text(wav_bytes: bytes) -> str:
    """Transcribe a Streamlit WAV recording as Indian English."""
    if not wav_bytes:
        raise SpeechServiceError("Audio recording खाली है।")

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(BytesIO(wav_bytes)) as source:
            audio_data = recognizer.record(source)
        transcript = recognizer.recognize_google(audio_data, language="en-IN")
    except sr.UnknownValueError as exc:
        raise SpeechServiceError(
            "आवाज़ समझ नहीं आई। Microphone के पास थोड़ा साफ और धीरे बोलें।"
        ) from exc
    except sr.RequestError as exc:
        raise SpeechServiceError(
            "Speech recognition service उपलब्ध नहीं है। Internet connection जाँचें।"
        ) from exc
    except (ValueError, EOFError) as exc:
        raise SpeechServiceError("Recorded audio सही WAV format में नहीं है।") from exc

    transcript = transcript.strip()
    if not transcript:
        raise SpeechServiceError("कोई speech detect नहीं हुई। दोबारा बोलें।")
    return transcript


async def _synthesize(text: str) -> bytes:
    clean_text = _text_for_speech(text)
    communicate = edge_tts.Communicate(
        clean_text,
        voice=INDIAN_FEMALE_VOICE,
        rate="-5%",
        pitch="+0Hz",
    )
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])

    if not audio:
        raise SpeechServiceError("Maya की voice generate नहीं हुई।")
    return bytes(audio)


def text_to_speech(text: str) -> bytes:
    """Return an MP3 spoken with the en-IN Neerja female neural voice."""
    if not text.strip():
        raise SpeechServiceError("बोलने के लिए response text खाली है।")

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        try:
            return asyncio.run(_synthesize(text))
        except Exception as exc:
            if isinstance(exc, SpeechServiceError):
                raise
            raise SpeechServiceError(
                "Indian female voice service से connection नहीं बन पाया।"
            ) from exc

    # Streamlit normally has no running loop in this thread. This fallback keeps
    # the function safe in notebook or async-hosted environments as well.
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(lambda: asyncio.run(_synthesize(text))).result()
    except Exception as exc:
        if isinstance(exc, SpeechServiceError):
            raise
        raise SpeechServiceError(
            "Indian female voice service से connection नहीं बन पाया।"
        ) from exc


def _text_for_speech(text: str) -> str:
    """Remove formatting that sounds unnatural when read aloud."""
    clean = re.sub(r"https?://\S+", "", text)
    clean = re.sub(r"[*_`#>]", "", clean)
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()