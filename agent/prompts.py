INTENT_EXTRACTION_PROMPT = """
You are an intent extraction engine for a productivity agent.

User input:
"{input}"

Extract intent as JSON with this exact schema:
{
  "intent": "schedule_task | add_task | summarize | unknown",
  "title": string | null,
  "duration_minutes": number | null,
  "time_constraint": string | null,
  "priority": number | null
}

Rules:
- If duration is given in hours, convert to minutes.
- If timing is vague (e.g. "after lunch"), keep it in time_constraint.
- Output ONLY valid JSON. No commentary.
"""
