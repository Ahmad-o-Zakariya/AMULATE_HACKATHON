import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))


from agent.state import AgentState, Task, UserPreferences
from agent.planner import plan_day

state = AgentState(
    user_preferences=UserPreferences(
        work_start_hour=9,
        work_end_hour=18,
        lunch_hour=13,
        focus_hours=[9, 10, 11]
    ),
    tasks=[
        Task(id="1", title="Code feature", priority=5, estimated_minutes=120, status="pending"),
        Task(id="2", title="Read ML paper", priority=3, estimated_minutes=90, status="pending"),
        Task(id="3", title="Emails", priority=1, estimated_minutes=30, status="pending"),
    ]
)

result = plan_day(state)

print(result.summary)
for block in result.schedule:
    print(block.start.time(), "-", block.end.time(), block.title)

for u in result.unscheduled:
    print("Unscheduled:", u.title, "-", u.reason)
