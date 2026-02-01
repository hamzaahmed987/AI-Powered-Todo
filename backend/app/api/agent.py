"""AI Agent API endpoints for task management via natural language."""

from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from agents import Runner

from app.database.session import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.agents import create_task_agent, TaskContext
from app.utils.logger import logger

router = APIRouter()


class AgentMessageRequest(BaseModel):
    """Request to send a message to the task agent."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Your task management request"
    )


class TaskData(BaseModel):
    """Task data from agent action."""
    id: str = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    status: str = Field(default="pending", description="Task status")
    priority: str = Field(default="medium", description="Task priority")


class AgentMessageResponse(BaseModel):
    """Response from the task agent."""
    message: str = Field(..., description="Agent's response")
    success: bool = Field(..., description="Whether successful")
    action: str = Field(default="none", description="Action performed: create, update, delete, get, none")
    task_data: Optional[TaskData] = Field(None, description="Task data if action performed")


@router.post(
    "/chat",
    response_model=AgentMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with task management agent",
    tags=["Agent"],
)
async def agent_chat(
    request: AgentMessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Chat with the AI task management agent using natural language.

    You can ask the agent to:
    - Create tasks: "Add a task called 'Buy groceries' with high priority"
    - Update tasks: "Mark my project task as completed"
    - Delete tasks: "Delete the old task from yesterday"
    - Get info: "Show me details of my project task"
    """
    try:
        logger.info(f"[Agent] Received chat from user {user.email}: {request.message[:50]}")

        # Create agent for this user
        logger.info(f"[Agent] Creating task agent for user {user.id}")
        agent = create_task_agent(user.id, db)

        # Create context that tools will receive
        context = TaskContext(user_id=user.id, db_session=db)

        # Run agent with context
        logger.info(f"[Agent] Running agent with message: {request.message}")
        result = await Runner.run(
            starting_agent=agent,
            input=request.message,
            context=context,
        )
        logger.info(f"[Agent] Runner completed, result type: {type(result)}")
        logger.info(f"[Agent] Result attributes: {dir(result)}")

        # Extract final message from result
        final_message = str(result.final_output) if result.final_output else "Task completed"
        logger.info(f"[Agent] Final message: {final_message}")

        # Determine action type and extract task data from message
        action = "none"
        task_data = None
        message_lower = final_message.lower()

        # Parse task ID from the final message if present
        # The tools return TaskResult with task_id and task_title
        # We need to extract this from the agent's tool calls
        task_id = None
        if hasattr(result, 'tool_calls') and result.tool_calls:
            logger.info(f"[Agent] Tool calls: {result.tool_calls}")
            # Get the last tool call result if available
            last_tool_call = result.tool_calls[-1] if result.tool_calls else None
            if last_tool_call and hasattr(last_tool_call, 'result'):
                tool_result = last_tool_call.result
                logger.info(f"[Agent] Tool result: {tool_result}")
                if isinstance(tool_result, dict):
                    task_id = tool_result.get('task_id')
                    logger.info(f"[Agent] Extracted task_id: {task_id}")

        if "created" in message_lower or "created successfully" in message_lower:
            action = "create"
        elif "updated" in message_lower or "updated successfully" in message_lower:
            action = "update"
        elif "deleted" in message_lower or "removed" in message_lower:
            action = "delete"

        logger.info(f"[Agent] Action determined: {action}")

        # If we have a task_id and it's a create/update action, fetch the task
        if task_id and action in ["create", "update"]:
            try:
                from uuid import UUID
                from app.services.task_service import get_task
                logger.info(f"[Agent] Fetching task with ID: {task_id}")
                task = get_task(db=db, task_id=UUID(task_id), user_id=user.id)
                if task:
                    task_data = TaskData(
                        id=str(task.id),
                        title=task.title,
                        status=task.status.value,
                        priority=task.priority.value,
                    )
                    logger.info(f"[Agent] Task data populated: {task_data}")
            except Exception as e:
                logger.error(f"[Agent] Failed to fetch task data: {e}")

        logger.info(f"[Agent] Sending response to user {user.email}")

        response = AgentMessageResponse(
            message=final_message,
            success=True,
            action=action,
            task_data=task_data,
        )
        logger.info(f"[Agent] Response: {response.model_dump()}")
        return response

    except Exception as e:
        error_str = str(e)
        logger.error(f"Agent error for {user.email}: {error_str}", exc_info=True)

        # Check if error is from OpenRouter API
        if "User not found" in error_str or "401" in error_str:
            logger.error(
                "OpenRouter API Authentication Error - Please verify:\n"
                "1. OPENROUTER_API_KEY is set in .env\n"
                "2. API key is valid and not expired\n"
                "3. Account associated with API key is active"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {error_str}"
        )


@router.get(
    "/capabilities",
    status_code=status.HTTP_200_OK,
    summary="Get agent capabilities",
    tags=["Agent"],
)
async def get_agent_capabilities(
    user: User = Depends(get_current_user),
):
    """Get information about the agent's capabilities."""
    return {
        "agent_name": "Task Manager",
        "capabilities": [
            {
                "action": "Create tasks",
                "description": "Add new tasks with title, description, priority, and deadline",
                "example": "Create a task called 'Buy groceries' with high priority"
            },
            {
                "action": "Update tasks",
                "description": "Change task title, status, priority, or deadline",
                "example": "Mark my project task as completed"
            },
            {
                "action": "Delete tasks",
                "description": "Remove tasks you no longer need",
                "example": "Delete the old task from yesterday"
            },
            {
                "action": "Get task info",
                "description": "Retrieve detailed information about a task",
                "example": "Show me the details of my project task"
            },
        ],
        "statuses": ["pending", "in_progress", "completed"],
        "priorities": ["low", "medium", "high", "urgent"],
    }
