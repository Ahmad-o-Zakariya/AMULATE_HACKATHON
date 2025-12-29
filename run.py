from agent.graph import build_graph
from agent.state import AgentState

graph = build_graph()
state = AgentState()

while True:
    user_input = input("> ")

    # Normalize state if LangGraph returned a dict
    if isinstance(state, dict):
        state = AgentState(**state)

    state.user_input = user_input
    state = graph.invoke(state)

    # Normalize again after invoke
    if isinstance(state, dict):
        state = AgentState(**state)

    print(state.last_action_summary)
