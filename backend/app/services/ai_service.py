"""AI service using OpenAI Agents SDK with Google Gemini.

Provides task analysis, priority suggestions, and natural language processing.
Uses OpenAI Agents SDK with Google Gemini API for intelligent task assistance.
"""

from typing import Optional, Tuple, List
import os
import json
import time
from app.utils.logger import logger, log_ai_interaction
from app.utils.decorators import rate_limit, timeout
from app.models.task import TaskPriority
from pydantic import BaseModel

# Lazy imports to avoid errors if packages not installed
try:
    import litellm
    from agents import Agent, Runner, ModelSettings, set_tracing_disabled
    from agents.extensions.models.litellm_model import LitellmModel
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    logger.warning("OpenAI Agents SDK not installed. AI features will be disabled.")

# Disable tracing since we're using only Gemini API (no OpenAI API key needed)
# This prevents the SDK from trying to export traces to OpenAI backend
set_tracing_disabled(disabled=True)

# Configure LiteLLM to drop unsupported parameters (like extra_headers from Agents SDK)
# Gemini doesn't support all parameters that OpenAI Agents SDK sends
litellm.drop_params = True

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT_SECONDS", 3))
AI_RATE_LIMIT_CALLS = int(os.getenv("AI_RATE_LIMIT_CALLS", 10))
AI_RATE_LIMIT_WINDOW = int(os.getenv("AI_RATE_LIMIT_WINDOW", 60))


class TaskAnalysisResult(BaseModel):
    """Structured output for task analysis."""
    priority: str  # "low", "medium", "high", or "urgent"
    estimated_hours: int  # 1-999


# Global agent instance (singleton pattern)
_task_analyzer_agent: Optional[Agent] = None


def get_task_analyzer_agent() -> Optional[Agent]:
    """Get or create the task analyzer agent instance.

    Returns:
        Agent instance or None if API key not configured
    """
    global _task_analyzer_agent

    if not GEMINI_API_KEY or not AGENTS_AVAILABLE:
        return None

    if _task_analyzer_agent is None:
        try:
            model = LitellmModel(
                model="gemini/gemini-2.0-flash",
                api_key=GEMINI_API_KEY,
            )

            _task_analyzer_agent = Agent(
                name="TaskAnalyzer",
                instructions="""You are a task analysis assistant that estimates priority and duration.

Analyze the task description and provide:
1. Priority level: "low", "medium", "high", or "urgent"
2. Estimated time in hours: whole number between 1-999

Consider factors like:
- Urgency indicators (deadlines, "ASAP", "urgent")
- Complexity and scope
- Dependencies and blockers
- Standard time estimates for task types

Respond with a JSON object containing "priority" and "estimated_hours".""",
                model=model,
                model_settings=ModelSettings(temperature=0.3),
                tools=[],  # No external tools needed for simple analysis
            )

            logger.info("Task analyzer agent initialized with Gemini API")

        except Exception as e:
            logger.error(f"Failed to initialize task analyzer agent: {e}")
            return None

    return _task_analyzer_agent


