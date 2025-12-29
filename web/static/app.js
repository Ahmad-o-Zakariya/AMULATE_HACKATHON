console.log("app.js loaded");

function addMessage(role, text) {
  const box = document.getElementById("messages");

  const div = document.createElement("div");
  div.className = role;
  div.textContent = text;

  box.append(div);
}


async function send() {
  const input = document.getElementById("input");
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  addMessage("user", message);

  const res = await fetch("/agent/step", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });

  const data = await res.json();

  addMessage("agent", data.reply);

  // Preferences
  document.getElementById("prefs").innerHTML = `
    Work hours: ${data.preferences.work_start_hour} – ${data.preferences.work_end_hour}<br>
    Lunch: ${data.preferences.lunch_hour}:00
  `;

  // Tasks
  const taskList = document.getElementById("tasks");
  taskList.innerHTML = "";
  data.tasks.forEach(t => {
    const li = document.createElement("li");
    li.innerText = `${t.title} (${t.estimated_minutes} min, priority ${t.priority})`;
    taskList.appendChild(li);
  });

  // Schedule
  const schedule = document.getElementById("schedule");
  schedule.innerHTML = "";
  (data.schedule || []).forEach(b => {
    const li = document.createElement("li");
    const start = new Date(b.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const end = new Date(b.end).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    li.innerText = `${start} – ${end}  ${b.title}`;
    schedule.appendChild(li);
  });
}
