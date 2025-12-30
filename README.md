# U-Dot AI – Personal Productivity Agent

U-Dot AI is an **agentic personal productivity assistant** that helps users plan their day and manage tasks using natural language.

Unlike a traditional chatbot, U-Dot AI combines:
- **LLM-based reasoning** (for intent understanding)
- **Deterministic planning logic** (for reliable scheduling)

This hybrid design ensures that the agent is **explainable, constraint-aware, and robust**, avoiding common LLM hallucination issues.

---

## Developed By

**Team Forcus** consists of **2 members**:

- **Ahmad Zakariya** — *Developer, Ideator, System Architecture & Design*
- **Shoraim Rashid** — *Research & Design (PPT)*

The team collaborated to balance deep technical implementation with research clarity and presentation, resulting in a robust and well-communicated system.

---

## Key Features

- Natural language task creation  
- Priority-based scheduling (1–5 scale, default = 3)  
- Time-aware constraints (e.g. *after lunch*)  
- User preference learning (work hours, lunch time)  
- Deterministic daily planner (no LLM for scheduling logic)  
- Self-reflection explaining what the agent did and why  
- Interactive web UI built with FastAPI + HTML/CSS/JS  

---

## How U-Dot AI Works

U-Dot AI follows an **agentic reasoning loop**:

1. **Intent Extraction (LLM)**  
   Gemini (via Vertex AI) extracts task intent, duration, and priority.

2. **Deterministic Execution (Code)**  
   Scheduling, constraints, and priorities are enforced using pure Python logic.

3. **Agent Flow (LangGraph)**  
   Intent → Plan → Execute → Reflect → Respond.

4. **Self-Reflection**  
   The agent evaluates whether it fulfilled the user’s intent and reports limitations if any.

This separation ensures reliability and explainability.

---

## Tech Stack

- **Language:** Python 3.10+  
- **Backend:** FastAPI  
- **Agent Framework:** LangGraph  
- **LLM:** Google Vertex AI (Gemini Flash)  
- **Frontend:** HTML, CSS, JavaScript  
- **State Management:** Pydantic models  

---

## Project Structure

```text
AMULATE_HACKATHON/
│
├── agent/                       # Core agent logic
│   ├── __init__.py
│   ├── graph.py                 # LangGraph agent flow
│   ├── llm.py                   # Gemini (Vertex AI) wrapper
│   ├── planner.py               # Deterministic scheduling logic
│   ├── planner_types.py         # TimeBlock, UnscheduledTask, PlanResult
│   ├── prompts.py               # LLM prompt templates
│   ├── reflection.py            # Self-reflection logic
│   ├── state.py                 # Agent state and data models
│   └── tools.py                 # Task creation and helpers
│
├── api/                         # FastAPI backend
│   ├── __init__.py
│   └── main.py                  # API server and agent endpoint
│
├── mcp_server/                  # MCP server (optional extension)
│   ├── __init__.py
│   └── server.py
│
├── scripts/                     # Testing utilities
│   └── test_planner.py
│
├── web/                         # Frontend
│   ├── index.html               # Main UI
│   └── static/
│       ├── app.js               # Frontend logic
│       └── style.css            # Styling
│
├── run.py                       # CLI-based runner
├── requirements.txt             # Dependencies
├── README.md                    # Documentation
├── LICENSE
└── .gitattributes
```
## How to Run the Project

### Prerequisites

- **Python 3.10 or higher**
- **Google Cloud account** with:
  - Billing enabled
  - Vertex AI API enabled
- **Google Cloud SDK** installed locally

Authenticate Google Cloud locally:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

U-Dot AI uses **Application Default Credentials**, so no API key is required.

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Start the Backend Server

**Recommended (with hot reload):**

```bash
uvicorn api.main:app --reload
```

**Alternative:**

```bash
python api/main.py
```

The server will start at:

```text
http://127.0.0.1:8000
```

---

### Open the Web App

Open your browser and navigate to:

```text
http://127.0.0.1:8000
```

---

## Example Commands to Try

```text
I work from 10 to 6 and lunch is at 2
```

```text
Add a 2 hour debugging session with medium priority
```

```text
Add a 2 hour meeting after lunch with high priority
```

```text
Plan my day
```

---

## Design Decisions

- The LLM is only used for **reasoning**, not scheduling  
- All time-based constraints (e.g. after lunch) are enforced **deterministically**  
- This prevents hallucinations and improves explainability  
- Agent state persists during a session for realistic interactions  

---

## Future Improvements

- Google Calendar API integration  
- Multi-day planning  
- User authentication and profiles  
- Advanced constraints (before lunch, fixed deadlines)  
- Agent observability using Arize Phoenix or Langfuse  

---

## About the Project

This project was built as part of the **BMW Hackathon (AMULATE)**  
to explore agentic AI systems and hybrid LLM + deterministic designs.

---

## License

This project is licensed under the terms specified in the `LICENSE` file.