@rate_limit(max_calls=AI_RATE_LIMIT_CALLS, time_window=AI_RATE_LIMIT_WINDOW)
@timeout(seconds=AI_TIMEOUT_SECONDS)
async def generate_priority_and_duration(
    task_description: str,
) -> Tuple[Optional[str], Optional[int]]:
    """Analyze task description and generate priority and duration suggestions.

    Uses OpenAI Agents SDK with Google Gemini to intelligently analyze tasks
    and provide recommendations for priority levels and time estimates.

    Args:
        task_description: Natural language task description

    Returns:
        Tuple of (priority_str, estimated_hours) where:
            - priority_str: "low", "medium", "high", or "urgent" (or None if AI unavailable)
            - estimated_hours: Integer hours estimate (1-999) or None if unavailable

    Example:
        >>> priority, hours = await generate_priority_and_duration(
        ...     "Review quarterly reports and prepare summary by Friday"
        ... )
        >>> priority
        'high'
        >>> hours
        3
    """
    start_time = time.time()
    agent = get_task_analyzer_agent()

    if not agent:
        logger.warning("Gemini API key not configured or agents unavailable, returning None")
        return None, None

    try:
        # Construct analysis prompt
        prompt = f"""Analyze this task and provide priority and duration estimate:

Task: {task_description}

Respond with JSON in this format:
{{"priority": "medium", "estimated_hours": 4}}"""

        # Run agent
        result = await Runner.run(agent, prompt)

        # Extract response
        response_text = result.final_output.strip()

        # Parse JSON response
        try:
            parsed = json.loads(response_text)
            priority_str = parsed.get("priority", "").lower()
            estimated_hours = parsed.get("estimated_hours", 0)
        except json.JSONDecodeError:
            # Fallback: try to parse simple format
            logger.warning(f"Failed to parse JSON response, trying fallback: {response_text}")

            # Try to extract from text (e.g., "priority: high, hours: 3")
            if "," in response_text:
                parts = response_text.split(",")
                if len(parts) >= 2:
                    priority_str = parts[0].strip().lower()
                    hours_str = parts[1].strip()
                    estimated_hours = int(hours_str) if hours_str.isdigit() else 0
                else:
                    return None, None
            else:
                return None, None

        # Validate priority
        valid_priorities = {"low", "medium", "high", "urgent"}
        if priority_str not in valid_priorities:
            logger.warning(f"Invalid priority from AI: {priority_str}")
            return None, None

        # Validate hours
        if not isinstance(estimated_hours, int) or not (1 <= estimated_hours <= 999):
            logger.warning(f"Invalid hours estimate from AI: {estimated_hours}")
            return None, None

        duration = time.time() - start_time
        logger.info(
            f"Generated AI suggestions: priority={priority_str}, hours={estimated_hours}"
        )

        # Log AI interaction for monitoring
        log_ai_interaction(
            user_id="system",  # System-generated analysis
            query=task_description,
            response=f"Priority: {priority_str}, Hours: {estimated_hours}",
            duration=duration,
            model_used="gemini/gemini-2.0-flash"
        )

        return priority_str, estimated_hours

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating AI suggestions: {e}")

        # Log AI interaction failure for monitoring
        log_ai_interaction(
            user_id="system",
            query=task_description,
            response=f"Error: {str(e)}",
            duration=duration,
            model_used="gemini/gemini-2.0-flash"
        )

        # Graceful degradation: return None instead of raising
        return None, None


@rate_limit(max_calls=AI_RATE_LIMIT_CALLS, time_window=AI_RATE_LIMIT_WINDOW)
@timeout(seconds=AI_TIMEOUT_SECONDS)
async def analyze_task_query(
    task_description: str,
    question: str,
) -> Tuple[Optional[str], Optional[List[str]], Optional[float]]:
    """Analyze a task and answer a natural language question about it.

    Uses OpenAI Agents SDK for context-aware task analysis and Q&A.
    (Deferred to Phase 2/3 - stub implementation)

    Args:
        task_description: The task to analyze
        question: Natural language question about the task

    Returns:
        Tuple of (answer, suggestions, confidence) where:
            - answer: Natural language answer to the question
            - suggestions: List of actionable suggestions
            - confidence: Confidence score (0.0-1.0)
    """
    # TODO: Implement in Phase 2
    logger.info(f"Task query analysis requested: {question}")
    return "This feature will be available in Phase 2", [], 0.0


async def suggest_subtasks(
    task_description: str,
) -> List[str]:
    """Break down a task into suggested subtasks.

    Uses AI to analyze complex tasks and suggest logical breakdown.
    (Deferred to Phase 2 - stub implementation)

    Args:
        task_description: Task to analyze

    Returns:
        List of suggested subtask descriptions
    """
    # TODO: Implement in Phase 2
    logger.info(f"Subtask suggestions requested for: {task_description}")
    return []


