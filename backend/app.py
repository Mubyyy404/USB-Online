from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB = "users.db"

def db():
    return sqlite3.connect(DB)

# ---------- INIT DATABASE ----------
conn = db()
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT,
    data TEXT,
    time TEXT
)
""")
conn.commit()
conn.close()

# ---------- REGISTER ----------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    try:
        conn = db()
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (
            data["username"],
            generate_password_hash(data["password"])
        ))
        conn.commit()
        return jsonify({"status": "registered"})
    except:
        return jsonify({"error": "User exists"}), 400

# ---------- LOGIN ----------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    conn = db()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (data["username"],))
    user = c.fetchone()
    if user and check_password_hash(user[0], data["password"]):
        return jsonify({"status": "success"})
    return jsonify({"error": "Invalid credentials"}), 401

# ---------- RECEIVE USB EVENTS ----------
@app.route("/api/report", methods=["POST"])
def report():
    data = request.json
    conn = db()
    c = conn.cursor()
    c.execute("INSERT INTO events VALUES (NULL, ?, ?, ?)", (
        data["event"],
        str(data["data"]),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    return jsonify({"status": "received"})

# ---------- DASHBOARD DATA ----------
@app.route("/api/events", methods=["GET"])
def events():
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY id DESC")
    rows = c.fetchall()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)
