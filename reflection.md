# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML focused on four main classes: `CareTask`, `Pet`, `Owner`, and `Scheduler`. I wanted each class to have one clear responsibility so the system would stay simple and readable.

- `CareTask` stores the information for one pet care activity, including title, duration, priority, whether it is required, and a preferred time block.
- `Pet` stores basic information about the pet, such as name, species, and age.
- `Owner` stores the owner's name, available minutes for the day, and simple preferences that can influence scheduling.
- `Scheduler` acts as the decision-making layer. It looks at all tasks, prioritizes them, builds a daily plan, and explains why tasks were chosen.

As the project grew, I also added `ScheduledTask` and `DailyPlan` to represent the output of the scheduler more clearly.

**b. Design changes**

My design changed during implementation. One major change was introducing `DailyPlan` and `ScheduledTask` as separate classes. At first, I thought the scheduler could just return a list of tasks, but that made it harder to track start times, end times, and total minutes in a clean way.

I also expanded `CareTask` to include `frequency`, `completed`, and `next_due` so I could support recurring daily and weekly tasks. Another change was adding owner time-block preferences so the scheduler could consider more than just raw priority.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers several constraints:

- available time for the owner
- whether a task is required
- task priority (`high`, `medium`, `low`)
- owner preference for a time block
- task preferred time block
- recurring frequency for task completion logic

I decided that required tasks mattered most because missing medication or feeding is more serious than skipping an optional activity. After that, I prioritized owner-preference matches and then task priority. I kept the rules simple on purpose so the project would stay understandable and easy to test.

**b. Tradeoffs**

One tradeoff my scheduler makes is using simple time blocks like morning, afternoon, and evening instead of a full calendar system. It also schedules tasks in priority order and skips anything that no longer fits.

That tradeoff is reasonable for this scenario because the app is meant to be a lightweight pet care planner, not a full scheduling platform. The simplified approach is easier to explain and test, while still being useful for helping a busy pet owner decide what to do today.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI for design brainstorming, reviewing my UML, improving test coverage, and polishing parts of the implementation. It was especially helpful when I wanted to quickly compare design options or think through how classes should interact.

The most helpful prompts were specific prompts tied to my actual files, such as:

- asking whether my UML was missing important relationships
- asking how the scheduler should retrieve and organize task data
- asking what edge cases were most important to test
- asking how to simplify a feature without making the system too complex

**b. Judgment and verification**

One moment where I did not accept an AI suggestion as-is was around using exact clock times for every task and building a more detailed scheduling model. That would have made the system more realistic, but it also would have added a lot of complexity that was unnecessary at the moment.

I chose to keep preferred times as broad blocks like morning, afternoon, and evening. I verified that choice by checking it against requirements, then making sure the logic still worked through automated tests and trying the implementation myself.

---

## 4. Testing and Verification

**a. What you tested**

I tested the behaviors that seemed most important to the scheduler working correctly:

- task defaults and string representation
- task completion and recurring rescheduling
- scheduled task end-time calculation
- total scheduled minutes and plan summary output
- required task ordering
- priority ordering
- owner preference matching
- tasks staying within available time
- preferred time slot placement
- conflict detection
- explanation text output

These tests were important because they cover both the "happy path" and the most likely logic mistakes. Since scheduling logic can fail silently, I wanted tests that confirmed the system was actually making the decisions I expected.

**b. Confidence**

I am fairly confident that the scheduler works correctly for the current scope. I would rate it at about 4 out of 5 because the major behaviors are covered by both live testing and automated tests.

If I had more time, I would test edge cases like:

- tasks that span midnight
- invalid or unexpected priority values
- empty owner preference lists in more scenarios
- multiple overlapping conflicts in one plan
- recurring tasks across many days instead of a single completion step

---

## 5. Reflection

**a. What went well**

The part I am most satisfied with is how the backend logic, tests, and UI now connect together. The project feels like a complete small system instead of just a few unrelated files. I also like that the explanation output makes the scheduler's decisions easier to understand.

**b. What you would improve**

If I had another iteration, I would redesign the model to support multiple pets per owner more explicitly and add richer scheduling features like exact due times, better recurrence handling, and more advanced conflict resolution. I would also improve the UI so recurring tasks and filters are easier to explore directly from the app.

**c. Key takeaway**

One important thing I learned is that AI is most useful when I treat it like a strong collaborator instead of a final authority. The best results came from using AI to generate ideas, test plans, and drafts, then making my own decisions about what actually fit the project requirements and level of complexity instead of having it over-engineer everything at once.
