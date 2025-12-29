from mcp import Server
from agent.graph import build_graph
from agent.state import AgentState

server = Server()
graph = build_graph()
state = AgentState()

@server.tool()
def run_agent(input: str) -> str:
    global state
    result = graph.invoke(state, {"user_input": input})
    state = result
    return result.last_action_summary

if __name__ == "__main__":
    server.run()
