"""Productivity Coach Subagent - Reusable Intelligence for Productivity Insights.

This subagent specializes in analyzing user's task patterns and providing
personalized productivity recommendations.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from collections import Counter

from app.models.task import Task, TaskStatus, TaskPriority
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ProductivityInsights(BaseModel):
    """Productivity analysis results."""
    completion_rate: float  # 0-100%
    avg_completion_time: Optional[float]  # hours
    most_productive_time: Optional[str]
    overdue_count: int
    suggestions: list[str]
    focus_areas: list[str]
    achievements: list[str]
    workload_assessment: str  # light, balanced, heavy, overloaded


class ProductivityCoachAgent:
    """Subagent for providing productivity coaching and insights.

    This is a reusable intelligence component that analyzes task
    patterns and provides personalized recommendations.

    Features:
    - Completion rate analysis
    - Workload assessment
    - Productivity suggestions
    - Achievement recognition
    - Focus area identification
    """

    def __init__(self):
        self.workload_thresholds = {
            "light": 3,
            "balanced": 7,
            "heavy": 12,
            "overloaded": float("inf")
        }

    async def analyze(
        self,
        tasks: list[Task],
        days_back: int = 30
    ) -> ProductivityInsights:
        """Analyze user's tasks and provide productivity insights.

        Args:
            tasks: List of user's tasks
            days_back: Number of days to analyze

        Returns:
            ProductivityInsights with recommendations
        """
        now = datetime.now()
        cutoff = now - timedelta(days=days_back)

        # Filter recent tasks
        recent_tasks = [t for t in tasks if t.created_at and t.created_at >= cutoff]

        # Calculate metrics
        completion_rate = self._calculate_completion_rate(recent_tasks)
        avg_time = self._calculate_avg_completion_time(recent_tasks)
        productive_time = self._find_productive_time(recent_tasks)
        overdue = self._count_overdue(tasks)
        workload = self._assess_workload(tasks)

        # Generate suggestions
        suggestions = self._generate_suggestions(
            completion_rate, overdue, workload, recent_tasks
        )

        # Identify focus areas
        focus_areas = self._identify_focus_areas(tasks)

        # Recognize achievements
        achievements = self._recognize_achievements(recent_tasks, completion_rate)

        return ProductivityInsights(
            completion_rate=completion_rate,
            avg_completion_time=avg_time,
            most_productive_time=productive_time,
            overdue_count=overdue,
            suggestions=suggestions,
            focus_areas=focus_areas,
            achievements=achievements,
            workload_assessment=workload
        )

    def _calculate_completion_rate(self, tasks: list[Task]) -> float:
        """Calculate task completion rate."""
        if not tasks:
            return 0.0
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        return round((completed / len(tasks)) * 100, 1)

    def _calculate_avg_completion_time(self, tasks: list[Task]) -> Optional[float]:
        """Calculate average time to complete tasks."""
        completed_with_time = [
            t for t in tasks
            if t.status == TaskStatus.COMPLETED and t.completed_at and t.created_at
        ]
        if not completed_with_time:
            return None

        total_hours = sum(
            (t.completed_at - t.created_at).total_seconds() / 3600
            for t in completed_with_time
        )
        return round(total_hours / len(completed_with_time), 1)

    def _find_productive_time(self, tasks: list[Task]) -> Optional[str]:
        """Find most productive time of day based on completion patterns."""
        completed = [
            t for t in tasks
            if t.status == TaskStatus.COMPLETED and t.completed_at
        ]
        if not completed:
            return None

        hours = [t.completed_at.hour for t in completed]
        if not hours:
            return None

        most_common_hour = Counter(hours).most_common(1)[0][0]

        if 5 <= most_common_hour < 12:
            return "Morning (5 AM - 12 PM)"
        elif 12 <= most_common_hour < 17:
            return "Afternoon (12 PM - 5 PM)"
        elif 17 <= most_common_hour < 21:
            return "Evening (5 PM - 9 PM)"
        else:
            return "Night (9 PM - 5 AM)"

    def _count_overdue(self, tasks: list[Task]) -> int:
        """Count overdue tasks."""
        now = datetime.now()
        return sum(
            1 for t in tasks
            if t.deadline and t.deadline < now and t.status != TaskStatus.COMPLETED
        )

    def _assess_workload(self, tasks: list[Task]) -> str:
        """Assess current workload level."""
        active_tasks = [
            t for t in tasks
            if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
        ]
        count = len(active_tasks)

        if count <= self.workload_thresholds["light"]:
            return "light"
        elif count <= self.workload_thresholds["balanced"]:
            return "balanced"
        elif count <= self.workload_thresholds["heavy"]:
            return "heavy"
        else:
            return "overloaded"

    def _generate_suggestions(
        self,
        completion_rate: float,
        overdue: int,
        workload: str,
        tasks: list[Task]
    ) -> list[str]:
        """Generate personalized productivity suggestions."""
        suggestions = []

        if completion_rate < 50:
            suggestions.append("Focus on completing existing tasks before adding new ones")
        elif completion_rate > 80:
            suggestions.append("Great completion rate! Consider taking on more challenging tasks")

        if overdue > 0:
            suggestions.append(f"You have {overdue} overdue task(s). Consider rescheduling or prioritizing them")

        if workload == "overloaded":
            suggestions.append("Your workload is high. Consider delegating or deferring some tasks")
        elif workload == "light":
            suggestions.append("You have capacity for more tasks. Set some new goals!")

        # Check for priority balance
        high_priority = sum(1 for t in tasks if t.priority in [TaskPriority.HIGH, TaskPriority.URGENT])
        if high_priority > 5:
            suggestions.append("You have many high-priority tasks. Review and re-prioritize if needed")

        # Time management suggestion
        if any(t.deadline and not t.estimated_duration for t in tasks):
            suggestions.append("Add time estimates to your tasks for better planning")

        return suggestions[:5]  # Max 5 suggestions

    def _identify_focus_areas(self, tasks: list[Task]) -> list[str]:
        """Identify areas that need attention."""
        focus_areas = []

        # Check for stale tasks
        now = datetime.now()
        stale = [
            t for t in tasks
            if t.status == TaskStatus.PENDING
            and t.created_at
            and (now - t.created_at).days > 7
        ]
        if stale:
            focus_areas.append(f"{len(stale)} task(s) pending for over a week")

        # Check for tasks without deadlines
        no_deadline = [
            t for t in tasks
            if t.status != TaskStatus.COMPLETED and not t.deadline
        ]
        if len(no_deadline) > 3:
            focus_areas.append("Many tasks without deadlines - add dates for better planning")

        # Check categories (if available)
        categories = [t.category for t in tasks if t.category]
        if categories:
            most_common = Counter(categories).most_common(1)[0][0]
            focus_areas.append(f"Most tasks are in '{most_common}' category")

        return focus_areas[:3]

    def _recognize_achievements(
        self,
        tasks: list[Task],
        completion_rate: float
    ) -> list[str]:
        """Recognize user achievements."""
        achievements = []

        completed_count = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)

        if completed_count >= 10:
            achievements.append(f"🎯 Completed {completed_count} tasks!")

        if completion_rate >= 90:
            achievements.append("⭐ Outstanding completion rate!")
        elif completion_rate >= 70:
            achievements.append("✅ Great progress on your tasks!")

        # Check for urgent task completions
        urgent_completed = sum(
            1 for t in tasks
            if t.status == TaskStatus.COMPLETED and t.priority == TaskPriority.URGENT
        )
        if urgent_completed > 0:
            achievements.append(f"🔥 Handled {urgent_completed} urgent task(s)!")

        return achievements


# Singleton instance for reuse
productivity_coach = ProductivityCoachAgent()
