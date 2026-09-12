import os
import json
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

DB_FILE = "free_users.json"
IP_DB_FILE = "used_ips.json"

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

def get_client_ip():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "").strip()
    users = load_data(DB_FILE, {})
    
    if username.lower() in [u.lower() for u in users.keys()]:
        return jsonify({"status": "error", "message": "Jméno již existuje"}), 409

    users[username] = {
        "password": data.get("password", ""), 
        "email": data.get("email", ""), 
        "phone": data.get("phone", ""), 
        "is_admin": False,
        "banned": False,
        "coins": 0,
        "vip_until": None,
        "vip_plus_until": None
    }
    save_data(DB_FILE, users)
    return jsonify({"status": "success"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True, silent=True) or {}
    login_id = str(data.get("login_id", "")).strip().lower()
    
    users = load_data(DB_FILE, {})
    for u_name, u_info in users.items():
        if login_id in [u_name.lower(), str(u_info.get("email", "")).lower(), str(u_info.get("phone", ""))]:
            if u_info.get("banned", False):
                return jsonify({"status": "banned", "username": u_name, "message": "BANNED"}), 403
            
            if u_info.get("password") == data.get("password", ""):
                return jsonify({
                    "status": "success", 
                    "username": u_name, 
                    "is_admin": u_info.get("is_admin", False),
                    "coins": u_info.get("coins", 0) # Pokud tam není, pošle 0
                }), 200
            return jsonify({"status": "error", "message": "Špatné heslo"}), 401
    return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404

# ZÍSKÁVÁNÍ MINCÍ - NYNÍ 100% BEZPEČNÉ PRO STARÉ ÚČTY
@app.route('/earn-coins', methods=['POST'])
def earn_coins():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    amount = data.get("amount", 0)
    
    users = load_data(DB_FILE, {})
    if username in users:
        # OPRAVA: Záchrana pro staré účty (vyrobí peněženku)
        if "coins" not in users[username]:
            users[username]["coins"] = 0
            
        users[username]["coins"] += amount
        save_data(DB_FILE, users)
        return jsonify({"status": "success", "coins": users[username]["coins"]}), 200
    return jsonify({"status": "error"}), 404

# NÁKUP VIP+ ZA MINCE (Stojí 5000 mincí na 14 dní)
@app.route('/buy-vip-plus', methods=['POST'])
def buy_vip_plus():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    users = load_data(DB_FILE, {})
    
    if username in users:
        # OPRAVA: Záchrana pro staré účty
        if "coins" not in users[username]:
            users[username]["coins"] = 0

        if users[username]["coins"] >= 5000:
            users[username]["coins"] -= 5000
            now = datetime.now()
            users[username]["vip_plus_until"] = (now + timedelta(days=14)).isoformat()
            save_data(DB_FILE, users)
            return jsonify({"status": "success", "coins": users[username]["coins"]}), 200
        else:
            return jsonify({"status": "error", "message": "Nemáš dost mincí! Potřebuješ 5000."}), 400
    return jsonify({"status": "error"}), 404

@app.route('/claim-vip-trial', methods=['POST'])
def claim_vip_trial():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    ip = get_client_ip()

    used_ips = load_data(IP_DB_FILE, {})
    if ip in used_ips.get("vip_trial", []):
        return jsonify({"status": "error", "message": "Tento PC už 3denní trial využil!"}), 403

    users = load_data(DB_FILE, {})
    if username in users:
        now = datetime.now()
        users[username]["vip_until"] = (now + timedelta(days=3)).isoformat()
        used_ips.setdefault("vip_trial", []).append(ip)
        save_data(DB_FILE, users)
        save_data(IP_DB_FILE, used_ips)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404

@app.route('/admin/toggle-ban', methods=['POST'])
def toggle_ban():
    data = request.get_json(force=True, silent=True) or {}
    user_target = data.get("user")
    users = load_data(DB_FILE, {})
    if user_target in users:
        users[user_target]["banned"] = not users[user_target].get("banned", False)
        save_data(DB_FILE, users)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
