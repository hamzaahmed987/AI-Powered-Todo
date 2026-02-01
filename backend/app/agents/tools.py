"""OpenAI Agents SDK tools for task management.

Defines function tools for adding, updating, and deleting tasks.
Tools accept RunContextWrapper to access user_id and db_session.
"""

from typing import Annotated, Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from agents import function_tool, RunContextWrapper

from app.models.task import TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate


class TaskContext(BaseModel):
    """Context for task tools - passed to tools via RunContextWrapper."""
    user_id: UUID
    db_session: Any


class TaskResult(BaseModel):
    """Result of a task operation."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable result message")
    task_id: Optional[str] = Field(None, description="Task ID if created/updated")
    task_title: Optional[str] = Field(None, description="Task title")


@function_tool(strict_mode=False)
async def add_task(
    ctx: RunContextWrapper[TaskContext],
    title: Annotated[str, "Task title (required, max 500 characters)"],
    description: Annotated[Optional[str], "Task description (optional)"] = None,
    priority: Annotated[Optional[str], "Priority: low, medium, high, urgent (default: medium)"] = "medium",
    deadline: Annotated[Optional[str], "Deadline in ISO 8601 format (optional)"] = None,
    estimated_duration: Annotated[Optional[int], "Estimated duration in minutes (optional)"] = None,
) -> TaskResult:
    """Create a new task with enhanced AI-powered suggestions.

    Args:
        ctx: RunContextWrapper containing user_id and db_session
        title: Task title
        description: Optional description
        priority: Priority level
        deadline: Optional deadline
        estimated_duration: Optional estimated duration in minutes

    Returns:
        TaskResult with success status and task details
    """
    try:
        from app.services.task_service import create_task as create_task_service
        from app.services.ai_service import generate_priority_and_duration

        # Parse deadline if provided
        deadline_dt = None
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            except ValueError:
                return TaskResult(
                    success=False,
                    message=f"Invalid deadline format. Use ISO 8601 format."
                )

        # Validate priority
        try:
            TaskPriority(priority)
        except ValueError:
            return TaskResult(
                success=False,
                message=f"Invalid priority. Must be: low, medium, high, or urgent"
            )

        # Create task via service
        task = create_task_service(
            db=ctx.context.db_session,
            user_id=ctx.context.user_id,
            title=title,
            description=description,
            deadline=deadline_dt,
            estimated_duration=estimated_duration,
        )

        # Generate AI suggestions for priority and duration based on task content
        description_for_ai = f"{title}. {description or ''}"
        ai_priority, ai_duration = await generate_priority_and_duration(description_for_ai)

        if ai_priority or ai_duration:
            from app.services.task_service import update_ai_suggestions
            update_ai_suggestions(
                ctx.context.db_session,
                task.id,
                ctx.context.user_id,
                priority=TaskPriority(ai_priority) if ai_priority else None,
                estimated_duration=ai_duration if ai_duration else None,
            )

        ai_suggestion_msg = ""
        if ai_priority and ai_priority != priority:
            ai_suggestion_msg += f" AI suggests priority: {ai_priority}."
        if ai_duration and estimated_duration != ai_duration:
            ai_suggestion_msg += f" AI suggests duration: {ai_duration} minutes."

        return TaskResult(
            success=True,
            message=f"Task '{title}' created successfully with {priority} priority.{ai_suggestion_msg}",
            task_id=str(task.id),
            task_title=task.title
        )

    except Exception as e:
        return TaskResult(
            success=False,
            message=f"Failed to create task: {str(e)}"
        )


def _parse_status_from_query(query: str) -> Optional[str]:
    """Extract status intent from natural language query."""
    query_lower = query.lower()

    # Completed status keywords
    if any(word in query_lower for word in ["complete", "done", "finished", "mark as done", "mark complete"]):
        return "completed"

    # In progress status keywords
    if any(word in query_lower for word in ["start", "in progress", "started", "working", "mark in progress"]):
        return "in_progress"

    # Pending status keywords
    if any(word in query_lower for word in ["pending", "mark as pending", "not done", "reopen"]):
        return "pending"

    return None


def _parse_title_from_query(query: str) -> Optional[str]:
    """Extract new title from natural language query."""
    query_lower = query.lower()

    # Look for rename/retitle patterns
    if "rename to" in query_lower or "retitle to" in query_lower:
        # Extract text after "rename to" or "retitle to"
        for pattern in ["rename to ", "retitle to "]:
            if pattern in query_lower:
                idx = query_lower.index(pattern) + len(pattern)
                new_title = query[idx:].strip()
                # Remove trailing punctuation
                new_title = new_title.rstrip('.,!?')
                if new_title and len(new_title) > 0:
                    return new_title

    if "change title to" in query_lower:
        idx = query_lower.index("change title to") + len("change title to")
        new_title = query[idx:].strip()
        new_title = new_title.rstrip('.,!?')
        if new_title:
            return new_title

    if "name it" in query_lower or "call it" in query_lower:
        for pattern in ["name it ", "call it "]:
            if pattern in query_lower:
                idx = query_lower.index(pattern) + len(pattern)
                new_title = query[idx:].strip()
                new_title = new_title.rstrip('.,!?')
                if new_title:
                    return new_title

    return None


@function_tool(strict_mode=False)
async def update_task(
    ctx: RunContextWrapper[TaskContext],
    task_id: Annotated[str, "Task ID (UUID) or task title/keyword. Example: 'milk', 'airport task', or exact UUID"],
    full_query: Annotated[Optional[str], "Full user query for intelligent parsing (optional)"] = None,
    title: Annotated[Optional[str], "New title (optional)"] = None,
    description: Annotated[Optional[str], "New description (optional)"] = None,
    status: Annotated[Optional[str], "New status: pending, in_progress, or completed (optional)"] = None,
    priority: Annotated[Optional[str], "New priority: low, medium, high, or urgent (optional)"] = None,
    deadline: Annotated[Optional[str], "New deadline in ISO 8601 format (optional)"] = None,
) -> TaskResult:
    """Update an existing task by ID or by matching task title.

    Intelligently parses natural language queries to extract status and title changes.

    Supports natural language queries:
    - By UUID: "550e8400-e29b-41d4-a716-446655440000"
    - By title: "milk task", "airport", "buy groceries"

    Status Examples:
    - "mark milk as completed" → status = "completed"
    - "mark as done" → status = "completed"
    - "start task" → status = "in_progress"
    - "mark as pending" → status = "pending"

    Title Examples:
    - "rename milk to groceries" → title = "groceries"
    - "change title to new task" → title = "new task"
    - "call it something new" → title = "something new"

    Args:
        ctx: RunContextWrapper containing user_id and db_session
        task_id: Task ID (UUID) or task title keyword
        full_query: Full user query for intelligent status/title parsing
        title: Optional new title (overrides query parsing)
        description: Optional new description
        status: Optional new status (overrides query parsing)
        priority: Optional new priority
        deadline: Optional new deadline

    Returns:
        TaskResult with success status
    """
    try:
        from app.services.task_service import (
            get_task as get_task_service,
            get_user_tasks as get_user_tasks_service,
            update_task as update_task_service
        )

        # Try to parse as UUID first
        task_to_update = None

        try:
            task_uuid = UUID(task_id)
            # It's a valid UUID
            task_to_update = get_task_service(
                db=ctx.context.db_session,
                task_id=task_uuid,
                user_id=ctx.context.user_id
            )

            if not task_to_update:
                return TaskResult(
                    success=False,
                    message=f"Task not found or permission denied"
                )
        except ValueError:
            # Not a UUID - treat as task title/keyword search
            all_tasks, _ = get_user_tasks_service(
                db=ctx.context.db_session,
                user_id=ctx.context.user_id
            )

            if not all_tasks:
                return TaskResult(
                    success=False,
                    message=f"No tasks found. Cannot update task matching '{task_id}'"
                )

            # Find task by matching keyword in title (case-insensitive)
            search_query = task_id.lower().strip()
            matching_tasks = [
                t for t in all_tasks
                if search_query in t.title.lower()
            ]

            if not matching_tasks:
                return TaskResult(
                    success=False,
                    message=f"No task found matching '{task_id}'. Available tasks: " +
                           ", ".join([f"'{t.title}'" for t in all_tasks[:5]])
                )

            if len(matching_tasks) > 1:
                # Multiple matches - provide copy-pastable commands
                commands = [
                    f"Update '{t.title}' - say: 'update {t.title}' to be specific"
                    for t in matching_tasks
                ]
                commands_text = "\n".join(commands)
                return TaskResult(
                    success=False,
                    message=f"Found {len(matching_tasks)} tasks matching '{task_id}':\n{commands_text}\n\nPlease be more specific!"
                )

            # Single match - proceed with update
            task_to_update = matching_tasks[0]
            task_uuid = task_to_update.id

        # Parse status and title from query if not explicitly provided
        if not status and full_query:
            parsed_status = _parse_status_from_query(full_query)
            if parsed_status:
                status = parsed_status

        if not title and full_query:
            parsed_title = _parse_title_from_query(full_query)
            if parsed_title:
                title = parsed_title

        # Validate enums if provided
        if status:
            try:
                TaskStatus(status)
            except ValueError:
                return TaskResult(
                    success=False,
                    message=f"Invalid status. Must be: pending, in_progress, or completed"
                )

        if priority:
            try:
                TaskPriority(priority)
            except ValueError:
                return TaskResult(
                    success=False,
                    message=f"Invalid priority. Must be: low, medium, high, or urgent"
                )

        # Parse deadline if provided
        deadline_dt = None
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            except ValueError:
                return TaskResult(
                    success=False,
                    message=f"Invalid deadline format. Use ISO 8601 format."
                )

        # Create update schema
        update_data = TaskUpdate(
            title=title,
            description=description,
            status=TaskStatus(status) if status else None,
            priority=TaskPriority(priority) if priority else None,
            deadline=deadline_dt,
        )

        # Update task - unpack TaskUpdate object into kwargs
        updated_task = update_task_service(
            db=ctx.context.db_session,
            task_id=task_uuid,
            user_id=ctx.context.user_id,
            **update_data.model_dump(exclude_none=True)
        )

        # Build detailed success message showing what was updated
        updates = []
        if title:
            updates.append(f"title to '{title}'")
        if status:
            updates.append(f"status to {status}")
        if priority:
            updates.append(f"priority to {priority}")
        if description:
            updates.append("description")
        if deadline:
            updates.append("deadline")

        message = f"Task '{updated_task.title}' updated successfully"
        if updates:
            message += f" - changed {', '.join(updates)}."
        else:
            message += "."

        return TaskResult(
            success=True,
            message=message,
            task_id=str(updated_task.id),
            task_title=updated_task.title
        )

    except Exception as e:
        return TaskResult(
            success=False,
            message=f"Failed to update task: {str(e)}"
        )


@function_tool(strict_mode=False)
async def delete_task(
    ctx: RunContextWrapper[TaskContext],
    task_id: Annotated[str, "Task ID (UUID) or task title/keyword to delete. Example: 'airport task', 'buy groceries'"],
) -> TaskResult:
    """Delete a task by ID or by matching task title.

    Supports natural language queries:
    - By UUID: "550e8400-e29b-41d4-a716-446655440000"
    - By title: "airport task", "buy groceries", "project meeting"

    Args:
        ctx: RunContextWrapper containing user_id and db_session
        task_id: Task ID (UUID) or task title keyword to delete

    Returns:
        TaskResult with success status
    """
    try:
        from app.services.task_service import (
            get_task as get_task_service,
            get_user_tasks as get_user_tasks_service,
            delete_task as delete_task_service
        )

        # Try to parse as UUID first
        task_to_delete = None

        try:
            task_uuid = UUID(task_id)
            # It's a valid UUID
            task_to_delete = get_task_service(
                db=ctx.context.db_session,
                task_id=task_uuid,
                user_id=ctx.context.user_id
            )
            if task_to_delete:
                delete_task_service(
                    db=ctx.context.db_session,
                    task_id=task_uuid,
                    user_id=ctx.context.user_id
                )
                return TaskResult(
                    success=True,
                    message=f"Task '{task_to_delete.title}' deleted successfully.",
                    task_id=str(task_uuid),
                    task_title=task_to_delete.title
                )
        except ValueError:
            # Not a UUID - treat as task title/keyword search
            pass

        # Search by task title/keyword
        all_tasks, _ = get_user_tasks_service(
            db=ctx.context.db_session,
            user_id=ctx.context.user_id
        )

        if not all_tasks:
            return TaskResult(
                success=False,
                message=f"No tasks found. Cannot delete task matching '{task_id}'"
            )

        # Find task by matching keyword in title (case-insensitive)
        search_query = task_id.lower().strip()
        matching_tasks = [
            t for t in all_tasks
            if search_query in t.title.lower()
        ]

        if not matching_tasks:
            return TaskResult(
                success=False,
                message=f"No task found matching '{task_id}'. Try being more specific or provide the exact task name."
            )

        if len(matching_tasks) > 1:
            # Multiple matches - provide copy-pastable commands
            commands = [
                f"Delete '{t.title}' - say: 'delete {t.title}' to be specific"
                for t in matching_tasks
            ]
            commands_text = "\n".join(commands)
            return TaskResult(
                success=False,
                message=f"Found {len(matching_tasks)} tasks matching '{task_id}':\n{commands_text}\n\nPlease be more specific!"
            )

        # Delete the matching task
        task_to_delete = matching_tasks[0]
        delete_task_service(
            db=ctx.context.db_session,
            task_id=task_to_delete.id,
            user_id=ctx.context.user_id
        )

        return TaskResult(
            success=True,
            message=f"Task '{task_to_delete.title}' deleted successfully.",
            task_id=str(task_to_delete.id),
            task_title=task_to_delete.title
        )

    except Exception as e:
        return TaskResult(
            success=False,
            message=f"Failed to delete task: {str(e)}"
        )


@function_tool(strict_mode=False)
async def get_task_info(
    ctx: RunContextWrapper[TaskContext],
    task_id: Annotated[str, "Task ID (UUID) to retrieve"],
) -> TaskResult:
    """Get information about a specific task.

    Args:
        ctx: RunContextWrapper containing user_id and db_session
        task_id: Task ID to retrieve

    Returns:
        TaskResult with task information
    """
    try:
        from app.services.task_service import get_task as get_task_service

        # Convert task_id to UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return TaskResult(
                success=False,
                message=f"Invalid task ID format"
            )

        # Get task
        task = get_task_service(
            db=ctx.context.db_session,
            task_id=task_uuid,
            user_id=ctx.context.user_id
        )

        if not task:
            return TaskResult(
                success=False,
                message=f"Task not found or permission denied"
            )

        # Format task details
        task_details = f"""Task: {task.title}
