from langgraph.graph import StateGraph, END
from .state import AgentState, Task
from .tools import parse_intent, add_task, schedule_task_after_lunch
from .planner import plan_day
from .tools import parse_intent, add_task, schedule_task_after_lunch, update_preferences
from uuid import uuid4


# -------------------------
# Intent parsing node
# -------------------------

def intent_node(state: AgentState):
    print("INTENT NODE CALLED WITH:", state.user_input)
    intent_data = parse_intent(state.user_input)

    # Store intent in state for routing
    state.intent = intent_data["intent"]
    state.intent_data = intent_data

    return state


# -------------------------
# Router (THIS IS KEY)
# -------------------------

def route_by_intent(state: AgentState) -> str:
    if state.intent == "plan_day":
        return "planner"
    elif state.intent == "schedule_task":
        return "executor"
    else:
        return "respond"


# -------------------------
# Planner node
# -------------------------

def planner_node(state: AgentState):
    result = plan_day(state)

    state.planned_schedule = result.schedule
    state.unscheduled_tasks = result.unscheduled
    state.last_action_summary = result.summary

    return state


# -------------------------
# Executor node (task ops)
# -------------------------

def executor_node(state: AgentState):
    data = state.intent_data

    task = Task(
        id=str(uuid4()),
        title=data.get("title", "Untitled task"),
        priority=data.get("priority", 3),
        estimated_minutes=data.get("duration_minutes", 60),
        status="pending",
    )

    state.tasks.append(task)

    state.last_action_summary = f"Task added: {task.title}"
    return state

# -------------------------
# Preference node
# -------------------------

def update_preferences_node(state: AgentState):
    return update_preferences(state, state.intent_data)

# -------------------------
# Response node
# -------------------------

def response_node(state: AgentState):
    return state


# -------------------------
# Graph builder
# -------------------------

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("intent", intent_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("update_preferences", update_preferences_node)
    graph.add_node("respond", response_node)

    graph.set_entry_point("intent")

    def route_by_intent(state: AgentState):
        if state.intent == "update_preferences":
            return "update_preferences"
        if state.intent == "plan_day":
            return "planner"
        if state.intent == "schedule_task":
            return "executor"
        return "respond"

    graph.add_conditional_edges(
        "intent",
        route_by_intent,
        {
            "update_preferences": "update_preferences",
            "planner": "planner",
            "executor": "executor",
            "respond": "respond",
        },
    )

    graph.add_edge("planner", "respond")
    graph.add_edge("executor", "respond")
    graph.add_edge("update_preferences", "respond")
    graph.add_edge("respond", END)

    return graph.compile()

