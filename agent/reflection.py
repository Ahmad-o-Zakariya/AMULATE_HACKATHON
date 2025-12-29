from .llm import get_llm

llm = get_llm(
    temperature=0.0,
    max_tokens=200,
)

REFLECTION_PROMPT = """
You are a self-reflection module for an AI productivity agent.

User intent:
{intent}

Actions taken:
{actions}

Outcome summary:
{summary}

Tasks scheduled: {scheduled_count}
Tasks unscheduled: {unscheduled_count}

Evaluate:
1. Did the agent fulfill the user intent?
2. If not, why?
3. Any constraint or limitation encountered?

Respond in JSON with:
{{
  "success": true | false,
  "explanation": string,
  "limitations": string | null
}}
"""

def reflect(intent: str, summary: str, scheduled: int, unscheduled: int):
    prompt = REFLECTION_PROMPT.format(
        intent=intent,
        actions="Scheduling and task planning",
        summary=summary,
        scheduled_count=scheduled,
        unscheduled_count=unscheduled,
    )

    response = llm.invoke(prompt)

    try:
        return eval(response.content)
    except Exception:
        return {
            "success": False,
            "explanation": "Reflection parsing failed.",
            "limitations": "Invalid reflection output."
        }