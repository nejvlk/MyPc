import os
import re
import math
import time as _time_mod
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE = "free_users"
TABLE_NESTS = "nests"

ADMIN_PWD = "SuperTajneHeslo123"

PROTECTED_KEYS = {"password", "is_admin", "banned", "admin_pending", "unban_reason"}

NEST_TYPES_SERVER = {"vosy", "srsni", "vcely"}
NEST_NOTE_MAX_LEN = 140
NEST_COOLDOWN_HOURS = 24
NEST_REWARD_COINS = 1.0

DEFAULT_DATA = {
    "email": "", "phone": "",
    "is_admin": False, "banned": False,
    "admin_pending": False, "unban_reason": None,
    "coins": 0.0, "level": 1, "xp": 0,
    "luck_multiplier": 1.0, "has_podkova": False,
    "daily_streak": 1, "last_daily_claim": None,
    "vip_until": None, "vip_plus_until": None,
    "wolfingo_plus_until": None,
    "caches_premium_until": None,
    "caches_premium_plus_until": None,
    "last_nest_claim": None,
}


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


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
    return data.get("admin_pwd") == ADMIN_PWD


def _is_active_iso(iso_str, now):
    if not iso_str:
        return False
    try:
        return datetime.fromisoformat(iso_str) > now
    except Exception:
        return False


# ===========================================================================
# EVENT SYSTÉM - in-memory (resetuje se při restartu serveru)
# ===========================================================================
_active_event = {}
_event_history = []   # in-memory log eventů - resetuje se při restartu serveru
_motd_state = {"message": "", "active": False}
_broadcast_log = []    # in-memory log broadcastů - resetuje se při restartu serveru


