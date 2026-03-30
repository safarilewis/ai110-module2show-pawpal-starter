from pawpal_system import CareTask, Pet, Owner, Scheduler

# --- Setup ---
owner = Owner("Jordan", available_minutes=90, preferences=["morning"])
pet = Pet("Mochi", "dog", 3)

# --- Tasks (added out of priority order intentionally) ---
tasks = [
    CareTask("Evening walk",    30, "medium", task_type="exercise",  preferred_time="evening"),
    CareTask("Medication",       5, "high",   task_type="health",    required=True, frequency="daily"),
    CareTask("Morning feeding", 10, "high",   task_type="feeding",   preferred_time="morning", frequency="daily"),
    CareTask("Grooming",        20, "low",    task_type="grooming",  preferred_time="evening"),
    CareTask("Playtime",        15, "medium", task_type="enrichment",preferred_time="afternoon"),
    CareTask("Training",        25, "medium", task_type="enrichment",preferred_time="morning"),
]

# --- Build schedule ---
scheduler = Scheduler(owner, pet, tasks)
plan = scheduler.build_plan()

# --- Print today's schedule ---
print("=" * 50)
print("  PawPal+ — Today's Schedule")
print("=" * 50)
print(plan.summary())

# --- Explain reasoning ---
print("\n" + "=" * 50)
print("  Why this plan?")
print("=" * 50)
print(scheduler.explain_plan(plan))

# --- Conflict check ---
conflicts = scheduler.detect_conflicts(plan)
print("\n" + "=" * 50)
if conflicts:
    print("  ⚠️  Conflicts detected:")
    for c in conflicts:
        print(f"  {c}")
else:
    print("  No conflicts detected.")
print("=" * 50)

# --- Demonstrate recurring task completion ---
print("\n--- Recurring task demo ---")
med = tasks[1]
print(f"Before: {med.title} | completed={med.completed} | next_due={med.next_due}")
med.mark_complete()
print(f"After:  {med.title} | completed={med.completed} | next_due={med.next_due}")
