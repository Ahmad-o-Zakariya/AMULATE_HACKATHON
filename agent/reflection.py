from .llm import get_llm

llm = get_llm(
    temperature=0.0,
    max_tokens=128,
)

def reflect(state):
    if not state.last_action_summary:
        return "No action was taken. Clarification needed."
    return state.last_action_summary
