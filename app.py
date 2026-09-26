import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from supabase import create_client, Client

# ---------------------------------------------------------------------------
# Free účty (login/MyPC data/kešky Free) - teď na Supabase místo free_users.json.
# VIP klasik i VIP+ zůstávají beze změny na pythonanywhere.py.
#
# V Supabase je jedna tabulka "free_users" se sloupci: username, password, data
# (JSONB se vším ostatním - email, coins, level, xp, vip_until, vip_plus_until,
# wolfingo_plus_until, caches_premium_until, caches_premium_plus_until, ...).
# /sync-stats díky tomu pořád umí uložit JAKÉKOLIV nové pole, stejně jako dřív
# u free_users.json - jen se to teď ukládá do sloupce "data", ne do souboru.
#
# Potřebuje proměnné prostředí (nastavit v Render -> Environment):
#   SUPABASE_URL          - z Supabase: Project Settings -> API -> Project URL
#   SUPABASE_SERVICE_KEY  - z Supabase: Project Settings -> API -> service_role klíč
#                            (NE anon klíč - service_role smí zapisovat, appka ho
#                            nikdy nedostane do rukou, žije jen tady na serveru)
# ---------------------------------------------------------------------------
app = Flask(__name__)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE = "free_users"
PROTECTED_KEYS = {"password", "is_admin", "banned"}   # tohle přes /sync-stats nikdy nejde přepsat

DEFAULT_DATA = {
    "email": "", "phone": "",
    "is_admin": False, "banned": False,
    "coins": 0.0, "level": 1, "xp": 0,
    "luck_multiplier": 1.0, "has_podkova": False,
    "daily_streak": 1, "last_daily_claim": None,
    "vip_until": None, "vip_plus_until": None,
    "wolfingo_plus_until": None,           # nové - Wolfingo Plus (pomalejší varianta, tady na Supabase)
    "caches_premium_until": None,          # kostra - zatím se nikde neaktivuje
    "caches_premium_plus_until": None,     # kostra - zatím se nikde neaktivuje
}


def _get_row(username):
    if not username:
        return None
    res = supabase.table(TABLE).select("*").ilike("username", username).limit(1).execute()
    rows = res.data or []
    return rows[0] if rows else None


def _get_row_by_email(email):
    email = (email or "").lower()
    if not email:
        return None
    res = supabase.table(TABLE).select("*").execute()
    for r in res.data or []:
        if str((r.get("data") or {}).get("email", "")).lower() == email:
            return r
    return None


def _public_view(row):
    """Celá data uživatele KROMĚ hesla - appka dostane zpátky úplně všechno, co bylo
    kdy přes /sync-stats uloženo, i z jiného zařízení."""
    out = dict(row.get("data") or {})
    out["status"] = "success"
    out["username"] = row["username"]
    return out


def _extend_until(d, key, hours):
    now = datetime.now()
    base = now
    curr = d.get(key)
    if curr:
        try:
            if datetime.fromisoformat(curr) > now:
                base = datetime.fromisoformat(curr)
        except Exception:
            pass
    if hours >= 876000:
        d[key] = "2099-01-01T00:00:00"
    else:
        d[key] = (base + timedelta(hours=hours)).isoformat()
    return d[key]


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"status": "error", "message": "Chybí username"}), 400
    if _get_row(username):
        return jsonify({"status": "error", "message": "Uživatel již existuje"}), 409

    user_data = dict(DEFAULT_DATA)
    user_data["email"] = data.get("email", "")
    user_data["phone"] = data.get("phone", "")

    supabase.table(TABLE).insert({
        "username": username,
        "password": data.get("password", ""),
        "data": user_data,
    }).execute()
    return jsonify({"status": "success"}), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    login_id = str(data.get("login_id", "")).strip()

    row = _get_row(login_id) or _get_row_by_email(login_id)
    if not row:
        return jsonify({"status": "error", "message": "Účet nenalezen"}), 404
    if (row.get("data") or {}).get("banned", False):
        return jsonify({"status": "banned"}), 403
    if row.get("password") != data.get("password", ""):
        return jsonify({"status": "error", "message": "Účet nenalezen"}), 404
    return jsonify(_public_view(row)), 200


