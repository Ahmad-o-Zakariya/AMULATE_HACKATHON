from langgraph.graph import StateGraph, END
from .state import AgentState
from .tools import parse_intent, add_task, schedule_task_after_lunch


def intent_node(state: AgentState, user_input: str):
    intent = parse_intent(user_input)
    return {"intent_data": intent}


def planner_node(state: AgentState):
    return state


def executor_node(state: AgentState, intent_data: dict):
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


def response_node(state: AgentState):
    return state.last_action_summary


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("intent", intent_node)
    graph.add_node("plan", planner_node)
    graph.add_node("execute", executor_node)
    graph.add_node("respond", response_node)

    graph.set_entry_point("intent")
    graph.add_edge("intent", "plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", "respond")
    graph.add_edge("respond", END)

    return graph.compile()
