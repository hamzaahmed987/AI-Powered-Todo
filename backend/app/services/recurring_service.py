"""Recurring tasks service.

Handles creation and management of recurring tasks.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from dateutil.relativedelta import relativedelta

from app.models.task import Task, TaskStatus, RecurrencePattern
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RecurringTaskService:
    """Service for managing recurring tasks.

    Handles:
    - Generating next occurrence of recurring tasks
    - Processing completed recurring tasks
    - Managing recurrence patterns
    """

    def get_next_occurrence(
        self,
        current_date: datetime,
        pattern: RecurrencePattern
    ) -> datetime:
        """Calculate the next occurrence date based on pattern.

        Args:
            current_date: Current/base date
            pattern: Recurrence pattern

        Returns:
            datetime: Next occurrence date
        """
        if pattern == RecurrencePattern.DAILY:
            return current_date + timedelta(days=1)
        elif pattern == RecurrencePattern.WEEKLY:
            return current_date + timedelta(weeks=1)
        elif pattern == RecurrencePattern.BIWEEKLY:
            return current_date + timedelta(weeks=2)
        elif pattern == RecurrencePattern.MONTHLY:
            return current_date + relativedelta(months=1)
        elif pattern == RecurrencePattern.YEARLY:
            return current_date + relativedelta(years=1)
        else:
            return current_date

    async def generate_next_task(
        self,
        db: AsyncSession,
        completed_task: Task
    ) -> Optional[Task]:
        """Generate the next occurrence of a recurring task.

        Called when a recurring task is completed.

        Args:
            db: Database session
            completed_task: The completed recurring task

        Returns:
            Optional[Task]: The newly created task, or None if recurrence ended
        """
        if not completed_task.is_recurring:
            return None

        if completed_task.recurrence_pattern == RecurrencePattern.NONE:
            return None

        # Check if recurrence has ended
        now = datetime.now(timezone.utc)
        if completed_task.recurrence_end_date and now >= completed_task.recurrence_end_date:
            logger.info(f"Recurrence ended for task {completed_task.id}")
            return None

        # Calculate next deadline
        next_deadline = None
        if completed_task.deadline:
            next_deadline = self.get_next_occurrence(
                completed_task.deadline,
                completed_task.recurrence_pattern
            )

        # Calculate next reminder
        next_reminder = None
        if completed_task.reminder_enabled and completed_task.reminder_time:
            next_reminder = self.get_next_occurrence(
                completed_task.reminder_time,
                completed_task.recurrence_pattern
            )

        # Create new task
        new_task = Task(
            id=uuid4(),
            owner_id=completed_task.owner_id,
            title=completed_task.title,
            description=completed_task.description,
            status=TaskStatus.PENDING,
            priority=completed_task.priority,
            deadline=next_deadline,
            estimated_duration=completed_task.estimated_duration,
            tags=completed_task.tags,
            category=completed_task.category,
            is_recurring=True,
            recurrence_pattern=completed_task.recurrence_pattern,
            recurrence_end_date=completed_task.recurrence_end_date,
            parent_task_id=completed_task.parent_task_id or completed_task.id,
            reminder_enabled=completed_task.reminder_enabled,
            reminder_time=next_reminder,
            reminder_sent=False
        )

        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)

        logger.info(
            f"Generated recurring task {new_task.id} from {completed_task.id}",
            extra={"pattern": completed_task.recurrence_pattern.value}
        )

        return new_task

    async def get_recurring_tasks(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> list[Task]:
        """Get all recurring tasks for a user.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            List of recurring tasks
        """
        result = await db.execute(
            select(Task).where(
                and_(
                    Task.owner_id == user_id,
                    Task.is_recurring == True
                )
            ).order_by(Task.deadline)
        )
        return result.scalars().all()

    async def process_due_recurring_tasks(
        self,
        db: AsyncSession
    ) -> list[Task]:
        """Process all recurring tasks that need generation.

        Called by scheduler/cron job to generate upcoming tasks.

        Args:
            db: Database session

        Returns:
            List of newly generated tasks
        """
        # Find completed recurring tasks that need next occurrence
        result = await db.execute(
            select(Task).where(
                and_(
                    Task.is_recurring == True,
                    Task.status == TaskStatus.COMPLETED,
                    Task.recurrence_pattern != RecurrencePattern.NONE
                )
            )
        )
        completed_tasks = result.scalars().all()

        generated_tasks = []
        for task in completed_tasks:
            new_task = await self.generate_next_task(db, task)
            if new_task:
                generated_tasks.append(new_task)
                # Mark original as processed
                task.is_recurring = False  # Prevent duplicate generation
                await db.commit()

        logger.info(f"Generated {len(generated_tasks)} recurring tasks")
        return generated_tasks


# Singleton instance
recurring_service = RecurringTaskService()
