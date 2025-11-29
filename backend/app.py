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
    
    # FIX: Use IF NOT EXISTS for the sequence to prevent race conditions 
    # when multiple containers start up simultaneously.
    # Step 1: Create sequence if not exists (Atomic operation)
    cur.execute("CREATE SEQUENCE IF NOT EXISTS tasks_id_seq;")
    
    # Step 2: Create table if not exists and use the sequence
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY DEFAULT nextval('tasks_id_seq'),
        title VARCHAR(255) NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Step 3: Ensure the sequence ownership is set correctly (Good practice)
    # The DEFAULT nextval() already links it, but ownership is safer.
    cur.execute("ALTER SEQUENCE tasks_id_seq OWNED BY tasks.id;")
    
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
    # Added error handling for missing 'title'
    if 'title' not in data:
        return jsonify({"error": "Missing 'title' in request body"}), 400
        
    title = data["title"]
    # print(title) # Removed print statement for production readiness
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) # Use DictCursor to return a dictionary
    
    # Note: RETURNING * is simpler than listing all columns manually
    cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING *", (title,))
    new_task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    # Return the result as a standard dictionary from DictCursor
    return jsonify(dict(new_task)), 201

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
    
    if updated is None:
        return jsonify({"message": f"Task with id {id} not found."}), 404

    return jsonify(dict(updated))

# Delete task
@app.delete("/tasks/<int:id>")
def delete_task(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (id,))
    rows_deleted = cur.rowcount # Check how many rows were affected
    conn.commit()
    cur.close()
    conn.close()
    
    if rows_deleted == 0:
        return jsonify({"message": f"Task with id {id} not found."}), 404
        
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