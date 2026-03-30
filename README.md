# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan daily care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

The project combines object-oriented design, scheduling logic, testing, and a simple interactive UI.

## Features

- Enter owner and pet information
- Add, edit, remove, and clear pet care tasks
- Generate a daily care plan based on available time, priority, and owner preferences
- Show start and end times for scheduled tasks
- Explain why each task was chosen
- Detect and display schedule conflicts
- Support recurring daily and weekly tasks in the backend logic
- Run an automated pytest suite for core scheduler behavior

## Running PawPal+

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Streamlit App

```bash
streamlit run app.py
```

### CLI Demo

```bash
python main.py
```

The CLI demo creates sample tasks, prints a formatted schedule, explains why tasks were chosen, checks for conflicts, and demonstrates recurring task completion.

## Smarter Scheduling

PawPal+ uses several algorithms to produce an intelligent daily plan:

- **Priority-based sorting** — Tasks are ranked by `required` flag first, then by owner time-block preference match, then by priority level (high → medium → low).
- **Greedy time fitting** — Tasks are placed into the schedule in priority order; any task that exceeds remaining available time is skipped.
- **Time-slot awareness** — Each task has an optional `preferred_time` (morning / afternoon / evening). Tasks are placed at the start of their preferred slot and slots advance as tasks fill up, preventing overlaps within the same block.
- **Owner preference boost** — If a task's preferred time matches the owner's stated preference, it gets a scheduling boost and a note in the explanation.
- **Recurring tasks** — Tasks can be marked `frequency="daily"` or `"weekly"`. Calling `mark_complete()` automatically advances `next_due` by the correct interval and resets the completion flag.
- **Conflict detection** — `Scheduler.detect_conflicts(plan)` scans the plan for any two tasks whose time windows overlap and returns human-readable warning messages.

## Demo

Add your final Streamlit screenshot here before submission:

```html
<a href="/course_images/ai110/your_screenshot_name.png" target="_blank"><img src='/course_images/ai110/your_screenshot_name.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>
```

## Testing PawPal+

```bash
python -m pytest tests/test_pawpal.py -v
```

The test suite covers:

- Task defaults and string representation
- Recurring task completion and rescheduling (daily + weekly)
- `ScheduledTask.end_time` calculation
- `DailyPlan` total minutes and summary output
- Priority and required-task ordering
- Owner preference boost in prioritization
- Time-slot placement and available-time constraints
- Conflict detection (overlapping and non-overlapping cases)
- Plan explanation output

**Confidence level: ★★★★☆** — Core scheduling behaviors are well covered. Edge cases like tasks spanning midnight or zero-duration tasks are not yet tested.