@app.route("/get-data", methods=["POST"])
def get_data():
    """Vrátí VŠECHNA uložená data podle username, bez hesla - appka si je natáhne
    i na novém PC (typicky po přihlášení přes pythonanywhere.py u VIP klasik)."""
    data = request.get_json(force=True, silent=True) or {}
    row = _get_row(data.get("username", "").strip())
    if not row:
        return jsonify({"status": "error", "message": "Účet nenalezen"}), 404
    if (row.get("data") or {}).get("banned", False):
        return jsonify({"status": "banned"}), 403
    return jsonify(_public_view(row)), 200


@app.route("/earn-coins", methods=["POST"])
def earn_coins():
    data = request.get_json(force=True, silent=True) or {}
    row = _get_row(data.get("username"))
    if not row:
        return jsonify({"status": "error"}), 404
    d = row.get("data") or {}
    d["coins"] = round(float(d.get("coins", 0.0)) + float(data.get("amount", 0.0)), 2)
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success", "coins": d["coins"]}), 200


@app.route("/shop-buy-tier", methods=["POST"])
def shop_buy_tier():
    """Funguje na jakékoliv '<typ>_until' pole - vip_until, vip_plus_until,
    wolfingo_plus_until, časem i caches_premium_until/caches_premium_plus_until."""
    data = request.get_json(force=True, silent=True) or {}
    tier_type = data.get("type")
    hours = int(data.get("hours", 0))
    cost = float(data.get("cost", 0.0))

    row = _get_row(data.get("username"))
    if not row:
        return jsonify({"status": "error"}), 404
    d = row.get("data") or {}
    if float(d.get("coins", 0.0)) < cost:
        return jsonify({"status": "error", "message": "Nedostatek mincí"}), 400

    d["coins"] = round(float(d["coins"]) - cost, 2)
    new_val = _extend_until(d, f"{tier_type}_until", hours)
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success", "coins": d["coins"], f"{tier_type}_until": new_val}), 200


@app.route("/update-account", methods=["POST"])
def update_account():
    """Změna hesla/e-mailu/telefonu - jediné místo, kudy jde měnit heslo."""
    data = request.get_json(force=True, silent=True) or {}
    row = _get_row(data.get("username"))
    if not row:
        return jsonify({"status": "error"}), 404

    d = row.get("data") or {}
    updates = {}
    if data.get("password"):
        updates["password"] = data["password"]
    if data.get("email"):
        d["email"] = data["email"]
    if data.get("phone"):
        d["phone"] = data["phone"]
    updates["data"] = d
    supabase.table(TABLE).update(updates).eq("username", row["username"]).execute()
    return jsonify({"status": "success"}), 200


@app.route("/sync-stats", methods=["POST"])
def sync_stats():
    """Obecné uložení - přijme JAKÁKOLIV pole (kromě hesla/admin/ban) a uloží je
    do sloupce 'data'. Appka tak může posílat cokoliv nového, aniž by se muselo
    cokoliv měnit v Supabase."""
    data = request.get_json(force=True, silent=True) or {}
    row = _get_row(data.get("username"))
    if not row:
        return jsonify({"status": "error"}), 404

    d = row.get("data") or {}
    for k, v in data.items():
        if k in ("username",) or k in PROTECTED_KEYS:
            continue
        d[k] = v
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success"}), 200


# --------------------- Caches Premium / Premium Plus - zatím jen kostra ---------------------
@app.route("/caches-premium/status", methods=["POST"])
def caches_premium_status():
    data = request.get_json(force=True, silent=True) or {}
    row = _get_row(data.get("username", ""))
    if not row:
        return jsonify({"status": "error"}), 404
    d = row.get("data") or {}
    return jsonify({
        "status": "success",
        "caches_premium_until": d.get("caches_premium_until"),
        "caches_premium_plus_until": d.get("caches_premium_plus_until"),
    }), 200


@app.route("/caches-premium/activate", methods=["POST"])
def caches_premium_activate():
    """Prázdná kostra - schválně zatím nic neaktivuje. Až bude jasné, jak se Caches
    Premium(+) má prodávat, doplní se sem stejná logika jako v /shop-buy-tier."""
    return jsonify({"status": "not_implemented", "message": "Caches Premium/Premium Plus zatím není aktivní."}), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