Status: {task.status}
Priority: {task.priority}
Description: {task.description or 'No description'}
Deadline: {task.deadline.isoformat() if task.deadline else 'No deadline'}
Created: {task.created_at.isoformat()}
Updated: {task.updated_at.isoformat()}"""

        return TaskResult(
            success=True,
            message=task_details,
            task_id=str(task.id),
            task_title=task.title
        )

    except Exception as e:
        return TaskResult(
            success=False,
            message=f"Failed to retrieve task: {str(e)}"
        )


@function_tool(strict_mode=False)
async def get_task_insights(
    ctx: RunContextWrapper[TaskContext],
    task_id: Annotated[str, "Task ID (UUID) to retrieve insights for"],
) -> TaskResult:
    """Get AI-powered insights about a specific task including recommendations.

    Args:
        ctx: RunContextWrapper containing user_id and db_session
        task_id: Task ID to retrieve insights for

    Returns:
        TaskResult with task insights and recommendations
    """
    try:
        from app.services.task_service import get_task as get_task_service
        from app.services.ai_service import generate_task_insights

        # Convert task_id to UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return TaskResult(
                success=False,
                message=f"Invalid task ID format"
            )

        # Get task
        task = get_task_service(
            db=ctx.context.db_session,
            task_id=task_uuid,
            user_id=ctx.context.user_id
        )

        if not task:
            return TaskResult(
                success=False,
                message=f"Task not found or permission denied"
            )

        # Generate AI insights for the task
        insights = await generate_task_insights(task)

        insights_text = f"""AI Insights for '{task.title}':
{insights}

