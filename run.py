from agent.graph import build_graph
from agent.state import AgentState

graph = build_graph()
state = AgentState()

print("AI Productivity Agent (type 'exit' to quit)")

while True:
    user_input = input("> ").strip()

    if user_input.lower() in {"exit", "quit", "bye", "q"}:
        print("See ya!")
        break

    # Normalize state if LangGraph returned dict
    if isinstance(state, dict):
        state = AgentState(**state)

    state.user_input = user_input
    state = graph.invoke(state)

    if isinstance(state, dict):
        state = AgentState(**state)

    print(state.last_action_summary)
