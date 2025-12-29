from langgraph.graph import StateGraph, END
from .state import AgentState
from .tools import parse_intent, add_task, schedule_task_after_lunch
from .planner import plan_day


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
    intent_data = state.intent_data

    if intent_data["intent"] == "schedule_task":
        state = add_task(
            state,
            intent_data["title"],
            intent_data["priority"],
            intent_data["duration_minutes"],
        )
        state = schedule_task_after_lunch(state, state.tasks[-1])
        state.last_action_summary = "Task scheduled after lunch."

    return state


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
    graph.add_node("respond", response_node)

    graph.set_entry_point("intent")

    # Conditional routing based on intent
    graph.add_conditional_edges(
        "intent",
        route_by_intent,
        {
            "planner": "planner",
            "executor": "executor",
            "respond": "respond",
        },
    )

    graph.add_edge("planner", "respond")
    graph.add_edge("executor", "respond")
    graph.add_edge("respond", END)

    return graph.compile()