Current Status: {task.status}
Priority: {task.priority}
AI Suggested Priority: {task.ai_priority or 'Not analyzed'}
Estimated Duration: {task.estimated_duration or 'Not set'} minutes
AI Estimated Duration: {task.ai_estimated_duration or 'Not analyzed'} minutes
"""

        return TaskResult(
            success=True,
            message=insights_text,
            task_id=str(task.id),
            task_title=task.title
        )

    except Exception as e:
        return TaskResult(
            success=False,
            message=f"Failed to retrieve task insights: {str(e)}"
        )


@function_tool(strict_mode=False)
async def get_overall_productivity_insights(
    ctx: RunContextWrapper[TaskContext],
) -> TaskResult:
    """Get AI-powered productivity insights based on all user tasks.

    Args:
        ctx: RunContextWrapper containing user_id and db_session

    Returns:
        TaskResult with productivity insights and recommendations
    """
    try:
        from app.services.task_service import get_user_tasks as get_user_tasks_service

        # Get all user tasks
        all_tasks, _ = get_user_tasks_service(
            db=ctx.context.db_session,
            user_id=ctx.context.user_id
        )

        if not all_tasks:
            return TaskResult(
                success=False,
                message=f"No tasks found for productivity analysis"
            )

        # Generate AI insights for all tasks
        from app.services.ai_service import generate_productivity_insights
        insights = await generate_productivity_insights(all_tasks)

        return TaskResult(
            success=True,
            message=f"Productivity Insights:\n{insights}",
            task_id=None,
            task_title="Productivity Analysis"
        )

    except Exception as e:
        return TaskResult(
            success=False,
            message=f"Failed to retrieve productivity insights: {str(e)}"
        )


# Export all tools for agent
TASK_TOOLS = [
    add_task,
    update_task,
    delete_task,
    get_task_info,
    get_task_insights,
    get_overall_productivity_insights,
]
