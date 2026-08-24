"""Offline smoke tests used by the GitHub Actions CI workflow."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from gemini_agent import GeminiTutor
from prompts import build_tutor_prompt
from speech_utils import _text_for_speech

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_required_deployment_files_exist() -> None:
    required_files = [
        "app.py",
        "requirements.txt",
        ".streamlit/config.toml",
        ".github/workflows/ci.yml",
    ]
    for relative_path in required_files:
        assert (PROJECT_ROOT / relative_path).is_file(), relative_path


def test_tutor_prompt_contains_conversation_rules() -> None:
    prompt = build_tutor_prompt(
        learner_name="Pradeep",
        level="Beginner",
        topic="Daily life",
        correction_mode="Gentle corrections",
    )
    assert "You are Maya" in prompt
    assert "ask exactly one natural" in prompt
    assert "Quick correction:" in prompt


def test_gemini_history_uses_supported_roles() -> None:
    history = GeminiTutor._history_to_contents(
        [
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "I am ready."},
            {"role": "assistant", "content": "Let us begin."},
        ]
    )
    assert [item.role for item in history] == ["user", "model"]


def test_tts_text_cleanup_removes_markdown_and_urls() -> None:
    cleaned = _text_for_speech("**Hello** see https://example.com now")
    assert cleaned == "Hello see now"


def test_streamlit_app_loads_without_api_key() -> None:
    app = AppTest.from_file(str(PROJECT_ROOT / "app.py"))
    app.run(timeout=30)
    assert not app.exception