"""Event handling API endpoints for Dapr integration.

Receives events from Kafka via Dapr pub/sub.
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


class CloudEvent(BaseModel):
    """CloudEvents format for Dapr pub/sub."""
    id: str
    source: str
    type: str
    specversion: str = "1.0"
    datacontenttype: str = "application/json"
    data: dict[str, Any]
    time: Optional[datetime] = None


@router.post("/task")
async def handle_task_event(request: Request):
    """Handle task events from Kafka via Dapr.

    Processes task-events topic messages.
    """
    try:
        body = await request.json()
        event_type = body.get("data", {}).get("event_type", "unknown")

        logger.info(f"Received task event: {event_type}", extra={"body": body})

        # Process based on event type
        if event_type == "task.completed":
            # Trigger recurring task generation
            task_id = body.get("data", {}).get("data", {}).get("task_id")
            logger.info(f"Task completed event received: {task_id}")

        elif event_type == "task.created":
            # Could trigger AI analysis
            task_id = body.get("data", {}).get("data", {}).get("task_id")
            logger.info(f"Task created event received: {task_id}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing task event: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/notification")
async def handle_notification_event(request: Request):
    """Handle notification events from Kafka via Dapr.

    Processes notifications topic messages for reminders.
    """
    try:
        body = await request.json()
        event_type = body.get("data", {}).get("event_type", "unknown")

        logger.info(f"Received notification event: {event_type}", extra={"body": body})

        if event_type == "reminder.due":
            # Process reminder notification
            data = body.get("data", {}).get("data", {})
            task_id = data.get("task_id")
            user_id = data.get("user_id")
            title = data.get("title")

            logger.info(f"Reminder due for task: {task_id}, user: {user_id}")
            # Here you would send push notification via WebSocket or push service

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing notification event: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/health")
async def events_health():
    """Health check for events endpoint."""
    return {"status": "healthy", "service": "events"}
