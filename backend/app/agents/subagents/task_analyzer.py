"""Task Analyzer Subagent - Reusable Intelligence for Task Analysis.

This subagent specializes in analyzing tasks and providing insights
about priority, duration, dependencies, and complexity.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TaskAnalysisResult(BaseModel):
    """Result of task analysis."""
    suggested_priority: str  # low, medium, high, urgent
    estimated_hours: float
    complexity: str  # simple, moderate, complex
    suggested_tags: list[str]
    suggested_category: Optional[str]
    dependencies: list[str]
    risks: list[str]
    breakdown: list[str]  # Suggested subtasks


class TaskAnalyzerAgent:
    """Subagent for analyzing tasks and providing intelligent suggestions.

    This is a reusable intelligence component that can be invoked
    from multiple places in the application.

    Features:
    - Priority suggestion based on keywords and deadlines
    - Duration estimation based on task complexity
    - Task breakdown into subtasks
    - Risk identification
    - Category and tag suggestions
    """

    def __init__(self):
        self.priority_keywords = {
            "urgent": ["urgent", "asap", "immediately", "critical", "emergency", "deadline today"],
            "high": ["important", "priority", "must", "need to", "required", "deadline"],
            "medium": ["should", "would like", "plan to", "want to"],
            "low": ["maybe", "sometime", "eventually", "when possible", "nice to have"]
        }
        self.category_keywords = {
            "work": ["meeting", "project", "client", "report", "presentation", "email", "call"],
            "personal": ["home", "family", "health", "exercise", "hobby", "friends"],
            "shopping": ["buy", "purchase", "order", "groceries", "shopping"],
            "health": ["doctor", "medicine", "gym", "exercise", "workout", "health"],
            "finance": ["pay", "bill", "budget", "bank", "investment", "tax"],
            "learning": ["study", "learn", "course", "read", "research", "practice"]
        }

    async def analyze(
        self,
        title: str,
        description: Optional[str] = None,
        deadline: Optional[datetime] = None
    ) -> TaskAnalysisResult:
        """Analyze a task and provide intelligent suggestions.

        Args:
            title: Task title
            description: Optional task description
            deadline: Optional deadline

        Returns:
            TaskAnalysisResult with suggestions
        """
        text = f"{title} {description or ''}".lower()

        # Determine priority
        priority = self._suggest_priority(text, deadline)

        # Estimate duration
        hours = self._estimate_duration(text)

        # Determine complexity
        complexity = self._assess_complexity(text, hours)

        # Suggest tags
        tags = self._suggest_tags(text)

        # Suggest category
        category = self._suggest_category(text)

        # Identify dependencies
        dependencies = self._identify_dependencies(text)

        # Identify risks
        risks = self._identify_risks(text, deadline)

        # Generate task breakdown
        breakdown = self._generate_breakdown(title, complexity)

        return TaskAnalysisResult(
            suggested_priority=priority,
            estimated_hours=hours,
            complexity=complexity,
            suggested_tags=tags,
            suggested_category=category,
            dependencies=dependencies,
            risks=risks,
            breakdown=breakdown
        )

    def _suggest_priority(self, text: str, deadline: Optional[datetime]) -> str:
        """Suggest task priority based on content and deadline."""
        # Check deadline urgency
        if deadline:
            hours_until = (deadline - datetime.now(deadline.tzinfo)).total_seconds() / 3600
            if hours_until < 24:
                return "urgent"
            elif hours_until < 72:
                return "high"

        # Check keywords
        for priority, keywords in self.priority_keywords.items():
            if any(kw in text for kw in keywords):
                return priority

        return "medium"

    def _estimate_duration(self, text: str) -> float:
        """Estimate task duration in hours."""
        # Simple heuristic based on keywords
        if any(word in text for word in ["quick", "simple", "brief", "short"]):
            return 0.5
        elif any(word in text for word in ["meeting", "call", "review"]):
            return 1.0
        elif any(word in text for word in ["project", "report", "presentation"]):
            return 4.0
        elif any(word in text for word in ["research", "analysis", "study"]):
            return 3.0
        else:
            return 1.5

    def _assess_complexity(self, text: str, hours: float) -> str:
        """Assess task complexity."""
        if hours <= 1:
            return "simple"
        elif hours <= 3:
            return "moderate"
        else:
            return "complex"

    def _suggest_tags(self, text: str) -> list[str]:
        """Suggest relevant tags for the task."""
        tags = []
        tag_keywords = {
            "meeting": ["meeting", "call", "discussion"],
            "deadline": ["deadline", "due", "submit"],
            "followup": ["follow up", "followup", "check on"],
            "review": ["review", "approve", "feedback"],
            "creative": ["design", "write", "create", "draft"]
        }
        for tag, keywords in tag_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
        return tags[:5]  # Max 5 tags

    def _suggest_category(self, text: str) -> Optional[str]:
        """Suggest a category for the task."""
        for category, keywords in self.category_keywords.items():
            if any(kw in text for kw in keywords):
                return category
        return None

    def _identify_dependencies(self, text: str) -> list[str]:
        """Identify potential task dependencies."""
        dependencies = []
        dependency_phrases = [
            ("after", "Complete prerequisite task first"),
            ("waiting for", "Waiting for external input"),
            ("need", "Gather required resources"),
            ("depends on", "Resolve dependency first")
        ]
        for phrase, dep in dependency_phrases:
            if phrase in text:
                dependencies.append(dep)
        return dependencies

    def _identify_risks(self, text: str, deadline: Optional[datetime]) -> list[str]:
        """Identify potential risks for the task."""
        risks = []
        if deadline:
            hours_until = (deadline - datetime.now(deadline.tzinfo)).total_seconds() / 3600
            if hours_until < 24:
                risks.append("Very tight deadline - consider starting immediately")
            elif hours_until < 48:
                risks.append("Short timeline - plan carefully")

        if "complex" in text or "difficult" in text:
            risks.append("Task may be more complex than expected")

        if "new" in text or "first time" in text:
            risks.append("Unfamiliar task - allow extra time for learning")

        return risks

    def _generate_breakdown(self, title: str, complexity: str) -> list[str]:
        """Generate suggested subtask breakdown."""
        if complexity == "simple":
            return [f"Complete: {title}"]

        # Generic breakdown for moderate/complex tasks
        return [
            f"Plan approach for: {title}",
            f"Gather resources/information",
            f"Execute main work",
            f"Review and verify",
            f"Finalize and close"
        ][:3 if complexity == "moderate" else 5]


# Singleton instance for reuse
task_analyzer = TaskAnalyzerAgent()
