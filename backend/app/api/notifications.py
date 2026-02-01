"""Notification API endpoints for push notifications and reminders."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.notification_service import notification_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class PushSubscription(BaseModel):
    """Web Push subscription object."""
    endpoint: str
    keys: dict[str, str]


class NotificationPreferences(BaseModel):
    """User notification preferences."""
    push_enabled: bool = True
    email_enabled: bool = False
    reminder_minutes_before: int = 30
    language: str = "en"


# In-memory subscription store (use Redis/DB in production)
subscriptions: dict[str, PushSubscription] = {}
preferences: dict[str, NotificationPreferences] = {}


@router.post("/subscribe")
async def subscribe_push(
    subscription: PushSubscription,
    current_user: User = Depends(get_current_user)
):
    """Subscribe to push notifications.

    Stores the push subscription for sending notifications.
    """
    user_id = str(current_user.id)
    subscriptions[user_id] = subscription
    logger.info(f"User {user_id} subscribed to push notifications")

    return {
        "message": "Successfully subscribed to push notifications",
        "vapid_public_key": notification_service.vapid_public_key
    }


@router.delete("/unsubscribe")
async def unsubscribe_push(
    current_user: User = Depends(get_current_user)
):
    """Unsubscribe from push notifications."""
    user_id = str(current_user.id)
    if user_id in subscriptions:
        del subscriptions[user_id]
        logger.info(f"User {user_id} unsubscribed from push notifications")

    return {"message": "Successfully unsubscribed from push notifications"}


@router.get("/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get user's notification preferences."""
    user_id = str(current_user.id)
    user_prefs = preferences.get(user_id, NotificationPreferences())
    return user_prefs


@router.put("/preferences")
async def update_preferences(
    prefs: NotificationPreferences,
    current_user: User = Depends(get_current_user)
):
    """Update user's notification preferences."""
    user_id = str(current_user.id)
    preferences[user_id] = prefs
    logger.info(f"User {user_id} updated notification preferences")

    return {"message": "Preferences updated", "preferences": prefs}


@router.post("/test")
async def send_test_notification(
    current_user: User = Depends(get_current_user)
):
    """Send a test push notification to the current user."""
    user_id = str(current_user.id)

    if user_id not in subscriptions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No push subscription found. Please subscribe first."
        )

    subscription = subscriptions[user_id]
    user_prefs = preferences.get(user_id, NotificationPreferences())

    title, body = notification_service.format_reminder_message(
        task_title="Test Task",
        deadline=None,
        language=user_prefs.language
    )

    payload = notification_service.create_notification_payload(
        title=title,
        body=body
    )

    success = await notification_service.send_push_notification(
        subscription=subscription.model_dump(),
        payload=payload
    )

    if success:
        return {"message": "Test notification sent"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )


@router.get("/vapid-key")
async def get_vapid_key():
    """Get the VAPID public key for push subscription."""
    return {"vapid_public_key": notification_service.vapid_public_key}