@rate_limit(max_calls=AI_RATE_LIMIT_CALLS, time_window=AI_RATE_LIMIT_WINDOW)
@timeout(seconds=AI_TIMEOUT_SECONDS)
async def generate_task_insights(task) -> str:
    """Generate AI-powered insights for a specific task.

    Args:
        task: Task object to analyze

    Returns:
        String with AI-generated insights and recommendations
    """
    start_time = time.time()
    agent = get_task_analyzer_agent()

    if not agent:
        logger.warning("Gemini API key not configured or agents unavailable, returning generic insights")
        return "Consider prioritizing this task based on its deadline and importance to your goals."

    try:
        # Construct analysis prompt
        prompt = f"""Provide productivity insights for this task:

Task: {task.title}
Description: {task.description or 'No description'}
Status: {task.status}
Priority: {task.priority}
AI Suggested Priority: {task.ai_priority or 'Not analyzed'}
Deadline: {task.deadline or 'No deadline'}
Estimated Duration: {task.estimated_duration or 'Not set'} minutes
AI Estimated Duration: {task.ai_estimated_duration or 'Not analyzed'} minutes

Provide specific, actionable insights about:
1. How to approach this task efficiently
2. Potential challenges to watch out for
3. Suggestions for optimal timing
4. Any recommendations for priority adjustment

Keep the response concise and practical."""

        # Run agent
        result = await Runner.run(agent, prompt)

        # Extract response
        response_text = result.final_output.strip()

        duration = time.time() - start_time
        logger.info(f"Generated AI insights for task: {task.title}")

        # Log AI interaction for monitoring
        log_ai_interaction(
            user_id=str(task.owner_id),
            query=f"Task insights for: {task.title}",
            response=response_text[:200] + "..." if len(response_text) > 200 else response_text,
            duration=duration,
            model_used="gemini/gemini-2.0-flash"
        )

        return response_text

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating task insights: {e}")

        # Log AI interaction failure for monitoring
        log_ai_interaction(
            user_id=str(task.owner_id),
            query=f"Task insights for: {task.title}",
            response=f"Error: {str(e)}",
            duration=duration,
            model_used="gemini/gemini-2.0-flash"
        )

        return "Consider reviewing this task's priority and deadline to optimize your workflow."


@rate_limit(max_calls=AI_RATE_LIMIT_CALLS, time_window=AI_RATE_LIMIT_WINDOW)
@timeout(seconds=AI_TIMEOUT_SECONDS)
async def generate_productivity_insights(tasks) -> str:
    """Generate AI-powered productivity insights based on all user tasks.

    Args:
        tasks: List of task objects to analyze

    Returns:
        String with AI-generated productivity insights and recommendations
    """
    start_time = time.time()
    agent = get_task_analyzer_agent()

    if not agent:
        logger.warning("Gemini API key not configured or agents unavailable, returning generic insights")
        return "Review your tasks regularly and prioritize based on deadlines and importance."

    try:
        # Construct analysis prompt
        task_summaries = []
        for task in tasks:
            task_summaries.append(f"- {task.title} ({task.status}, {task.priority})")

        tasks_text = "\n".join(task_summaries)

        prompt = f"""Analyze these tasks and provide productivity insights:

User Tasks:
{tasks_text}

Total Tasks: {len(tasks)}
Completed: {len([t for t in tasks if t.status == 'completed'])}
Pending: {len([t for t in tasks if t.status == 'pending'])}
In Progress: {len([t for t in tasks if t.status == 'in_progress'])}

Provide insights about:
1. Overall productivity patterns
2. Recommendations for task prioritization
3. Suggestions for time management
4. Areas for improvement

Keep the response concise and actionable."""

        # Run agent
        result = await Runner.run(agent, prompt)

        # Extract response
        response_text = result.final_output.strip()

        duration = time.time() - start_time
        logger.info(f"Generated productivity insights for user with {len(tasks)} tasks")

        # Log AI interaction for monitoring
        user_id = str(tasks[0].owner_id) if tasks else "unknown"
        log_ai_interaction(
            user_id=user_id,
            query=f"Productivity insights for {len(tasks)} tasks",
            response=response_text[:200] + "..." if len(response_text) > 200 else response_text,
            duration=duration,
            model_used="gemini/gemini-2.0-flash"
        )

        return response_text

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating productivity insights: {e}")

        # Log AI interaction failure for monitoring
        user_id = str(tasks[0].owner_id) if tasks else "unknown"
        log_ai_interaction(
            user_id=user_id,
            query=f"Productivity insights for {len(tasks)} tasks",
            response=f"Error: {str(e)}",
            duration=duration,
            model_used="gemini/gemini-2.0-flash"
        )

        return "Consider organizing your tasks by priority and deadline to improve productivity."
