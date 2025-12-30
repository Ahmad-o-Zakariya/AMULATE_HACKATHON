from .llm import get_llm
import json

llm = get_llm(
    temperature=0.0,
    max_tokens=200,
)

REFLECTION_PROMPT = """
You are a self-reflection module for an AI productivity agent.

User intent:
{intent}

Outcome summary:
{summary}

Tasks scheduled: {scheduled_count}
Tasks unscheduled: {unscheduled_count}

Evaluate:
1. Did the agent fulfill the user intent?
2. If not, why?
3. Any constraint or limitation encountered?

IMPORTANT:
- Output MUST be valid JSON
- Output MUST start with {{ and end with }}
- Do NOT include any text before or after the JSON

Return JSON in this exact format:
{{
  "success": true | false,
  "explanation": string,
  "limitations": string | null
}}
"""


def reflect(intent: str, summary: str, scheduled: int, unscheduled: int):

    if scheduled == 0 and unscheduled == 0:
        return {
            "success": False,
            "explanation": "No tasks were available to schedule for the day.",
            "limitations": None
        }
    if unscheduled == 0 and scheduled > 0:
        return {
            "success": True,
            "explanation": "All tasks were successfully scheduled within available work hours.",
            "limitations": None
        }

    prompt = REFLECTION_PROMPT.format(
        intent=intent,
        summary=summary,
        scheduled_count=scheduled,
        unscheduled_count=unscheduled,
    )

    response = llm.invoke(prompt)
    raw = response.content.strip()

    # Defensive JSON extraction
    start = raw.find("{")
    end = raw.rfind("}")

    if start != -1 and end != -1:
        raw_json = raw[start:end + 1]
        try:
            return json.loads(raw_json)
        except Exception:
            pass

    return {
    "success": False,
    "explanation": "The agent completed the task but could not reliably self-evaluate.",
    "limitations": "Reflection model returned malformed JSON."
    }

