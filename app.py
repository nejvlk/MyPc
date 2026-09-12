import os
import json
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
DB_FILE = "free_users.json"

def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception: pass
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "").strip()
    users = load_data(DB_FILE, {})
    if username.lower() in [u.lower() for u in users.keys()]:
        return jsonify({"status": "error", "message": "Uživatel již existuje"}), 409
    
    users[username] = {
        "password": data.get("password", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "is_admin": False, "banned": False,
        "coins": 0.0, "level": 1, "xp": 0,
        "luck_multiplier": 1.0, "has_podkova": False,
        "daily_streak": 1, "last_daily_claim": None,
        "vip_until": None, "vip_plus_until": None
    }
    save_data(DB_FILE, users)
    return jsonify({"status": "success"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True, silent=True) or {}
    login_id = str(data.get("login_id", "")).strip().lower()
    users = load_data(DB_FILE, {})
    for u_name, u_info in users.items():
        if login_id in [u_name.lower(), str(u_info.get("email", "")).lower()]:
            if u_info.get("banned", False): return jsonify({"status": "banned"}), 403
            if u_info.get("password") == data.get("password", ""):
                return jsonify({
                    "status": "success", "username": u_name,
                    "email": u_info.get("email", ""), "phone": u_info.get("phone", ""),
                    "coins": float(u_info.get("coins", 0.0)),
                    "level": u_info.get("level", 1), "xp": u_info.get("xp", 0),
                    "luck_multiplier": float(u_info.get("luck_multiplier", 1.0)),
                    "has_podkova": u_info.get("has_podkova", False),
                    "daily_streak": u_info.get("daily_streak", 1),
                    "last_daily_claim": u_info.get("last_daily_claim"),
                    "vip_until": u_info.get("vip_until"), "vip_plus_until": u_info.get("vip_plus_until"),
                    "is_admin": u_info.get("is_admin", False)
                }), 200
    return jsonify({"status": "error", "message": "Účet nenalezen"}), 404

@app.route('/earn-coins', methods=['POST'])
def earn_coins():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    amount = float(data.get("amount", 0.0))
    users = load_data(DB_FILE, {})
    if username not in users: return jsonify({"status": "error"}), 404
    
    users[username]["coins"] = round(float(users[username].get("coins", 0.0)) + amount, 2)
    save_data(DB_FILE, users)
    return jsonify({"status": "success", "coins": users[username]["coins"]}), 200

@app.route('/shop-buy-tier', methods=['POST'])
def shop_buy_tier():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    tier_type = data.get("type")
    hours = int(data.get("hours", 0))
    cost = float(data.get("cost", 0.0))

    users = load_data(DB_FILE, {})
    if username not in users: return jsonify({"status": "error"}), 404
    
    if float(users[username].get("coins", 0.0)) < cost:
        return jsonify({"status": "error", "message": "Nedostatek mincí"}), 400

    users[username]["coins"] = round(float(users[username]["coins"]) - cost, 2)
    now = datetime.now()
    key = f"{tier_type}_until"
    curr = users[username].get(key)
    base = datetime.fromisoformat(curr) if curr and datetime.fromisoformat(curr) > now else now

    if hours >= 876000: users[username][key] = "2099-01-01T00:00:00"
    else: users[username][key] = (base + timedelta(hours=hours)).isoformat()

    save_data(DB_FILE, users)
    return jsonify({"status": "success", "coins": users[username]["coins"]}), 200

@app.route('/sync-stats', methods=['POST'])
def sync_stats():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    users = load_data(DB_FILE, {})
    if username in users:
        for k in ["level", "xp", "password", "email", "phone", "daily_streak"]:
            if k in data: users[username][k] = data[k]
        if "last_daily_claim" in data: users[username]["last_daily_claim"] = data["last_daily_claim"]
        if "luck_multiplier" in data: users[username]["luck_multiplier"] = float(data["luck_multiplier"])
        if "has_podkova" in data: users[username]["has_podkova"] = data["has_podkova"]
        save_data(DB_FILE, users)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
