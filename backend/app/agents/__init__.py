"""AI Agents module for task management.

Contains OpenAI Agents SDK implementations for task management functionality.
Uses OpenRouter's OpenAI-compatible API endpoint with Qwen models via ChatCompletionsModel.
"""

from app.agents.agent import create_task_agent
from app.agents.openrouter_client import setup_openrouter_client, create_openrouter_model
from app.agents.tools import TASK_TOOLS, TaskContext

__all__ = [
    "create_task_agent",
    "setup_openrouter_client",
    "create_openrouter_model",
    "TASK_TOOLS",
    "TaskContext",
]
