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
        "is_admin": False,
        "banned": False,
        "coins": 0,
        "vip_until": None,
        "vip_plus_until": None,
        "pm_pass_until": None,
        "multiplier_until": None,
        "has_luck": False
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
                return jsonify({"status": "banned"}), 403
            
            if u_info.get("password") == data.get("password", ""):
                return jsonify({
                    "status": "success", 
                    "username": u_name, 
                    "is_admin": u_info.get("is_admin", False),
                    "coins": u_info.get("coins", 0),
                    "multiplier_until": u_info.get("multiplier_until"),
                    "has_luck": u_info.get("has_luck", False)
                }), 200
            return jsonify({"status": "error", "message": "Špatné heslo"}), 401
    return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404

@app.route('/earn-coins', methods=['POST'])
def earn_coins():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    amount = data.get("amount", 0)
    
    users = load_data(DB_FILE, {})
    if username not in users:
        users[username] = {"password": "synced", "is_admin": True, "banned": False, "coins": 0}
        
    if "coins" not in users[username]: users[username]["coins"] = 0
        
    users[username]["coins"] += amount
    save_data(DB_FILE, users)
    return jsonify({"status": "success", "coins": users[username]["coins"]}), 200

# =========================================================
# UNIVERZÁLNÍ OBCHOD - Zvládne VIP, Funkce, Hodiny i Boosty
# =========================================================
@app.route('/shop-buy', methods=['POST'])
def shop_buy():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    cost = int(data.get("cost", 0))
    item = data.get("item") # "vip_plus", "pm_pass", "multiplier", "luck"
    duration_hours = int(data.get("duration_hours", 0))
    
    users = load_data(DB_FILE, {})
    if username not in users: return jsonify({"status": "error"}), 404
    if "coins" not in users[username]: users[username]["coins"] = 0
    
    if users[username]["coins"] >= cost:
        users[username]["coins"] -= cost
        now = datetime.now()
        
        if item == "luck":
            users[username]["has_luck"] = True
        else:
            key = f"{item}_until"
            current_exp = users[username].get(key)
            base_time = datetime.fromisoformat(current_exp) if current_exp and datetime.fromisoformat(current_exp) > now else now
            if duration_hours == 999999: # Doživotní
                users[username][key] = "2099-01-01T00:00:00"
            else:
                users[username][key] = (base_time + timedelta(hours=duration_hours)).isoformat()

        save_data(DB_FILE, users)
        return jsonify({"status": "success", "coins": users[username]["coins"]}), 200
    else:
        return jsonify({"status": "error", "message": f"Nemáš dost mincí. Chybí {cost - users[username]['coins']}!"}), 400

@app.route('/claim-vip-trial', methods=['POST'])
def claim_vip_trial():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    ip = get_client_ip()

    used_ips = load_data(IP_DB_FILE, {})
    if ip in used_ips.get("vip_trial", []): return jsonify({"status": "error", "message": "Tento PC už trial využil!"}), 403

    users = load_data(DB_FILE, {})
    if username not in users: users[username] = {"password": "synced", "coins": 0}
    users[username]["vip_until"] = (datetime.now() + timedelta(days=3)).isoformat()
    used_ips.setdefault("vip_trial", []).append(ip)
    save_data(DB_FILE, users)
    save_data(IP_DB_FILE, used_ips)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
