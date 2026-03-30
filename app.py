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
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Pet age", min_value=0, max_value=30, value=3)

st.divider()

# --- Task Entry ---
st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    preferred_time = st.selectbox("Preferred time", ["none", "morning", "afternoon", "evening"])
with col5:
    required = st.checkbox("Required")

if st.button("Add task"):
    st.session_state.tasks.append(
        CareTask(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            required=required,
            preferred_time=preferred_time if preferred_time != "none" else None,
        )
    )

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
    if st.button("Clear all tasks"):
        st.session_state.tasks = []
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
        owner = Owner(owner_name, available_minutes)
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
