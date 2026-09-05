import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_FILE = "free_users.json"
PENDING_FILE = "pending_payments.json"

def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@app.route('/admin/toggle-ban', methods=['POST'])
def toggle_ban():
    data = request.get_json(force=True, silent=True) or {}
    user_target = data.get("user")
    if not user_target:
        return jsonify({"status": "error", "message": "Chybí user"}), 400

    users = load_data(DB_FILE, {})
    if user_target in users:
        curr = users[user_target].get("banned", False)
        users[user_target]["banned"] = not curr
        save_data(DB_FILE, users)
        return jsonify({"status": "success", "banned": not curr}), 200
    else:
        # Pokud je uživatel zatím jen na VIP, založíme mu záznam i sem jako zabanovaný
        users[user_target] = {"banned": True, "password": "sync", "email": "", "phone": ""}
        save_data(DB_FILE, users)
        return jsonify({"status": "success", "banned": True}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True, silent=True) or {}
    login_id = str(data.get("login_id", "")).strip().lower()
    password = data.get("password", "")

    users = load_data(DB_FILE, {})
    for u_name, u_info in users.items():
        if login_id in [u_name.lower(), str(u_info.get("email", "")).lower(), str(u_info.get("phone", ""))]:
            if u_info.get("banned", False):
                return jsonify({"status": "banned", "message": "BANNED"}), 403
            if u_info.get("password") == password:
                return jsonify({"status": "success", "username": u_name, "is_admin": u_info.get("is_admin", False)}), 200
            return jsonify({"status": "error", "message": "Špatné heslo"}), 401

    return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404

@app.route('/activate-pm', methods=['POST'])
def activate_pm():
    data = request.get_json(force=True, silent=True) or {}
    user = data.get("user")
    code = data.get("code")
    pending = load_data(PENDING_FILE, [])
    pending.append({"user": user, "code": code})
    save_data(PENDING_FILE, pending)
    return jsonify({"status": "success"}), 200

@app.route('/admin/pending', methods=['POST'])
def get_pending():
    return jsonify({"status": "success", "pending": load_data(PENDING_FILE, [])}), 200

@app.route('/admin/remove-pending', methods=['POST'])
def remove_pending():
    data = request.get_json(force=True, silent=True) or {}
    user = data.get("user")
    pending = load_data(PENDING_FILE, [])
    pending = [p for p in pending if p.get("user") != user]
    save_data(PENDING_FILE, pending)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
