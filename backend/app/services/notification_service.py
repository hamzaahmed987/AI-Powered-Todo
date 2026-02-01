"""Notification service for task reminders and alerts.

Handles browser push notifications and reminder scheduling.
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.task import Task
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotificationService:
    """Service for managing task notifications and reminders.

    Provides functionality for:
    - Checking due reminders
    - Sending push notifications via web-push
    - Managing notification subscriptions
    """

    def __init__(self):
        self.vapid_private_key = os.getenv("VAPID_PRIVATE_KEY", "")
        self.vapid_public_key = os.getenv("VAPID_PUBLIC_KEY", "")
        self.vapid_email = os.getenv("VAPID_EMAIL", "mailto:admin@example.com")

    async def get_due_reminders(
        self,
        db: AsyncSession,
        window_minutes: int = 15
    ) -> list[Task]:
        """Get tasks with reminders due in the next window.

        Args:
            db: Database session
            window_minutes: Time window to check (default 15 minutes)

        Returns:
            List of tasks with due reminders
        """
        now = datetime.now(timezone.utc)
        window_end = now + timedelta(minutes=window_minutes)

        result = await db.execute(
            select(Task).where(
                and_(
                    Task.reminder_enabled == True,
                    Task.reminder_sent == False,
                    Task.reminder_time <= window_end,
                    Task.reminder_time >= now,
                    Task.status != "completed"
                )
            )
        )
        return result.scalars().all()

    async def mark_reminder_sent(self, db: AsyncSession, task_id: UUID) -> bool:
        """Mark a task's reminder as sent.

        Args:
            db: Database session
            task_id: Task UUID

        Returns:
            bool: True if updated successfully
        """
        result = await db.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            task.reminder_sent = True
            await db.commit()
            return True
        return False

    def create_notification_payload(
        self,
        title: str,
        body: str,
        task_id: Optional[UUID] = None,
        deadline: Optional[datetime] = None,
        icon: str = "/icon-192x192.png",
        badge: str = "/badge-72x72.png"
    ) -> dict:
        """Create a web push notification payload.

        Args:
            title: Notification title
            body: Notification body text
            task_id: Optional task ID for deep linking
            deadline: Optional deadline to display
            icon: Notification icon URL
            badge: Notification badge URL

        Returns:
            dict: Web push notification payload
        """
        payload = {
            "title": title,
            "body": body,
            "icon": icon,
            "badge": badge,
            "tag": f"task-{task_id}" if task_id else "todo-reminder",
            "requireInteraction": True,
            "actions": [
                {"action": "view", "title": "View Task"},
                {"action": "dismiss", "title": "Dismiss"}
            ],
            "data": {
                "task_id": str(task_id) if task_id else None,
                "deadline": deadline.isoformat() if deadline else None,
                "url": f"/dashboard?task={task_id}" if task_id else "/dashboard"
            }
        }
        return payload

    async def send_push_notification(
        self,
        subscription: dict,
        payload: dict
    ) -> bool:
        """Send a web push notification.

        Args:
            subscription: Web push subscription object
            payload: Notification payload

        Returns:
            bool: True if sent successfully
        """
        try:
            from pywebpush import webpush, WebPushException

            webpush(
                subscription_info=subscription,
                data=str(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims={"sub": self.vapid_email}
            )
            logger.info(f"Push notification sent: {payload.get('title')}")
            return True
        except ImportError:
            logger.warning("pywebpush not installed, skipping push notification")
            return False
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False

    def format_reminder_message(
        self,
        task_title: str,
        deadline: Optional[datetime],
        language: str = "en"
    ) -> tuple[str, str]:
        """Format reminder notification message.

        Args:
            task_title: Task title
            deadline: Task deadline
            language: Language code (en/ur)

        Returns:
            tuple: (title, body) in specified language
        """
        if language == "ur":
            # Urdu translations
            title = "یاددہانی: کام باقی ہے"
            if deadline:
                time_str = deadline.strftime("%I:%M %p")
                body = f"'{task_title}' کی آخری تاریخ {time_str} ہے"
            else:
                body = f"'{task_title}' مکمل کرنا نہ بھولیں"
        else:
            # English (default)
            title = "Task Reminder"
            if deadline:
                time_str = deadline.strftime("%I:%M %p on %b %d")
                body = f"'{task_title}' is due at {time_str}"
            else:
                body = f"Don't forget to complete '{task_title}'"

        return title, body


# Singleton instance
notification_service = NotificationService()
