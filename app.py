import os
import json
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# MALÝ soubor s daty - Free účty I VIP klasik (mince/level/xp/vip_until/
# emeraldy/Wolfingo progres/srdíčka/odznaky/Wolfingo Plus+Ultra/...).
# VIP+ má svoje data (i přihlášení) na pythonanywhere.py - tam se sem
# vip_plus_until prakticky nepoužívá, necháno jen kvůli starším záznamům.
# Přihlášení (/login s heslem) je tu určené hlavně pro Free účty -
# VIP klasik se přihlašuje přes pythonanywhere.py a data si pak natáhne
# odsud přes /get-data (bez hesla, jen podle username).
#
# /sync-stats bere JAKÉKOLIV pole (kromě chráněných - heslo, admin, ban)
# a rovnou ho uloží k uživateli. Appka tak může posílat úplně cokoliv
# nového (nové Wolfingo pole, nové nastavení...) a nemusí se kvůli tomu
# nic měnit na serveru - vždy se to uloží a při přihlášení/get-data zase
# vrátí zpátky, i na jiném počítači.
# ---------------------------------------------------------------------------
app = Flask(__name__)
DB_FILE = "free_users.json"
PROTECTED_KEYS = {"password", "is_admin", "banned"}   # tohle přes /sync-stats nikdy nejde přepsat


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


def _public_view(u_name, u_info):
    """Celý záznam uživatele KROMĚ hesla - tohle appka dostane při loginu i get-data,
    takže se jí vrátí úplně všechno, co kdy přes /sync-stats poslala (i z jiného PC)."""
    out = {k: v for k, v in u_info.items() if k != "password"}
    out["status"] = "success"
    out["username"] = u_name
    return out


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
            if u_info.get("banned", False):
                return jsonify({"status": "banned"}), 403
            if u_info.get("password") == data.get("password", ""):
                return jsonify(_public_view(u_name, u_info)), 200
    return jsonify({"status": "error", "message": "Účet nenalezen"}), 404


@app.route('/get-data', methods=['POST'])
def get_data():
    """Vrátí VŠECHNA uložená data podle username, BEZ hesla (bez hesla proto,
    aby appka mohla data dotáhnout i po přihlášení přes pythonanywhere.py -
    typicky VIP klasik). Vrací se úplně vše, co bylo kdy přes /sync-stats
    uloženo (Wolfingo progres, emeraldy, srdíčka, odznaky, Plus/Ultra, ...),
    takže na novém PC appka dostane zpátky stejný stav jako na starém."""
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "").strip()
    users = load_data(DB_FILE, {})
    for u_name, u_info in users.items():
        if u_name.lower() == username.lower():
            if u_info.get("banned", False):
                return jsonify({"status": "banned"}), 403
            return jsonify(_public_view(u_name, u_info)), 200
    return jsonify({"status": "error", "message": "Účet nenalezen"}), 404


@app.route('/earn-coins', methods=['POST'])
def earn_coins():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    amount = float(data.get("amount", 0.0))
    users = load_data(DB_FILE, {})
    if username not in users:
        return jsonify({"status": "error"}), 404

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
    if username not in users:
        return jsonify({"status": "error"}), 404

    if float(users[username].get("coins", 0.0)) < cost:
        return jsonify({"status": "error", "message": "Nedostatek mincí"}), 400

    users[username]["coins"] = round(float(users[username]["coins"]) - cost, 2)
    now = datetime.now()
    key = f"{tier_type}_until"
    curr = users[username].get(key)
    base = datetime.fromisoformat(curr) if curr and datetime.fromisoformat(curr) > now else now

    if hours >= 876000:
        users[username][key] = "2099-01-01T00:00:00"
    else:
        users[username][key] = (base + timedelta(hours=hours)).isoformat()

    save_data(DB_FILE, users)
    return jsonify({"status": "success", "coins": users[username]["coins"]}), 200


@app.route('/update-account', methods=['POST'])
def update_account():
    """Změna hesla/e-mailu/telefonu - JEDINÉ místo, kudy jde měnit heslo
    (na rozdíl od /sync-stats, kde je heslo schválně chráněné proti přepsání)."""
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    users = load_data(DB_FILE, {})
    if username not in users:
        return jsonify({"status": "error"}), 404

    if data.get("password"):
        users[username]["password"] = data["password"]
    if data.get("email"):
        users[username]["email"] = data["email"]
    if data.get("phone"):
        users[username]["phone"] = data["phone"]

    save_data(DB_FILE, users)
    return jsonify({"status": "success"}), 200


@app.route('/sync-stats', methods=['POST'])
def sync_stats():
    """Obecné uložení - přijme JAKÁKOLIV pole (kromě hesla/admin/ban) a uloží je
    k uživateli. Díky tomu appka může synchronizovat Wolfingo progres, srdíčka,
    odznaky, Plus/Ultra, zvolené téma, co se chce uživatel učit, atd. - všechno
    napříč zařízeními, bez nutnosti cokoliv dalšího na serveru měnit."""
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    users = load_data(DB_FILE, {})
    if username in users:
        for k, v in data.items():
            if k in ("username",) or k in PROTECTED_KEYS:
                continue
            users[username][k] = v
        save_data(DB_FILE, users)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
