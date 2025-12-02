import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# -------------------------------
# In-memory store
# -------------------------------
tasks = []
next_id = 1


# Get all tasks
@app.get("/tasks")
def get_tasks():
    return jsonify(tasks)


# Add a new task
@app.post("/tasks")
def add_task():
    global next_id
    data = request.json

    if "title" not in data:
        return jsonify({"error": "Missing 'title' in request body"}), 400

    new_task = {
        "id": next_id,
        "title": data["title"],
        "completed": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


# Toggle completed
@app.put("/tasks/<int:id>")
def toggle_task(id):
    for task in tasks:
        if task["id"] == id:
            task["completed"] = not task["completed"]
            return jsonify(task)
    return jsonify({"message": f"Task with id {id} not found."}), 404


# Delete task
@app.delete("/tasks/<int:id>")
def delete_task(id):
    global tasks
    for task in tasks:
        if task["id"] == id:
            tasks = [t for t in tasks if t["id"] != id]
            return jsonify({"message": "Task deleted"})
    return jsonify({"message": f"Task with id {id} not found."}), 404


# Health check endpoint
@app.get("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    # Read port from environment variable, default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
