import pytest
from datetime import datetime, timedelta, date
from pawpal_system import CareTask, Pet, Owner, ScheduledTask, DailyPlan, Scheduler


# --- Fixtures ---

@pytest.fixture
def owner():
    return Owner("Jordan", available_minutes=60)

@pytest.fixture
def pet():
    return Pet("Mochi", "dog", 3)

@pytest.fixture
def basic_tasks():
    return [
        CareTask("Morning walk", 30, "high", preferred_time="morning"),
        CareTask("Feeding", 10, "high", required=True),
        CareTask("Grooming", 20, "medium", preferred_time="evening"),
        CareTask("Playtime", 15, "low", preferred_time="afternoon"),
    ]


# --- CareTask ---

def test_caretask_repr():
    task = CareTask("Walk", 30, "high")
    assert "Walk" in repr(task)
    assert "30min" in repr(task)
    assert "high" in repr(task)

def test_caretask_defaults():
    task = CareTask("Feed", 10, "medium")
    assert task.required is False
    assert task.preferred_time is None
    assert task.task_type is None
    assert task.frequency == "once"
    assert task.completed is False


# --- Recurring tasks ---

def test_mark_complete_once_task():
    task = CareTask("Bath", 30, "low", frequency="once")
    task.mark_complete()
    assert task.completed is True

def test_daily_task_reschedules_next_day():
    task = CareTask("Feeding", 10, "high", frequency="daily")
    today = date.today()
    task.mark_complete()
    assert task.next_due == today + timedelta(days=1)
    assert task.completed is False  # resets for recurring

def test_weekly_task_reschedules_next_week():
    task = CareTask("Grooming", 20, "medium", frequency="weekly")
    today = date.today()
    task.mark_complete()
    assert task.next_due == today + timedelta(weeks=1)
    assert task.completed is False


# --- ScheduledTask ---

def test_scheduled_task_end_time():
    task = CareTask("Walk", 30, "high")
    start = datetime(2000, 1, 1, 8, 0)
    st = ScheduledTask(task, start, "test reason")
    assert st.end_time.hour == 8
    assert st.end_time.minute == 30


# --- DailyPlan ---

def test_daily_plan_total_minutes():
    tasks = [
        ScheduledTask(CareTask("Walk", 30, "high"), None, ""),
        ScheduledTask(CareTask("Feed", 10, "high"), None, ""),
    ]
    plan = DailyPlan(tasks)
    assert plan.total_minutes == 40

def test_daily_plan_empty_summary():
    plan = DailyPlan([])
    assert plan.summary() == "No tasks scheduled."

def test_daily_plan_summary_contains_task_titles(owner, pet, basic_tasks):
    scheduler = Scheduler(owner, pet, basic_tasks)
    plan = scheduler.build_plan()
    summary = plan.summary()
    for st in plan.scheduled_tasks:
        assert st.task.title in summary


# --- Scheduler.prioritize_tasks ---

def test_required_tasks_come_first(owner, pet):
    tasks = [
        CareTask("Optional walk", 20, "high"),
        CareTask("Medication", 5, "low", required=True),
    ]
    scheduler = Scheduler(owner, pet, tasks)
    prioritized = scheduler.prioritize_tasks()
    assert prioritized[0].title == "Medication"

def test_high_priority_before_low(owner, pet):
    tasks = [
        CareTask("Playtime", 10, "low"),
        CareTask("Feeding", 10, "high"),
    ]
    scheduler = Scheduler(owner, pet, tasks)
    prioritized = scheduler.prioritize_tasks()
    assert prioritized[0].title == "Feeding"

def test_owner_preference_boosts_matching_time_block(pet):
    owner = Owner("Jordan", available_minutes=60, preferences=["evening"])
    tasks = [
        CareTask("Afternoon play", 10, "medium", preferred_time="afternoon"),
        CareTask("Evening groom", 10, "medium", preferred_time="evening"),
    ]
    scheduler = Scheduler(owner, pet, tasks)
    prioritized = scheduler.prioritize_tasks()
    assert prioritized[0].title == "Evening groom"


