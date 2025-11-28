const API_URL = "/api/tasks";

async function loadTasks() {
  const res = await fetch(API_URL);
  const tasks = await res.json();

  const list = document.getElementById("taskList");
  list.innerHTML = "";

  tasks.forEach((task) => {
    const li = document.createElement("li");

    li.innerHTML = `
            <span class="task-text ${task.completed ? "completed" : ""}">
                ${task.title}
            </span>

            <div class="task-btns">
                <button class="done-btn" onclick="toggleTask(${
                  task.id
                })">✔</button>
                <button class="delete-btn" onclick="deleteTask(${
                  task.id
                })">🗑</button>
            </div>
        `;

    list.appendChild(li);
  });
}

async function addTask() {
  const input = document.getElementById("taskInput");
  const title = input.value.trim();

  if (!title) {
    alert("Task cannot be empty!");
    return;
  }

  await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });

  input.value = "";
  loadTasks();
}

async function toggleTask(id) {
  await fetch(`${API_URL}/${id}`, { method: "PUT" });
  loadTasks();
}

async function deleteTask(id) {
  await fetch(`${API_URL}/${id}`, { method: "DELETE" });
  loadTasks();
}

loadTasks();
