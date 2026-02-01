"""Setup OpenRouter ChatCompletionsModel for OpenAI Agents SDK.

Uses OpenAIChatCompletionsModel with OpenRouter's OpenAI-compatible endpoint.
Supports Qwen and other open-source models via OpenRouter.
"""

import os
from openai import AsyncOpenAI

from agents import set_tracing_disabled, OpenAIChatCompletionsModel


def create_openrouter_model() -> OpenAIChatCompletionsModel:
    """Create OpenAIChatCompletionsModel for OpenRouter API with Qwen.

    Returns:
        OpenAIChatCompletionsModel configured for OpenRouter API

    Environment:
        OPENROUTER_API_KEY: Required - Get from https://openrouter.ai
        OPENROUTER_MODEL: Optional - Default is qwen/qwen-2.5-72b-instruct

    Models available on OpenRouter (free tier):
    - qwen/qwen-2.5-72b-instruct: Best overall - 72B parameters, excellent quality
    - qwen/qwq-32b: Reasoning model - 32B parameters, great for complex tasks
    - qwen/qwen-1.5-0.5b-chat: Lightweight option
    - And many others (visit https://openrouter.ai/models for full list)
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable not set. "
            "Get one from: https://openrouter.ai/keys"
        )

    # Validate API key format (should start with sk-or-)
    if not api_key.startswith("sk-or-"):
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"OPENROUTER_API_KEY has unexpected format. "
            f"Expected to start with 'sk-or-', got: {api_key[:20]}..."
        )

    # Get model from environment or use default
    model_name = os.getenv("OPENROUTER_MODEL", "ai/glm-4.5-air:free")

    # Create AsyncOpenAI client pointing to OpenRouter's OpenAI-compatible endpoint
    openrouter_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    # Create ChatCompletionsModel with OpenRouter client
    model = OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=openrouter_client
    )

    return model


def setup_openrouter_client():
    """Setup function called during application startup.

    Disables tracing for OpenRouter (not OpenAI).
    The actual model creation is done per-agent via create_openrouter_model().
    """
    # Disable tracing since we're using OpenRouter (not OpenAI)
    set_tracing_disabled(disabled=True)
