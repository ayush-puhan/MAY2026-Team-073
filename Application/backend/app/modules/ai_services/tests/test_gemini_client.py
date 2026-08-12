"""Unit tests for app/modules/ai_services/gemini_client.py.

Run from `backend/` with:
    PYTHONPATH="$(pwd):$(pwd)/app" python3 -m pytest \
        app/modules/ai_services/tests/ -q

These tests mock the `google.genai` SDK call (migrated from the
deprecated `google.generativeai` package - see gemini_client.py's
module docstring) and never hit the real Gemini API. All tests run
outside a Flask app context, so GEMINI_API_KEY/GEMINI_MODEL are
supplied via environment variables (the module's documented fallback
path - see gemini_client._resolve_config) rather than app.config.
"""
import sys
import types

import pytest

from app.modules.ai_services.gemini_client import (
    GeminiConfigError,
    GeminiRequestError,
    generate_response,
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    yield


def _install_fake_genai(monkeypatch, *, response_text="A helpful answer.", raise_on_generate=None):
    """Install a fake `google.genai` module in sys.modules so
    `from google import genai` inside gemini_client resolves to a
    stand-in we control, without needing the real SDK installed or
    making any network call."""
    calls = {"configure_args": None, "model_name": None, "prompt": None}

    class _FakeResult:
        def __init__(self, text):
            self.text = text

    class _FakeModels:
        def generate_content(self, model, contents, config=None):
            calls["model_name"] = model
            calls["prompt"] = contents
            calls["config"] = config
            if raise_on_generate is not None:
                raise raise_on_generate
            return _FakeResult(response_text)

    class _FakeClient:
        def __init__(self, api_key=None):
            calls["configure_args"] = api_key
            self.models = _FakeModels()

    class _FakeThinkingConfig:
        def __init__(self, thinking_budget=None):
            self.thinking_budget = thinking_budget

    class _FakeGenerateContentConfig:
        def __init__(self, thinking_config=None, max_output_tokens=None):
            self.thinking_config = thinking_config
            self.max_output_tokens = max_output_tokens

    fake_types = types.ModuleType("google.genai.types")
    fake_types.ThinkingConfig = _FakeThinkingConfig
    fake_types.GenerateContentConfig = _FakeGenerateContentConfig

    fake_genai = types.ModuleType("google.genai")
    fake_genai.Client = _FakeClient
    fake_genai.types = fake_types

    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai

    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    return calls


# ---------------------------------------------------------------------------
# Config errors - never crash, always a clean exception
# ---------------------------------------------------------------------------


def test_missing_api_key_raises_config_error(monkeypatch):
    _install_fake_genai(monkeypatch)
    with pytest.raises(GeminiConfigError):
        generate_response("hello")


def test_blank_api_key_raises_config_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    _install_fake_genai(monkeypatch)
    with pytest.raises(GeminiConfigError):
        generate_response("hello")


def test_missing_sdk_raises_config_error_not_import_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    # Ensure the real (or fake) SDK is not importable for this test.
    monkeypatch.setitem(sys.modules, "google.genai", None)
    with pytest.raises(GeminiConfigError):
        generate_response("hello")


# ---------------------------------------------------------------------------
# Successful call
# ---------------------------------------------------------------------------


def test_successful_call_returns_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    calls = _install_fake_genai(monkeypatch, response_text="Your balance is 42 points.")

    result = generate_response("How many points do I have?")

    assert result == "Your balance is 42 points."
    assert calls["configure_args"] == "test-key"
    assert calls["prompt"] == "How many points do I have?"


def test_default_model_name_used_when_not_configured(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    calls = _install_fake_genai(monkeypatch)

    generate_response("hi")

    assert calls["model_name"] == "gemini-2.5-flash"


def test_explicit_model_name_overrides_default(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-pro")
    calls = _install_fake_genai(monkeypatch)

    generate_response("hi", model_name="gemini-custom")

    assert calls["model_name"] == "gemini-custom"


def test_env_model_used_when_no_explicit_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-pro")
    calls = _install_fake_genai(monkeypatch)

    generate_response("hi")

    assert calls["model_name"] == "gemini-2.5-pro"


# ---------------------------------------------------------------------------
# Request errors - SDK exceptions and empty responses
# ---------------------------------------------------------------------------


def test_sdk_exception_raises_request_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    _install_fake_genai(monkeypatch, raise_on_generate=RuntimeError("rate limited"))

    with pytest.raises(GeminiRequestError):
        generate_response("hello")


def test_empty_response_raises_request_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    _install_fake_genai(monkeypatch, response_text="")

    with pytest.raises(GeminiRequestError):
        generate_response("hello")


def test_none_response_text_raises_request_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    _install_fake_genai(monkeypatch, response_text=None)

    with pytest.raises(GeminiRequestError):
        generate_response("hello")