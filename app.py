import streamlit as st
from pawpal_system import CareTask, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Owner & Pet Info ---
st.subheader("Owner & Pet Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Available time (minutes)", min_value=10, max_value=480, value=60)
    owner_preferred_time = st.selectbox(
        "Owner preferred time block",
        ["none", "morning", "afternoon", "evening"],
        help="Tasks matching this time block get a small scheduling boost.",
    )
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Pet age", min_value=0, max_value=30, value=3)

st.divider()

# --- Task Entry ---
st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "edit_task_index" not in st.session_state:
    st.session_state.edit_task_index = None

editing_task = None
if st.session_state.edit_task_index is not None and 0 <= st.session_state.edit_task_index < len(st.session_state.tasks):
    editing_task = st.session_state.tasks[st.session_state.edit_task_index]

priority_options = ["low", "medium", "high"]
time_options = ["none", "morning", "afternoon", "evening"]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input(
        "Title",
        value=editing_task.title if editing_task else "Morning walk",
    )
with col2:
    duration = st.number_input(
        "Duration (min)",
        min_value=1,
        max_value=240,
        value=editing_task.duration_minutes if editing_task else 20,
    )
with col3:
    priority = st.selectbox(
        "Priority",
        priority_options,
        index=priority_options.index(editing_task.priority) if editing_task else 2,
    )
with col4:
    preferred_time = st.selectbox(
        "Preferred time",
        time_options,
        index=time_options.index(editing_task.preferred_time or "none") if editing_task else 0,
    )
with col5:
    required = st.checkbox("Required", value=editing_task.required if editing_task else False)

action_col1, action_col2 = st.columns(2)
with action_col1:
    save_label = "Save task changes" if editing_task else "Add task"
    if st.button(save_label):
        task = CareTask(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            required=required,
            preferred_time=preferred_time if preferred_time != "none" else None,
        )
        if editing_task:
            st.session_state.tasks[st.session_state.edit_task_index] = task
            st.session_state.edit_task_index = None
        else:
            st.session_state.tasks.append(task)
        st.rerun()

with action_col2:
    if editing_task and st.button("Cancel edit"):
        st.session_state.edit_task_index = None
        st.rerun()

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table([
        {
            "Title": t.title,
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority,
            "Preferred time": t.preferred_time or "any",
            "Required": t.required,
        }
        for t in st.session_state.tasks
    ])
    selected_task_index = st.selectbox(
        "Select a task to edit or remove",
        options=list(range(len(st.session_state.tasks))),
        format_func=lambda i: f"{i + 1}. {st.session_state.tasks[i].title}",
    )
    manage_col1, manage_col2 = st.columns(2)
    with manage_col1:
        if st.button("Edit selected task"):
            st.session_state.edit_task_index = selected_task_index
            st.rerun()
    with manage_col2:
        if st.button("Remove selected task"):
            st.session_state.tasks.pop(selected_task_index)
            if st.session_state.edit_task_index == selected_task_index:
                st.session_state.edit_task_index = None
            elif st.session_state.edit_task_index is not None and st.session_state.edit_task_index > selected_task_index:
                st.session_state.edit_task_index -= 1
            st.rerun()

    if st.button("Clear all tasks"):
        st.session_state.tasks = []
        st.session_state.edit_task_index = None
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task first.")
    else:
        preferences = [] if owner_preferred_time == "none" else [owner_preferred_time]
        owner = Owner(owner_name, available_minutes, preferences=preferences)
        pet = Pet(pet_name, species, age)
        scheduler = Scheduler(owner, pet, st.session_state.tasks)
        plan = scheduler.build_plan()

        st.success(f"Scheduled {len(plan.scheduled_tasks)} of {len(st.session_state.tasks)} tasks ({plan.total_minutes} min)")

        st.markdown("### Daily Plan")
        for st_task in plan.scheduled_tasks:
            start = st_task.start_time.strftime("%I:%M %p")
            end = st_task.end_time.strftime("%I:%M %p")
            with st.container(border=True):
                st.markdown(f"**{start} – {end}  {st_task.task.title}**  `{st_task.task.priority}`")
                st.caption(f"Reason: {st_task.reason}")

        st.markdown("### Explanation")
        st.text(scheduler.explain_plan(plan))
