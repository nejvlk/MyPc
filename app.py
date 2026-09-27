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

# Heslo pro admin panel (adminpanel.py) - MUSÍ být stejné jako ADMIN_PWD tam
# a stejné jako ADMIN_PWD na pythonanywhere.py serveru.
ADMIN_PWD = "SuperTajneHeslo123"

# Chráněná pole - přes /sync-stats je nejde přepsat (mění se jen přes vyhrazené
# endpointy: /update-account, /shop-buy-tier, /request-admin, /request-unban, /admin/*).
PROTECTED_KEYS = {"password", "is_admin", "banned", "admin_pending", "unban_reason"}

# Kolik hodin musí uplynout mezi dvěma odměnami za přidání úlu/hnízda (anti-spam).
HIVE_COOLDOWN_HOURS = 24
# Kolik kreditů (coins) appka dostane za jeden přidaný úl/hnízdo.
HIVE_REWARD_COINS = 1.0

DEFAULT_DATA = {
    "email": "", "phone": "",
    "is_admin": False, "banned": False,
    "admin_pending": False, "unban_reason": None,
    "coins": 0.0, "level": 1, "xp": 0,
    "luck_multiplier": 1.0, "has_podkova": False,
    "daily_streak": 1, "last_daily_claim": None,
    "vip_until": None, "vip_plus_until": None,
    "wolfingo_plus_until": None,           # nové - Wolfingo Plus (pomalejší varianta, tady na Supabase)
    "caches_premium_until": None,          # kostra - zatím se nikde neaktivuje
    "caches_premium_plus_until": None,     # kostra - zatím se nikde neaktivuje
    "hives": [],                           # seznam přidaných včelích úlů/hnízd
    "last_hive_claim": None,               # kdy naposledy dostal odměnu za úl/hnízdo (anti-spam, 1x/24h)
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


def _check_admin(data):
    """True pokud payload obsahuje správné admin_pwd. Používá se pro všechny /admin/* routy."""
    return data.get("admin_pwd") == ADMIN_PWD


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


@app.route("/request-admin", methods=["POST"])
def request_admin():
    """Volá appka po registraci, když uživatel zaškrtl 'Chci požádat o ADMIN účet'
    a zadal správné potvrzovací heslo. Jen zařadí do fronty, kterou schvaluje
    adminpanel.py v záložce 'Admin Žádosti'."""
    data = request.get_json(force=True, silent=True) or {}
    row = _get_row(data.get("username", ""))
    if not row:
        return jsonify({"status": "error", "message": "Účet nenalezen"}), 404

    d = row.get("data") or {}
    if d.get("is_admin"):
        return jsonify({"status": "success", "message": "Účet je už admin"}), 200

    d["admin_pending"] = True
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success"}), 200


@app.route("/request-unban", methods=["POST"])
def request_unban():
    """Volá appka, když se zabanovaný uživatel odvolává."""
    data = request.get_json(force=True, silent=True) or {}
    row = _get_row(data.get("username", ""))
    if not row:
        return jsonify({"status": "error", "message": "Účet nenalezen"}), 404

    d = row.get("data") or {}
    if not d.get("banned"):
        return jsonify({"status": "error", "message": "Účet není zabanovaný"}), 400

    d["unban_reason"] = str(data.get("reason", "")).strip() or "(bez uvedeného důvodu)"
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
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


@app.route("/add-hive", methods=["POST"])
def add_hive():
    """Přidání včelího úlu nebo hnízda appkou. Za každý přidaný úl/hnízdo se dá
    odměna HIVE_REWARD_COINS kreditů, ale jen jednou za HIVE_COOLDOWN_HOURS hodin
    na uživatele (anti-spam) - i kdyby appka poslala víc požadavků rychle po sobě,
    samotný úl/hnízdo se do seznamu uloží vždycky, ale kredity se přičtou jen když
    cooldown už uplynul.

    Očekávaný JSON:
      username (povinné)
      type     ("ul" nebo "hnizdo", volitelné, default "ul")
      name     (volitelný název/popisek)
      lat, lon (volitelné souřadnice)
    """
    data = request.get_json(force=True, silent=True) or {}
    row = _get_row(data.get("username"))
    if not row:
        return jsonify({"status": "error", "message": "Účet nenalezen"}), 404
    if (row.get("data") or {}).get("banned", False):
        return jsonify({"status": "banned"}), 403

    d = row.get("data") or {}
    now = datetime.now()

    # --- anti-spam kontrola cooldownu ---
    cooldown_active = False
    hours_left = 0
    minutes_left = 0
    last_claim = d.get("last_hive_claim")
    if last_claim:
        try:
            last_dt = datetime.fromisoformat(last_claim)
            elapsed = now - last_dt
            remaining = timedelta(hours=HIVE_COOLDOWN_HOURS) - elapsed
            if remaining.total_seconds() > 0:
                cooldown_active = True
                hours_left = int(remaining.total_seconds() // 3600)
                minutes_left = int((remaining.total_seconds() % 3600) // 60)
        except Exception:
            pass

    if cooldown_active:
        return jsonify({
            "status": "error",
            "message": f"Úl/hnízdo lze odměnit jen 1x za {HIVE_COOLDOWN_HOURS}h. Zkus to za {hours_left}h {minutes_left}m.",
            "cooldown": True,
            "hours_left": hours_left,
            "minutes_left": minutes_left,
            "coins": d.get("coins", 0.0),
        }), 429

    # --- uložení úlu/hnízda a odměna ---
    hive_type = data.get("type", "ul")  # "ul" nebo "hnizdo"
    hive_entry = {
        "type": hive_type,
        "name": data.get("name", ""),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
        "added_at": now.isoformat(),
    }

    hives = d.get("hives") or []
    hives.append(hive_entry)
    d["hives"] = hives
    d["last_hive_claim"] = now.isoformat()
    d["coins"] = round(float(d.get("coins", 0.0)) + HIVE_REWARD_COINS, 2)

    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({
        "status": "success",
        "coins": d["coins"],
        "reward": HIVE_REWARD_COINS,
        "hives_count": len(hives),
        "hive": hive_entry,
    }), 200


@app.route("/get-hives", methods=["POST"])
def get_hives():
    """Vrátí seznam všech přidaných úlů/hnízd daného uživatele."""
    data = request.get_json(force=True, silent=True) or {}
    row = _get_row(data.get("username"))
    if not row:
        return jsonify({"status": "error", "message": "Účet nenalezen"}), 404
    d = row.get("data") or {}
    return jsonify({"status": "success", "hives": d.get("hives") or []}), 200


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
    """Obecné uložení - přijme JAKÁKOLIV pole (kromě hesla/admin/ban/admin_pending/
    unban_reason) a uloží je do sloupce 'data'. Appka tak může posílat cokoliv nového,
    aniž by se muselo cokoliv měnit v Supabase."""
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


# ===========================================================================
# ADMIN ROUTY - volá je výhradně adminpanel.py, vždy s "admin_pwd" v těle.
# ===========================================================================

@app.route("/admin/users", methods=["POST"])
def admin_users():
    """Vrátí všechny Free účty (bez hesla) pro tabulku 'Všichni Uživatelé & BANY'."""
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401

    res = supabase.table(TABLE).select("*").execute()
    out = {}
    for row in res.data or []:
        d = row.get("data") or {}
        out[row["username"]] = {
            "email": d.get("email", ""),
            "phone": d.get("phone", ""),
            "banned": bool(d.get("banned", False)),
            "is_admin": bool(d.get("is_admin", False)),
        }
    return jsonify({"status": "success", "users": out}), 200


@app.route("/admin/toggle-ban", methods=["POST"])
def admin_toggle_ban():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401

    row = _get_row(data.get("user", ""))
    if not row:
        return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404

    d = row.get("data") or {}
    d["banned"] = not bool(d.get("banned", False))
    if not d["banned"]:
        d["unban_reason"] = None
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success", "banned": d["banned"]}), 200


@app.route("/admin/delete-user", methods=["POST"])
def admin_delete_user():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401

    row = _get_row(data.get("user", ""))
    if not row:
        return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404

    supabase.table(TABLE).delete().eq("username", row["username"]).execute()
    return jsonify({"status": "success"}), 200


@app.route("/admin/unban-requests", methods=["POST"])
def admin_unban_requests():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401

    res = supabase.table(TABLE).select("*").execute()
    out = {}
    for row in res.data or []:
        d = row.get("data") or {}
        if d.get("banned") and d.get("unban_reason"):
            out[row["username"]] = {"reason": d.get("unban_reason")}
    return jsonify({"status": "success", "requests": out}), 200


@app.route("/admin/approve-unban", methods=["POST"])
def admin_approve_unban():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401

    row = _get_row(data.get("user", ""))
    if not row:
        return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404

    d = row.get("data") or {}
    d["banned"] = False
    d["unban_reason"] = None
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success"}), 200


@app.route("/admin/admin-requests", methods=["POST"])
def admin_admin_requests():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401

    res = supabase.table(TABLE).select("*").execute()
    pending = []
    for row in res.data or []:
        d = row.get("data") or {}
        if d.get("admin_pending") and not d.get("is_admin"):
            pending.append(row["username"])
    return jsonify({"status": "success", "requests": pending}), 200


@app.route("/admin/approve-admin", methods=["POST"])
def admin_approve_admin():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401

    row = _get_row(data.get("user", ""))
    if not row:
        return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404

    d = row.get("data") or {}
    d["is_admin"] = True
    d["admin_pending"] = False
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