def _get_active_event_info():
    ev = _active_event
    if not ev or ev.get("type") == "none":
        return {"active": False}
    remaining = ev.get("ends_at", 0) - _time_mod.time()
    if remaining <= 0:
        return {"active": False}
    return {
        "active": True,
        "type": ev["type"],
        "multiplier": ev["multiplier"],
        "minutes_left": max(1, int(remaining // 60)),
    }


@app.route("/active-event", methods=["GET"])
def active_event_get():
    return jsonify(_get_active_event_info()), 200


@app.route("/admin/set-event", methods=["POST"])
def admin_set_event():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401

    typ = data.get("type", "none")
    mult = float(data.get("multiplier", 1))
    dur_min = int(data.get("duration_minutes", 0))

    _active_event.clear()
    if typ in ("coins", "emeralds") and dur_min > 0:
        _active_event.update({
            "type": typ,
            "multiplier": mult,
            "ends_at": _time_mod.time() + dur_min * 60,
        })
        _event_history.insert(0, {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": typ,
            "multiplier": mult,
            "duration": dur_min,
            "admin": "admin",
        })
        del _event_history[200:]
    else:
        _active_event["type"] = "none"

    return jsonify({"status": "success", **_get_active_event_info()}), 200


@app.route("/admin/event-history", methods=["POST"])
def admin_event_history():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    return jsonify({"status": "success", "history": _event_history}), 200


# ===========================================================================
# STANDARDNÍ ENDPOINTY
# ===========================================================================

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


@app.route("/nests", methods=["GET"])
def nests_get():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    radius_km = request.args.get("radius_km", default=3.0, type=float)
    req_username = (request.args.get("username") or "").strip() or None
    req_device_id = (request.args.get("device_id") or "").strip() or None
    if lat is None or lon is None:
        return jsonify({"status": "error", "message": "Chybí lat/lon"}), 400
    res = supabase.table(TABLE_NESTS).select("*").execute()
    out = []
    for r in res.data or []:
        try:
            r_lat, r_lon = float(r["lat"]), float(r["lon"])
        except (TypeError, ValueError, KeyError):
            continue
        if _haversine_km(lat, lon, r_lat, r_lon) <= radius_km:
            mine = bool((req_username and r.get("username") == req_username) or
                        (req_device_id and r.get("device_id") == req_device_id))
            out.append({
                "id": r.get("id"),
                "lat": r_lat,
                "lon": r_lon,
                "type": r.get("type"),
                "hive_type": r.get("hive_type"),
                "note": r.get("note"),
                "mine": mine,
            })
    return jsonify({"nests": out}), 200


@app.route("/nests/delete", methods=["POST"])
def nests_delete():
    data = request.get_json(force=True, silent=True) or {}
    nest_id = data.get("id")
    username = (data.get("username") or "").strip() or None
    device_id = (data.get("device_id") or "").strip() or None
    if nest_id is None:
        return jsonify({"ok": False, "reason": "Chybí id hlášení."}), 400
    res = supabase.table(TABLE_NESTS).select("*").eq("id", nest_id).limit(1).execute()
    rows = res.data or []
    if not rows:
        return jsonify({"ok": False, "reason": "Hlášení už neexistuje."}), 404
    row = rows[0]
    owns = (username and row.get("username") == username) or (device_id and row.get("device_id") == device_id)
    if not owns:
        return jsonify({"ok": False, "reason": "Tohle hlášení není tvoje."}), 403
    supabase.table(TABLE_NESTS).delete().eq("id", nest_id).execute()
    return jsonify({"ok": True}), 200


@app.route("/nests", methods=["POST"])
def nests_post():
    data = request.get_json(force=True, silent=True) or {}
    lat, lon = data.get("lat"), data.get("lon")
    kind = data.get("type")
    hive_type = data.get("hive_type")
    note = str(data.get("note") or "").strip()
    device_id = data.get("device_id")
    username = str(data.get("username") or "").strip() or None

    if lat is None or lon is None or kind not in NEST_TYPES_SERVER:
        return jsonify({"ok": False, "reason": "Neplatné hlášení."}), 400
    if len(note) > NEST_NOTE_MAX_LEN:
        return jsonify({"ok": False, "reason": "Poznámka je moc dlouhá."}), 400
    if re.search(r"https?://|www\.", note.lower()):
        return jsonify({"ok": False, "reason": "Odkazy v poznámce nejsou povolené."}), 400

    now = datetime.now()
    reward = None
    row = _get_row(username) if username else None

    if row:
        if (row.get("data") or {}).get("banned", False):
            return jsonify({"ok": False, "reason": "Účet je zabanovaný."}), 403
        d = row.get("data") or {}
        last_claim = d.get("last_nest_claim")
        if last_claim:
            try:
                remaining = timedelta(hours=NEST_COOLDOWN_HOURS) - (now - datetime.fromisoformat(last_claim))
                if remaining.total_seconds() > 0:
                    hours_left = int(remaining.total_seconds() // 3600)
                    minutes_left = int((remaining.total_seconds() % 3600) // 60)
                    return jsonify({
                        "ok": False,
                        "reason": f"Hlášení lze poslat jen 1x za {NEST_COOLDOWN_HOURS}h. "
                                  f"Zkus to za {hours_left}h {minutes_left}m.",
                    }), 429
            except Exception:
                pass
        d["last_nest_claim"] = now.isoformat()
        d["coins"] = round(float(d.get("coins", 0.0)) + NEST_REWARD_COINS, 2)
        supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
        reward = NEST_REWARD_COINS
    elif device_id:
        since = (now - timedelta(hours=NEST_COOLDOWN_HOURS)).isoformat()
        try:
            recent = (supabase.table(TABLE_NESTS).select("created_at")
                      .eq("device_id", device_id).gte("created_at", since).limit(1).execute())
            if recent.data:
                return jsonify({
                    "ok": False,
                    "reason": f"Z tohoto zařízení lze poslat hlášení jen 1x za {NEST_COOLDOWN_HOURS}h.",
                }), 429
        except Exception:
            pass

    supabase.table(TABLE_NESTS).insert({
        "lat": lat, "lon": lon, "type": kind, "hive_type": hive_type,
        "note": note or None, "device_id": device_id, "username": username,
        "created_at": now.isoformat(),
    }).execute()
    return jsonify({"ok": True, "reward_coins": reward}), 200


@app.route("/shop-buy-tier", methods=["POST"])
def shop_buy_tier():
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
    return jsonify({"status": "not_implemented", "message": "Caches Premium/Premium Plus zatím není aktivní."}), 501


# ===========================================================================
# ADMIN ROUTY
# ===========================================================================

@app.route("/admin/users", methods=["POST"])
def admin_users():
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
            "coins": float(d.get("coins", 0.0)),
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


@app.route("/admin/add-currency", methods=["POST"])
def admin_add_currency():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    row = _get_row(data.get("user", ""))
    if not row:
        return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404
    ctype = data.get("type", "coins")
    if ctype not in ("coins", "emeralds"):
        return jsonify({"status": "error", "message": "Neplatný typ měny"}), 400
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Neplatná částka"}), 400
    d = row.get("data") or {}
    current = float(d.get(ctype, 0.0))
    d[ctype] = round(max(0.0, current + amount), 2)
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success", "user": row["username"], ctype: d[ctype]}), 200


@app.route("/admin/set-level", methods=["POST"])
def admin_set_level():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    row = _get_row(data.get("user", ""))
    if not row:
        return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404
    try:
        level = int(data.get("level", 1))
        xp = int(data.get("xp", 0))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Neplatný level/XP"}), 400
    d = row.get("data") or {}
    d["level"] = max(1, level)
    d["xp"] = max(0, xp)
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success", "user": row["username"], "level": d["level"], "xp": d["xp"]}), 200


@app.route("/admin/bulk-reward", methods=["POST"])
def admin_bulk_reward():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    rtype = data.get("type", "coins")
    if rtype not in ("coins", "emeralds", "xp"):
        return jsonify({"status": "error", "message": "Neplatný typ odměny"}), 400
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Neplatná částka"}), 400
    if amount <= 0:
        return jsonify({"status": "error", "message": "Částka musí být kladná"}), 400
    res = supabase.table(TABLE).select("*").execute()
    count = 0
    for row in res.data or []:
        d = row.get("data") or {}
        current = float(d.get(rtype, 0.0))
        d[rtype] = round(current + amount, 2) if rtype != "xp" else int(current + amount)
        supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
        count += 1
    return jsonify({"status": "success", "users_affected": count}), 200


@app.route("/admin/set-score", methods=["POST"])
def admin_set_score():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    row = _get_row(data.get("user", ""))
    if not row:
        return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404
    try:
        score = int(data.get("score", 0))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Neplatné skóre"}), 400
    d = row.get("data") or {}
    d["score"] = score
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success", "user": row["username"], "score": score}), 200


@app.route("/admin/set-vip", methods=["POST"])
def admin_set_vip():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    row = _get_row(data.get("user", ""))
    if not row:
        return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404
    tier = data.get("tier", "none")
    far_future = "2099-01-01T00:00:00"
    d = row.get("data") or {}
    if tier == "vip":
        d["vip_until"] = far_future
        d["vip_plus_until"] = None
    elif tier == "vip+":
        d["vip_plus_until"] = far_future
    elif tier == "none":
        d["vip_until"] = None
        d["vip_plus_until"] = None
    else:
        return jsonify({"status": "error", "message": "Neplatný tier"}), 400
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success", "user": row["username"],
                     "vip_until": d.get("vip_until"),
                     "vip_plus_until": d.get("vip_plus_until")}), 200


@app.route("/admin/vip-list", methods=["POST"])
def admin_vip_list():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    res = supabase.table(TABLE).select("*").execute()
    now = datetime.now()
    out = []
    for row in res.data or []:
        d = row.get("data") or {}
        if _is_active_iso(d.get("vip_plus_until"), now):
            out.append({"username": row["username"], "tier": "VIP+", "expiry": d.get("vip_plus_until")})
        elif _is_active_iso(d.get("vip_until"), now):
            out.append({"username": row["username"], "tier": "VIP", "expiry": d.get("vip_until")})
    return jsonify({"status": "success", "vip_users": out}), 200


@app.route("/admin/broadcast", methods=["POST"])
def admin_broadcast():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    msg = str(data.get("message", "")).strip()
    if not msg:
        return jsonify({"status": "error", "message": "Zpráva je prázdná"}), 400
    _broadcast_log.insert(0, {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": msg})
    del _broadcast_log[200:]
    return jsonify({"status": "success"}), 200


@app.route("/admin/set-motd", methods=["POST"])
def admin_set_motd():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    _motd_state["message"] = str(data.get("message", ""))
    _motd_state["active"] = bool(data.get("active", False))
    return jsonify({"status": "success"}), 200


@app.route("/admin/get-motd", methods=["POST"])
def admin_get_motd():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    return jsonify({"status": "success", **_motd_state}), 200


@app.route("/admin/stats", methods=["POST"])
def admin_stats():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    res = supabase.table(TABLE).select("*").execute()
    rows = res.data or []
    total_users = len(rows)
    levels = [int((r.get("data") or {}).get("level", 1)) for r in rows]
    avg_level = round(sum(levels) / len(levels), 1) if levels else 0
    total_coins = round(sum(float((r.get("data") or {}).get("coins", 0.0)) for r in rows), 2)
    total_emeralds = round(sum(float((r.get("data") or {}).get("emeralds", 0.0)) for r in rows), 2)
    top = sorted(rows, key=lambda r: float((r.get("data") or {}).get("coins", 0.0)), reverse=True)[:10]
    top_user = top[0]["username"] if top else "–"
    top_users = [{"user": r["username"], "logins": "–", "last": "–"} for r in top]
    return jsonify({
        "status": "success",
        "online_today": "–",
        "total_users": total_users,
        "avg_level": avg_level,
        "top_user": top_user,
        "total_coins": total_coins,
        "total_emeralds": total_emeralds,
        "top_users": top_users,
    }), 200


@app.route("/admin/remove-coins", methods=["POST"])
def admin_remove_coins():
    data = request.get_json(force=True, silent=True) or {}
    if not _check_admin(data):
        return jsonify({"status": "error", "message": "Špatné admin heslo"}), 401
    row = _get_row(data.get("user", ""))
    if not row:
        return jsonify({"status": "error", "message": "Uživatel nenalezen"}), 404
    try:
        amount = float(data.get("amount", 0.0))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Neplatná částka"}), 400
    if amount <= 0:
        return jsonify({"status": "error", "message": "Částka musí být kladné číslo"}), 400
    d = row.get("data") or {}
    current = float(d.get("coins", 0.0))
    d["coins"] = round(max(0.0, current - amount), 2)
    supabase.table(TABLE).update({"data": d}).eq("username", row["username"]).execute()
    return jsonify({"status": "success", "user": row["username"], "coins": d["coins"]}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
