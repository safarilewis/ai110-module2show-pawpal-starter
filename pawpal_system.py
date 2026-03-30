class CareTask:
    def __init__(self, title, duration_minutes, priority, task_type=None, required=False, preferred_time=None):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority          # "low", "medium", "high"
        self.task_type = task_type        # e.g. "feeding", "exercise", "grooming"
        self.required = required
        self.preferred_time = preferred_time  # "morning", "afternoon", "evening", or None

    def __repr__(self):
        pass


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
        pass


class DailyPlan:
    def __init__(self, scheduled_tasks):
        self.scheduled_tasks = scheduled_tasks
        self.total_minutes = 0

    def summary(self):
        pass


class Scheduler:
    def __init__(self, owner, pet, tasks):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def prioritize_tasks(self):
        pass

    def build_plan(self):
        pass

    def explain_plan(self, plan):
        pass
