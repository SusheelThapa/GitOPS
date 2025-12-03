const API_URL = "/api/tasks";

// Fetch tasks from backend
async function loadTasks() {
    const response = await fetch(`${API_URL}/tasks`);
    const tasks = await response.json();

    const list = document.getElementById("taskList");
    list.innerHTML = "";

    tasks.forEach(task => {
        const li = document.createElement("li");
        li.className = task.completed ? "completed" : "";
        
        li.innerHTML = `
            <span onclick="toggleTask(${task.id})" style="cursor:pointer;">
                ${task.title}
            </span>
            <button class="deleteBtn" onclick="deleteTask(${task.id})">X</button>
        `;

        list.appendChild(li);
    });
}

// Add a new task
document.getElementById("addBtn").addEventListener("click", async () => {
    const input = document.getElementById("newTaskInput");
    const title = input.value.trim();
    if (!title) return;

    await fetch(`${API_URL}/tasks`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ title })
    });

    input.value = "";
    loadTasks();
});

// Toggle completed state
async function toggleTask(id) {
    await fetch(`${API_URL}/tasks/${id}`, {
        method: "PUT"
    });
    loadTasks();
}

// Delete a task
async function deleteTask(id) {
    await fetch(`${API_URL}/tasks/${id}`, {
        method: "DELETE"
    });
    loadTasks();
}

loadTasks(); // initial load
