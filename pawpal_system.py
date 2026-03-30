from datetime import datetime, timedelta

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

TIME_SLOT_START = {
    "morning": datetime(2000, 1, 1, 8, 0),
    "afternoon": datetime(2000, 1, 1, 13, 0),
    "evening": datetime(2000, 1, 1, 18, 0),
}


class CareTask:
    def __init__(self, title, duration_minutes, priority, task_type=None,
                 required=False, preferred_time=None, frequency="once"):
        """Represents a single pet care task with scheduling metadata."""
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low", "medium", "high"
        self.task_type = task_type        # e.g. "feeding", "exercise", "grooming"
        self.required = required
        self.preferred_time = preferred_time  # "morning", "afternoon", "evening", or None
        self.frequency = frequency        # "once", "daily", "weekly"
        self.completed = False
        self.next_due = datetime.today().date()

    def mark_complete(self):
        """Mark the task complete and advance next_due for recurring tasks."""
        self.completed = True
        if self.frequency == "daily":
            self.next_due = datetime.today().date() + timedelta(days=1)
            self.completed = False
        elif self.frequency == "weekly":
            self.next_due = datetime.today().date() + timedelta(weeks=1)
            self.completed = False

    def __repr__(self):
        """Return a concise string representation of the task."""
        return f"CareTask({self.title!r}, {self.duration_minutes}min, {self.priority})"


class Pet:
    def __init__(self, name, species, age):
        """Stores basic information about a pet."""
        self.name = name
        self.species = species
        self.age = age


class Owner:
    def __init__(self, name, available_minutes, preferences=None):
        """Represents the pet owner and their daily scheduling constraints."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or []  # preferred time blocks e.g. ["evening"]


class ScheduledTask:
    def __init__(self, task, start_time, reason):
        """A CareTask placed at a specific time in the daily plan."""
        self.task = task
        self.start_time = start_time  # datetime
        self.reason = reason

    @property
    def end_time(self):
        """Calculate end time from start time and task duration."""
        return self.start_time + timedelta(minutes=self.task.duration_minutes)


class DailyPlan:
    def __init__(self, scheduled_tasks):
        """A complete daily schedule with all placed tasks."""
        self.scheduled_tasks = scheduled_tasks
        self.total_minutes = sum(st.task.duration_minutes for st in scheduled_tasks)

    def summary(self):
        """Return a formatted string of the full daily schedule."""
        if not self.scheduled_tasks:
            return "No tasks scheduled."
        lines = [f"Daily Plan — {self.total_minutes} minutes total\n"]
        for st in self.scheduled_tasks:
            start = st.start_time.strftime("%I:%M %p")
            end = st.end_time.strftime("%I:%M %p")
            lines.append(f"  {start} – {end}  {st.task.title} ({st.task.priority} priority)")
            lines.append(f"    Reason: {st.reason}")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner, pet, tasks):
        """Initialize the scheduler with an owner, pet, and list of tasks."""
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def prioritize_tasks(self):
        """Sort tasks by required flag, owner preference match, then priority."""
        return sorted(
            self.tasks,
            key=lambda t: (
                t.required,
                self._preference_score(t),
                PRIORITY_RANK.get(t.priority, 0),
            ),
            reverse=True,
        )

    def build_plan(self):
        """Build a DailyPlan by greedily fitting prioritized tasks into available time."""
        prioritized = self.prioritize_tasks()
        remaining_minutes = self.owner.available_minutes
        slot_cursors = {k: v for k, v in TIME_SLOT_START.items()}
        scheduled = []

        for task in prioritized:
            if task.duration_minutes > remaining_minutes:
                continue
            slot = task.preferred_time if task.preferred_time in slot_cursors else "morning"
            start_time = slot_cursors[slot]
            reason = self._reason(task, remaining_minutes)
            scheduled.append(ScheduledTask(task, start_time, reason))
            slot_cursors[slot] += timedelta(minutes=task.duration_minutes)
            remaining_minutes -= task.duration_minutes

        return DailyPlan(scheduled)

    def detect_conflicts(self, plan):
        """Return a list of warning strings for tasks that overlap in the same time slot."""
        warnings = []
        seen = []
        for st in plan.scheduled_tasks:
            for other in seen:
                if st.start_time < other.end_time and st.end_time > other.start_time:
                    warnings.append(
                        f"Conflict: '{st.task.title}' and '{other.task.title}' overlap "
                        f"({st.start_time.strftime('%I:%M %p')} – {st.end_time.strftime('%I:%M %p')})"
                    )
            seen.append(st)
        return warnings

    def explain_plan(self, plan):
        """Return a plain-English explanation of every scheduled task."""
        lines = [
            f"Plan for {self.pet.name} ({self.pet.species}), owner: {self.owner.name}",
            f"Available time: {self.owner.available_minutes} minutes",
            f"Scheduled: {len(plan.scheduled_tasks)} tasks ({plan.total_minutes} min used)\n",
        ]
        for st in plan.scheduled_tasks:
            lines.append(f"• {st.task.title}: {st.reason}")
        return "\n".join(lines)

    def _reason(self, task, remaining_minutes):
        """Build a human-readable reason string for why a task was scheduled."""
        parts = []
        if task.required:
            parts.append("required task")
        if self._preference_score(task):
            parts.append("matches owner preference")
        parts.append(f"{task.priority} priority")
        if task.preferred_time:
            parts.append(f"preferred in the {task.preferred_time}")
        parts.append(f"{remaining_minutes} min remaining when scheduled")
        return ", ".join(parts)

    def _preference_score(self, task):
        """Return 1 if the task's preferred time matches an owner preference, else 0."""
        if task.preferred_time and task.preferred_time in self.owner.preferences:
            return 1
        return 0
