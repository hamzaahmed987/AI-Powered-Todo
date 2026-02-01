# Task Intelligence Skill

This skill provides reusable AI-powered task analysis and productivity coaching.

## Available Capabilities

### 1. Task Analysis
Analyze a task and get intelligent suggestions:
- Priority recommendation
- Duration estimation
- Complexity assessment
- Tag suggestions
- Risk identification

**Usage:**
```python
from app.agents.subagents import TaskAnalyzerAgent

analyzer = TaskAnalyzerAgent()
result = await analyzer.analyze(
    title="Complete quarterly report",
    description="Compile data from all departments",
    deadline=datetime(2024, 12, 31)
)
print(result.suggested_priority)  # "high"
print(result.estimated_hours)     # 4.0
print(result.suggested_tags)      # ["deadline", "report"]
```

### 2. Productivity Coaching
Get personalized productivity insights:
- Completion rate analysis
- Workload assessment
- Achievement recognition
- Focus area identification

**Usage:**
```python
from app.agents.subagents import ProductivityCoachAgent

coach = ProductivityCoachAgent()
insights = await coach.analyze(user_tasks, days_back=30)
print(insights.completion_rate)     # 75.5
print(insights.workload_assessment) # "balanced"
print(insights.suggestions)         # ["Focus on...", ...]
```

### 3. Smart Scheduling
Generate optimized daily schedules:
- Priority-based ordering
- Deadline awareness
- Workload balancing
- Conflict detection

**Usage:**
```python
from app.agents.subagents import SchedulerAgent

scheduler = SchedulerAgent()
schedule = await scheduler.generate_schedule(tasks, days_ahead=7)
for day in schedule:
    print(f"{day.date}: {day.total_hours}h scheduled, {day.free_hours}h free")
```

## Integration Points

These subagents are integrated into:
- Task creation API (auto-analysis)
- Agent chat (natural language queries)
- Dashboard (productivity insights)
- Notifications (smart reminders)
