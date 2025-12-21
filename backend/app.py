from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "usb_sentinel_secret"
CORS(app, supports_credentials=True)

DB = "sentinel.db"

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
CREATE TABLE IF NOT EXISTS usb_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event TEXT,
    device TEXT,
    time TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS sandbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    file_name TEXT,
    hash TEXT,
    result TEXT,
    time TEXT
)
""")

conn.commit()
conn.close()

# ---------- REGISTER ----------
@app.route("/register", methods=["POST"])
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
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = db()
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username=?", (data["username"],))
    user = c.fetchone()

    if user and check_password_hash(user[1], data["password"]):
        session["user_id"] = user[0]
        return jsonify({"status": "success"})
    return jsonify({"error": "Invalid"}), 401

# ---------- USB LOG (AGENT CALL) ----------
@app.route("/log_usb", methods=["POST"])
def log_usb():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    data = request.json
    conn = db()
    c = conn.cursor()
    c.execute("INSERT INTO usb_logs VALUES (NULL, ?, ?, ?, ?)", (
        session["user_id"],
        data["event"],
        data["device"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    return jsonify({"status": "logged"})

# ---------- SANDBOX (SIMULATED) ----------
@app.route("/sandbox", methods=["POST"])
def sandbox():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    data = request.json
    conn = db()
    c = conn.cursor()
    c.execute("INSERT INTO sandbox VALUES (NULL, ?, ?, ?, ?, ?)", (
        session["user_id"],
        data["file"],
        data["hash"],
        data["result"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    return jsonify({"status": "sandboxed"})

# ---------- DASHBOARD DATA ----------
@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = db()
    c = conn.cursor()

    c.execute("SELECT event, device, time FROM usb_logs WHERE user_id=?", (session["user_id"],))
    usb = c.fetchall()

    c.execute("SELECT file_name, result, time FROM sandbox WHERE user_id=?", (session["user_id"],))
    sandbox = c.fetchall()

    return jsonify({"usb": usb, "sandbox": sandbox})

if __name__ == "__main__":
    app.run(debug=True)
