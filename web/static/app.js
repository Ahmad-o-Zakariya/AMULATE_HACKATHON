console.log("app.js loaded");

/* -----------------------------
   Agent Status Handling
------------------------------ */
function setStatus(state, text) {
  const status = document.getElementById("agent-status");
  if (!status) return;

  status.className = `agent-status ${state}`;
  status.textContent = text;
}

/* -----------------------------
   Chat Message Handling
------------------------------ */
function addMessage(role, text) {
  const box = document.getElementById("messages");
  if (!box) return;

  const div = document.createElement("div");
  div.className = role;
  div.textContent = text;

  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

/* -----------------------------
   Send Message to Agent
------------------------------ */
async function send() {
  const input = document.getElementById("input");
  const message = input.value.trim();
  if (!message) return;

  // UI: user message
  input.value = "";
  addMessage("user", message);

  // UI: reasoning state
  input.disabled = true;
  setStatus("thinking", "AI is reasoning…");

  try {
    const res = await fetch("/agent/step", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });

    const data = await res.json();

    // UI: agent reply
    addMessage("agent", data.reply || "Done.");

    /* -----------------------------
       Preferences
    ------------------------------ */
    const prefs = document.getElementById("prefs");
    if (prefs && data.preferences) {
      prefs.innerHTML = `
        <strong>Work:</strong> ${data.preferences.work_start_hour}:00 – ${data.preferences.work_end_hour}:00<br>
        <strong>Lunch:</strong> ${data.preferences.lunch_hour}:00
      `;
    }

    /* -----------------------------
       Tasks
    ------------------------------ */
    const taskList = document.getElementById("tasks");
    if (taskList && Array.isArray(data.tasks)) {
      taskList.innerHTML = "";
      data.tasks.forEach(t => {
        const li = document.createElement("li");
        li.innerText = `${t.title} • ${t.estimated_minutes} min • Priority ${t.priority}/5`;
        taskList.appendChild(li);
      });
    }

    /* -----------------------------
       Schedule
    ------------------------------ */
    const schedule = document.getElementById("schedule");
    if (schedule && Array.isArray(data.schedule)) {
      schedule.innerHTML = "";
      data.schedule.forEach(b => {
        const li = document.createElement("li");
        const start = new Date(b.start).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit"
        });
        const end = new Date(b.end).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit"
        });
        li.innerText = `${start} – ${end}  ${b.title}`;
        schedule.appendChild(li);
      });
    }

    /* -----------------------------
       Self-Reflection
    ------------------------------ */
    const reflectionBox = document.getElementById("reflection");
    if (reflectionBox && data.reflection) {
      reflectionBox.className =
        "reflection " + (data.reflection.success ? "success" : "failure");

      reflectionBox.innerHTML = `
        <strong>Status:</strong> ${
          data.reflection.success ? "Success" : "Partial / Failed"
        }<br>
        <strong>Explanation:</strong> ${data.reflection.explanation}
        ${
          data.reflection.limitations
            ? `<br><strong>Limitations:</strong> ${data.reflection.limitations}`
            : ""
        }
      `;
    }

    // UI: completed state
    setStatus("done", "AI completed the action");

  } catch (err) {
    console.error(err);
    addMessage("agent", "Something went wrong while reasoning.");
    setStatus("idle", "AI is idle");
  }

  // Restore input + idle state
  input.disabled = false;
  setTimeout(() => {
    setStatus("idle", "AI is idle");
  }, 2000);
}

/* -----------------------------
   Enter Key Support
------------------------------ */
document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("input");
  if (!input) return;

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });
});
