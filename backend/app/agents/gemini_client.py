"""Setup Gemini ChatCompletionsModel for OpenAI Agents SDK.

Uses OpenAIChatCompletionsModel with Gemini's OpenAI-compatible endpoint.
"""

import os
from openai import AsyncOpenAI

from agents import set_tracing_disabled,OpenAIChatCompletionsModel


def create_gemini_model() -> OpenAIChatCompletionsModel:
    """Create OpenAIChatCompletionsModel for Gemini API.

    Returns:
        OpenAIChatCompletionsModel configured for Gemini API

    Environment:
        GEMINI_API_KEY: Required - Get from https://aistudio.google.com/app/apikey
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Get one from: https://aistudio.google.com/app/apikey"
        )

    # Create AsyncOpenAI client pointing to Gemini's OpenAI-compatible endpoint
    gemini_client = AsyncOpenAI(
        api_key='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',
        base_url="https://openrouter.ai/api/v1"
    )

    # Create ChatCompletionsModel with Gemini client
    # This uses Chat Completions API directly (Gemini doesn't support Responses API)
    model = OpenAIChatCompletionsModel(
        model="qwen/qwen-2.5-72b-instruct",  # Use Gemini 2.0 Flash model
        openai_client=gemini_client
    )

    return model


def setup_gemini_client():
    """Setup function called during application startup.

    Disables tracing for Gemini (not OpenAI).
    The actual model creation is done per-agent via create_gemini_model().
    """
    # Disable tracing since we're using Gemini (not OpenAI)
    set_tracing_disabled(disabled=True)
