"""Scheduler Subagent - Reusable Intelligence for Task Scheduling.

This subagent specializes in scheduling tasks and managing deadlines
with intelligent time management recommendations.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from app.models.task import Task, TaskStatus, TaskPriority
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScheduleSuggestion(BaseModel):
    """A suggested time slot for a task."""
    task_id: str
    task_title: str
    suggested_start: datetime
    suggested_end: datetime
    reason: str


class DailySchedule(BaseModel):
    """Daily schedule with task allocations."""
    date: str
    tasks: list[ScheduleSuggestion]
    total_hours: float
    free_hours: float
    conflicts: list[str]


class SchedulerAgent:
    """Subagent for intelligent task scheduling.

    This is a reusable intelligence component that helps users
    plan their time effectively.

    Features:
    - Smart task scheduling based on priority and deadline
    - Workload balancing across days
    - Conflict detection
    - Buffer time recommendations
    - Focus time suggestions
    """

    def __init__(self):
        self.work_hours = (9, 17)  # 9 AM to 5 PM default
        self.max_hours_per_day = 8
        self.buffer_between_tasks = 0.25  # 15 minutes

    async def generate_schedule(
        self,
        tasks: list[Task],
        days_ahead: int = 7,
        work_hours: tuple[int, int] = (9, 17)
    ) -> list[DailySchedule]:
        """Generate a schedule for the given tasks.

        Args:
            tasks: List of tasks to schedule
            days_ahead: Number of days to plan
            work_hours: Working hours tuple (start, end)

        Returns:
            List of DailySchedule objects
        """
        self.work_hours = work_hours
        self.max_hours_per_day = work_hours[1] - work_hours[0]

        # Filter schedulable tasks
        schedulable = [
            t for t in tasks
            if t.status != TaskStatus.COMPLETED
        ]

        # Sort by priority and deadline
        schedulable.sort(key=lambda t: (
            self._priority_score(t.priority),
            t.deadline or datetime.max.replace(tzinfo=timezone.utc)
        ))

        # Generate daily schedules
        schedules = []
        now = datetime.now(timezone.utc)

        for day_offset in range(days_ahead):
            day = now + timedelta(days=day_offset)
            day_start = day.replace(
                hour=work_hours[0], minute=0, second=0, microsecond=0
            )

            daily_tasks = []
            current_time = day_start
            total_hours = 0
            conflicts = []

            for task in schedulable:
                # Skip if already scheduled
                if any(s.task_id == str(task.id) for s in daily_tasks):
                    continue

                # Skip if deadline is in the past relative to this day
                if task.deadline and task.deadline.date() < day.date():
                    conflicts.append(f"Task '{task.title}' is overdue")
                    continue

                # Check if task should be scheduled today
                if task.deadline and task.deadline.date() == day.date():
                    # Must be done today
                    pass
                elif total_hours >= self.max_hours_per_day:
                    # No more capacity
                    continue

                # Estimate duration
                duration = task.estimated_duration or self._estimate_duration(task)
                duration_hours = duration / 60 if duration > 60 else duration

                # Check if fits in day
                if total_hours + duration_hours > self.max_hours_per_day:
                    if task.deadline and task.deadline.date() == day.date():
                        conflicts.append(f"Task '{task.title}' may not fit in today's schedule")
                    continue

                # Schedule the task
                end_time = current_time + timedelta(hours=duration_hours)

                daily_tasks.append(ScheduleSuggestion(
                    task_id=str(task.id),
                    task_title=task.title,
                    suggested_start=current_time,
                    suggested_end=end_time,
                    reason=self._get_scheduling_reason(task, day)
                ))

                total_hours += duration_hours + self.buffer_between_tasks
                current_time = end_time + timedelta(hours=self.buffer_between_tasks)

            schedules.append(DailySchedule(
                date=day.strftime("%Y-%m-%d"),
                tasks=daily_tasks,
                total_hours=round(total_hours, 1),
                free_hours=round(self.max_hours_per_day - total_hours, 1),
                conflicts=conflicts
            ))

        return schedules

    async def suggest_reschedule(
        self,
        task: Task,
        tasks: list[Task],
        new_time: Optional[datetime] = None
    ) -> ScheduleSuggestion:
        """Suggest a new time slot for rescheduling a task.

        Args:
            task: Task to reschedule
            tasks: All user's tasks
            new_time: Optional preferred new time

        Returns:
            ScheduleSuggestion with new time slot
        """
        if new_time:
            duration = task.estimated_duration or self._estimate_duration(task)
            return ScheduleSuggestion(
                task_id=str(task.id),
                task_title=task.title,
                suggested_start=new_time,
                suggested_end=new_time + timedelta(hours=duration),
                reason="Rescheduled to requested time"
            )

        # Find next available slot
        now = datetime.now(timezone.utc)
        schedule = await self.generate_schedule(tasks, days_ahead=3)

        for day in schedule:
            if day.free_hours >= 1:  # At least 1 hour free
                # Find a gap
                for i, slot in enumerate(day.tasks):
                    if i == 0:
                        # Check morning slot
                        day_start = datetime.fromisoformat(day.date).replace(
                            hour=self.work_hours[0], tzinfo=timezone.utc
                        )
                        if slot.suggested_start > day_start + timedelta(hours=1):
                            duration = task.estimated_duration or 1
                            return ScheduleSuggestion(
                                task_id=str(task.id),
                                task_title=task.title,
                                suggested_start=day_start,
                                suggested_end=day_start + timedelta(hours=duration),
                                reason=f"Found opening on {day.date}"
                            )

        # Default: schedule for next day morning
        tomorrow = now + timedelta(days=1)
        start = tomorrow.replace(hour=self.work_hours[0], minute=0, second=0, microsecond=0)
        duration = task.estimated_duration or 1

        return ScheduleSuggestion(
            task_id=str(task.id),
            task_title=task.title,
            suggested_start=start,
            suggested_end=start + timedelta(hours=duration),
            reason="Scheduled for next available morning slot"
        )

    def _priority_score(self, priority: TaskPriority) -> int:
        """Get numeric score for priority (lower = higher priority)."""
        scores = {
            TaskPriority.URGENT: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        return scores.get(priority, 2)

    def _estimate_duration(self, task: Task) -> float:
        """Estimate task duration in hours if not provided."""
        # Simple heuristic
        title_len = len(task.title)
        if title_len < 20:
            return 0.5
        elif title_len < 50:
            return 1.0
        else:
            return 2.0

    def _get_scheduling_reason(self, task: Task, day: datetime) -> str:
        """Get reason for scheduling task on this day."""
        if task.deadline:
            if task.deadline.date() == day.date():
                return "Due today - must complete"
            elif task.deadline.date() == (day + timedelta(days=1)).date():
                return "Due tomorrow - start early"
            elif (task.deadline - day).days <= 3:
                return "Approaching deadline"

        if task.priority == TaskPriority.URGENT:
            return "Urgent priority"
        elif task.priority == TaskPriority.HIGH:
            return "High priority task"

        return "Scheduled based on priority"


# Singleton instance for reuse
scheduler_agent = SchedulerAgent()
