from datetime import datetime, timedelta

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

TIME_SLOT_START = {
    "morning": datetime(2000, 1, 1, 8, 0),
    "afternoon": datetime(2000, 1, 1, 13, 0),
    "evening": datetime(2000, 1, 1, 18, 0),
}


class CareTask:
    def __init__(self, title, duration_minutes, priority, task_type=None, required=False, preferred_time=None):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low", "medium", "high"
        self.task_type = task_type        # e.g. "feeding", "exercise", "grooming"
        self.required = required
        self.preferred_time = preferred_time  # "morning", "afternoon", "evening", or None

    def __repr__(self):
        return f"CareTask({self.title!r}, {self.duration_minutes}min, {self.priority})"


class Pet:
    def __init__(self, name, species, age):
        self.name = name
        self.species = species
        self.age = age


class Owner:
    def __init__(self, name, available_minutes, preferences=None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or []


class ScheduledTask:
    def __init__(self, task, start_time, reason):
        self.task = task
        self.start_time = start_time
        self.reason = reason

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.task.duration_minutes)


class DailyPlan:
    def __init__(self, scheduled_tasks):
        self.scheduled_tasks = scheduled_tasks
        self.total_minutes = sum(st.task.duration_minutes for st in scheduled_tasks)

    def summary(self):
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
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def prioritize_tasks(self):
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

    def explain_plan(self, plan):
        lines = [
            f"Plan for {self.pet.name} ({self.pet.species}), owner: {self.owner.name}",
            f"Available time: {self.owner.available_minutes} minutes",
            f"Scheduled: {len(plan.scheduled_tasks)} tasks ({plan.total_minutes} min used)\n",
        ]
        for st in plan.scheduled_tasks:
            lines.append(f"• {st.task.title}: {st.reason}")
        return "\n".join(lines)

    def _reason(self, task, remaining_minutes):
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
        if task.preferred_time and task.preferred_time in self.owner.preferences:
            return 1
        return 0
