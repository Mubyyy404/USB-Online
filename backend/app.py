from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "usb_sentinel_secret"
CORS(app, supports_credentials=True)

DB = "sentinel.db"

def get_db():
    return sqlite3.connect(DB)

# ---------- INIT DB ----------
conn = get_db()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS usb_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    device TEXT,
    serial TEXT,
    action TEXT,
    time TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS sandbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    file TEXT,
    hash TEXT,
    result TEXT,
    time TEXT
)
""")

conn.commit()
conn.close()

# ---------- AUTH ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (
            data["email"],
            generate_password_hash(data["password"])
        ))
        conn.commit()
        return jsonify({"status": "registered"})
    except:
        return jsonify({"error": "User exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email=?", (data["email"],))
    user = c.fetchone()

    if user and check_password_hash(user[0], data["password"]):
        session["user"] = data["email"]
        return jsonify({"status": "success"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"status": "logged_out"})

# ---------- USB LOG ----------
@app.route("/log_usb", methods=["POST"])
def log_usb():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO usb_logs VALUES (NULL, ?, ?, ?, ?, ?)", (
        data["user"],
        data["device"],
        data["serial"],
        data["action"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    return jsonify({"status": "logged"})

# ---------- SANDBOX ----------
@app.route("/sandbox", methods=["POST"])
def sandbox():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO sandbox VALUES (NULL, ?, ?, ?, ?, ?)", (
        data["user"],
        data["file"],
        data["hash"],
        data["result"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    return jsonify({"status": "sandboxed"})

# ---------- DASHBOARD DATA ----------
@app.route("/dashboard")
def dashboard():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT user, device, serial, action, time FROM usb_logs ORDER BY id DESC LIMIT 50")
    usb = c.fetchall()

    c.execute("SELECT user, file, result, time FROM sandbox ORDER BY id DESC LIMIT 10")
    sandbox = c.fetchall()

    return jsonify({
        "usb_logs": usb,
        "sandbox": sandbox
    })

if __name__ == "__main__":
    app.run(debug=True)
