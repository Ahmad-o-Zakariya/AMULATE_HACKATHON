from agent.graph import build_graph
from agent.state import AgentState

graph = build_graph()
state = AgentState()

while True:
    user_input = input("> ")
    state = graph.invoke(state, {"user_input": user_input})
    print(state.last_action_summary)
