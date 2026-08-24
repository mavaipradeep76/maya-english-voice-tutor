"""Gemini-backed conversation and feedback service."""

from __future__ import annotations

from collections.abc import Sequence

from google import genai
from google.genai import types

from config import GEMINI_MODEL, MAX_HISTORY_MESSAGES
from prompts import build_report_prompt, build_tutor_prompt


class GeminiTutorError(RuntimeError):
    """Raised when Maya cannot get a valid reply from Gemini."""


class GeminiTutor:
    """Small wrapper around the official Google Gen AI Python SDK."""

    def __init__(self, api_key: str, model: str = GEMINI_MODEL) -> None:
        if not api_key:
            raise GeminiTutorError(
                "GEMINI_API_KEY नहीं मिली। .env file में अपनी key paste करें।"
            )
        self.api_key = api_key
        self.model = model

    def reply(
        self,
        messages: Sequence[dict[str, str]],
        learner_name: str,
        level: str,
        topic: str,
        correction_mode: str,
    ) -> str:
        """Generate Maya's next short spoken response."""
        contents = self._history_to_contents(messages)
        if not contents:
            raise GeminiTutorError("पहले अपना message बोलें या type करें।")

        config = types.GenerateContentConfig(
            system_instruction=build_tutor_prompt(
                learner_name, level, topic, correction_mode
            ),
            temperature=0.65,
            max_output_tokens=220,
        )

        try:
            with genai.Client(api_key=self.api_key) as client:
                response = client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )
        except Exception as exc:  # SDK errors differ by HTTP failure type.
            raise GeminiTutorError(self._friendly_error(exc)) from exc

        text = (response.text or "").strip()
        if not text:
            raise GeminiTutorError("Gemini से खाली response मिला। दोबारा प्रयास करें।")
        return text

    def session_report(
        self,
        messages: Sequence[dict[str, str]],
        learner_name: str,
        level: str,
    ) -> str:
        """Generate a compact end-of-session learning report."""
        transcript_lines = []
        for message in messages:
            speaker = "Learner" if message["role"] == "user" else "Maya"
            transcript_lines.append(f"{speaker}: {message['content']}")

        prompt = build_report_prompt(
            "\n".join(transcript_lines), learner_name, level
        )
        try:
            with genai.Client(api_key=self.api_key) as client:
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.25,
                        max_output_tokens=500,
                    ),
                )
        except Exception as exc:
            raise GeminiTutorError(self._friendly_error(exc)) from exc

        report = (response.text or "").strip()
        if not report:
            raise GeminiTutorError("Session report generate नहीं हो सकी।")
        return report

    @staticmethod
    def _history_to_contents(
        messages: Sequence[dict[str, str]],
    ) -> list[types.Content]:
        """Convert recent Streamlit messages into Gemini conversation objects."""
        recent = list(messages)[-MAX_HISTORY_MESSAGES:]
        contents: list[types.Content] = []
        user_seen = False

        for message in recent:
            role = message.get("role")
            text = message.get("content", "").strip()
            if not text:
                continue
            if role == "user":
                user_seen = True
                gemini_role = "user"
            elif role == "assistant" and user_seen:
                gemini_role = "model"
            else:
                continue

            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=text)],
                )
            )
        return contents

    @staticmethod
    def _friendly_error(exc: Exception) -> str:
        error_text = str(exc).lower()
        if "429" in error_text or "resource_exhausted" in error_text:
            return "Gemini free-tier limit पूरी हो गई है। थोड़ी देर बाद फिर कोशिश करें।"
        if "api key" in error_text or "401" in error_text or "403" in error_text:
            return "Gemini API key invalid या unauthorized है। .env file की key जाँचें।"
        if "network" in error_text or "connection" in error_text:
            return "Internet connection नहीं मिल रहा। Network जाँचकर फिर कोशिश करें।"
        return f"Gemini response में समस्या आई: {exc}"