from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from agent.graph import build_graph
from agent.state import AgentState
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict

app = FastAPI(title="AI Personal Productivity Agent")

# Build agent once
graph = build_graph()
state = AgentState()


class AgentInput(BaseModel):
    message: str


class AgentOutput(BaseModel):
    reply: str
    tasks: list
    preferences: dict
    schedule: list | None
    reflection: Optional[Dict] = None   # 🔹 ADD THIS


@app.post("/agent/step", response_model=AgentOutput)
def agent_step(input: AgentInput):
    global state

    # Normalize state
    if isinstance(state, dict):
        state = AgentState(**state)

    state.user_input = input.message
    state = graph.invoke(state)

    if isinstance(state, dict):
        state = AgentState(**state)

    return AgentOutput(
        reply=state.last_action_summary,
        tasks=[t.dict() for t in state.tasks],
        preferences=state.user_preferences.dict(),
        schedule=[
            {
                "title": b.title,
                "start": b.start.isoformat(),
                "end": b.end.isoformat(),
            }
            for b in (state.planned_schedule or [])
        ],
        reflection=state.reflection,   # 🔹 ADD THIS
    )


# Serve frontend
app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/")
def root():
    return FileResponse("web/index.html")
