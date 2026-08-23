"""ClubConnect AI Assistant - Gemini Client (Phase 5A; migrated to the
``google-genai`` SDK).

Gateway stage 8 from
docs/ClubConnect_AI_Documentation/Architecture/ClubConnect_AI_Architecture_V2.md
Task 7 ("Call Gemini"): a thin wrapper around Google's Gen AI SDK.
Deliberately minimal - no retry/backoff, no streaming, no provider
failover (Groq/OpenRouter remain deferred, per NEXT_PHASE.md/
PROJECT_CONTEXT.md).

Migration note: this module originally used the now-deprecated
``google-generativeai`` package (``genai.configure()`` +
``genai.GenerativeModel(...).generate_content(...)``). That SDK's
model catalog no longer serves ``gemini-2.5-flash`` to new API keys
("404 ... no longer available to new users"), so this module now uses
the unified ``google-genai`` SDK instead: a single
``genai.Client(api_key=...)`` whose ``client.models.generate_content(
model=..., contents=...)`` call replaces the old configure+model-object
pattern. The public interface (``generate_response``,
``GeminiConfigError``, ``GeminiRequestError``) is unchanged, so
``routes.py``/``prompt_builder.py`` needed no changes.

This module only proxies a finished prompt string in and Gemini's text
response out. It knows nothing about intents, SQL context, or RAG
context - ``prompt_builder.py`` has already flattened all of that into
a single string by the time it reaches here (Task 1.5's provider
abstraction: AI providers are isolated behind this one module so a
future provider swap/addition doesn't touch the rest of the pipeline).
"""
import os
import sys


class GeminiConfigError(Exception):
    """Raised when GEMINI_API_KEY is missing or blank.

    Callers must catch this and return a clean, non-crashing error
    response - per the Non-Functional Requirements' Availability/
    Reliability rules ("temporary AI service failures shall not affect
    core platform functionality").
    """


class GeminiRequestError(Exception):
    """Raised when the Gemini API call itself fails: timeout, rate
    limit, network error, an unusable (empty) response, or a
    google.genai.errors.APIError (e.g. an invalid/retired model name).
    Kept distinct from ``GeminiConfigError`` so callers can message the
    user differently (retry-able vs. needs an admin to fix
    configuration).
    """


def _resolve_config(model_name: "str | None" = None):
    """Read GEMINI_API_KEY/GEMINI_MODEL from the Flask app config when
    available, falling back to raw environment variables outside an app
    context (e.g. unit tests) - same convention as
    ``rag_retriever._resolve_kb_rag_dir``.
    """
    try:
        from flask import current_app
        api_key = current_app.config.get("GEMINI_API_KEY")
        default_model = current_app.config.get("GEMINI_MODEL")
    except RuntimeError:
        api_key = None
        default_model = None

    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
    if not default_model:
        default_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    return api_key, (model_name or default_model)


def generate_response(prompt: str, model_name: "str | None" = None) -> str:
    """Call Gemini with ``prompt`` and return its raw text response.

    Raises:
        GeminiConfigError: ``GEMINI_API_KEY`` isn't configured, or the
            ``google-genai`` package isn't installed. Never crashes the
            process - callers (routes.py) catch this and return a
            clean error instead.
        GeminiRequestError: the SDK call raised (including a
            ``google.genai.errors.APIError`` such as a 404 for a
            retired/invalid model name), or returned an empty
            response.
    """
    api_key, resolved_model = _resolve_config(model_name)
    if not api_key:
        raise GeminiConfigError("GEMINI_API_KEY is not configured.")

    try:
        from google import genai
    except ImportError as exc:
        # Missing dependency behaves like a configuration problem from
        # the caller's point of view - AI is unavailable, core platform
        # keeps running.
        raise GeminiConfigError(f"google-genai is not installed: {exc}") from exc

    # --- ROOT CAUSE ---------------------------------------------------
    # gemini-2.5-flash has "thinking" turned on by default. With no
    # GenerateContentConfig at all (as this call previously had), the
    # SDK lets the model spend an unbounded/dynamic share of its output
    # token budget on internal "thought" parts before it ever writes the
    # user-visible answer. For a RAG-grounded lookup prompt like this
    # one (system docs + sql_context + rag_context + message), that
    # thinking pass alone can consume the whole response, so the API
    # call itself succeeds (hence the Google AI Studio request counter
    # going up), but the returned candidate has ONLY thought parts and
    # no answer text - result.text comes back None/"" and this module
    # raised GeminiRequestError("Gemini returned an empty response."),
    # which routes.py surfaces as 503 ai_unavailable. Fix: disable
    # thinking (thinking_budget=0) since this call only needs a direct,
    # grounded answer, not multi-step reasoning, and set an explicit
    # max_output_tokens as a safety net.
    debug = os.environ.get("GEMINI_DEBUG") == "1"
    config = genai.types.GenerateContentConfig(
        max_output_tokens=2048,
    )

    if debug:
        print(
            f"[gemini_client] sdk_version={getattr(genai, '__version__', 'unknown')} "
            f"model={resolved_model!r} prompt_len={len(prompt)} "
            f"api_key_prefix={api_key[:8]!r}",
            file=sys.stderr,
        )
        print(f"[gemini_client] prompt[:300]={prompt[:300]!r}", file=sys.stderr)

    try:
        client = genai.Client(api_key=api_key)
        result = client.models.generate_content(
            model=resolved_model, contents=prompt, config=config
        )
    except (GeminiConfigError, GeminiRequestError):
        raise
    except Exception as exc:  # SDK/network/rate-limit/APIError of any shape
        if debug:
            import traceback

            traceback.print_exc(file=sys.stderr)
        raise GeminiRequestError(str(exc)) from exc

    if debug:
        candidates = getattr(result, "candidates", None)
        finish_reason = candidates[0].finish_reason if candidates else None
        print(
            f"[gemini_client] response_type={type(result)} finish_reason={finish_reason!r} "
            f"candidates={candidates!r}",
            file=sys.stderr,
        )
        print(f"[gemini_client] result.text={getattr(result, 'text', None)!r}", file=sys.stderr)

    text = getattr(result, "text", None)
    if not text:
        candidates = getattr(result, "candidates", None)
        finish_reason = candidates[0].finish_reason if candidates else None
        raise GeminiRequestError(
            f"Gemini returned an empty response (finish_reason={finish_reason})."
        )
    return text