# --- Scheduler.build_plan ---

def test_tasks_fit_within_available_time(owner, pet, basic_tasks):
    scheduler = Scheduler(owner, pet, basic_tasks)
    plan = scheduler.build_plan()
    assert plan.total_minutes <= owner.available_minutes

def test_task_exceeding_time_is_skipped(owner, pet):
    tasks = [CareTask("Long hike", 120, "high")]
    scheduler = Scheduler(owner, pet, tasks)
    plan = scheduler.build_plan()
    assert len(plan.scheduled_tasks) == 0

def test_required_task_is_scheduled(owner, pet):
    tasks = [
        CareTask("Medication", 5, "low", required=True),
        CareTask("Long bath", 50, "high"),
    ]
    scheduler = Scheduler(owner, pet, tasks)
    plan = scheduler.build_plan()
    titles = [st.task.title for st in plan.scheduled_tasks]
    assert "Medication" in titles

def test_preferred_time_slot_respected(owner, pet):
    tasks = [CareTask("Evening groom", 20, "medium", preferred_time="evening")]
    scheduler = Scheduler(owner, pet, tasks)
    plan = scheduler.build_plan()
    assert len(plan.scheduled_tasks) == 1
    assert plan.scheduled_tasks[0].start_time.hour == 18

def test_sorting_correctness(owner, pet):
    """Tasks should be scheduled in priority order, high before low."""
    tasks = [
        CareTask("Low task", 10, "low"),
        CareTask("High task", 10, "high"),
        CareTask("Medium task", 10, "medium"),
    ]
    scheduler = Scheduler(owner, pet, tasks)
    prioritized = scheduler.prioritize_tasks()
    assert prioritized[0].priority == "high"
    assert prioritized[1].priority == "medium"
    assert prioritized[2].priority == "low"


# --- Conflict detection ---

def test_no_conflicts_when_tasks_sequential(owner, pet):
    tasks = [
        CareTask("Walk", 30, "high", preferred_time="morning"),
        CareTask("Feed", 10, "high", preferred_time="afternoon"),
    ]
    scheduler = Scheduler(owner, pet, tasks)
    plan = scheduler.build_plan()
    conflicts = scheduler.detect_conflicts(plan)
    assert len(conflicts) == 0

def test_conflict_detected_for_overlapping_tasks(pet):
    """Force two tasks into the same slot to trigger a conflict."""
    owner = Owner("Jordan", available_minutes=120)
    start = datetime(2000, 1, 1, 8, 0)
    task_a = CareTask("Walk", 30, "high")
    task_b = CareTask("Feed", 20, "high")
    # Manually build a plan with overlapping times
    st_a = ScheduledTask(task_a, start, "test")
    st_b = ScheduledTask(task_b, start + timedelta(minutes=10), "test")  # overlaps
    plan = DailyPlan([st_a, st_b])
    conflicts = Scheduler(owner, pet, []).detect_conflicts(plan)
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feed" in conflicts[0]


# --- Scheduler.explain_plan ---

def test_explain_plan_contains_owner_and_pet(owner, pet, basic_tasks):
    scheduler = Scheduler(owner, pet, basic_tasks)
    plan = scheduler.build_plan()
    explanation = scheduler.explain_plan(plan)
    assert owner.name in explanation
    assert pet.name in explanation

def test_explain_plan_lists_scheduled_tasks(owner, pet, basic_tasks):
    scheduler = Scheduler(owner, pet, basic_tasks)
    plan = scheduler.build_plan()
    explanation = scheduler.explain_plan(plan)
    for st in plan.scheduled_tasks:
        assert st.task.title in explanation

def test_explain_plan_mentions_owner_preference_match(pet):
    owner = Owner("Jordan", available_minutes=60, preferences=["evening"])
    tasks = [CareTask("Evening groom", 20, "medium", preferred_time="evening")]
    scheduler = Scheduler(owner, pet, tasks)
    plan = scheduler.build_plan()
    explanation = scheduler.explain_plan(plan)
    assert "matches owner preference" in explanation
