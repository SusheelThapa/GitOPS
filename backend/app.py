from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_connection
import psycopg2.extras

app = Flask(__name__)
CORS(app)

# -------------------------------
# Auto-create tasks table on startup
# -------------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()  # Call on startup
# -------------------------------

# Get all tasks
@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(t) for t in tasks])

# Add a new task
@app.post("/tasks")
def add_task():
    data = request.json
    title = data["title"]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, completed, created_at", (title,))
    new_task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "id": new_task[0],
        "title": new_task[1],
        "completed": new_task[2],
        "created_at": new_task[3]
    })

# Toggle completed
@app.put("/tasks/<int:id>")
def toggle_task(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        UPDATE tasks 
        SET completed = NOT completed 
        WHERE id = %s RETURNING *
    """, (id,))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(dict(updated))

# Delete task
@app.delete("/tasks/<int:id>")
def delete_task(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Task deleted"})

# Health check endpoint
@app.get("/health")
def health_check():
    """
    Simple health check for Docker/Nginx or monitoring.
    Returns 200 OK if the backend is up and DB connection works.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")  # simple query to check DB
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
