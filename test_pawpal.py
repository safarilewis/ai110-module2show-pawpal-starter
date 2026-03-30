import pytest
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


# --- ScheduledTask ---

def test_scheduled_task_end_time():
    from datetime import datetime
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


# --- Scheduler.build_plan ---

def test_tasks_fit_within_available_time(owner, pet, basic_tasks):
    scheduler = Scheduler(owner, pet, basic_tasks)
    plan = scheduler.build_plan()
    assert plan.total_minutes <= owner.available_minutes

def test_task_exceeding_time_is_skipped(owner, pet):
    tasks = [CareTask("Long hike", 120, "high")]
    scheduler = Scheduler(owner, pet, tasks)  # owner has 60 min
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
    from datetime import datetime
    tasks = [CareTask("Evening groom", 20, "medium", preferred_time="evening")]
    scheduler = Scheduler(owner, pet, tasks)
    plan = scheduler.build_plan()
    assert len(plan.scheduled_tasks) == 1
    assert plan.scheduled_tasks[0].start_time.hour == 18


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
