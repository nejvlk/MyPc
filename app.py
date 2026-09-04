import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

FREE_USERS_FILE = "free_users.json"
PENDING_CARDS_FILE = "pending_cards.json"

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

free_users_db = load_json(FREE_USERS_FILE, {})
pending_cards = load_json(PENDING_CARDS_FILE, [])

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    user = data.get('username')
    pwd = data.get('password')

    if not user or not pwd:
        return jsonify({"status": "error", "message": "Zadejte jméno i heslo"}), 400
    if user in free_users_db:
        return jsonify({"status": "error", "message": "Uživatel již existuje"}), 400

    free_users_db[user] = {
        "password": pwd,
        "premium": False,
        "hwid": data.get("hwid", "Neznámé")
    }
    save_json(FREE_USERS_FILE, free_users_db)
    return jsonify({"status": "success", "message": "Free účet vytvořen"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = data.get('username')
    pwd = data.get('password')

    if user in free_users_db and free_users_db[user]["password"] == pwd:
        return jsonify({"status": "success", "premium": False, "message": "Přihlášen přes Free server"}), 200
    
    return jsonify({"status": "error", "message": "Špatné jméno nebo heslo"}), 401

@app.route('/activate-pm', methods=['POST'])
def activate_pm():
    data = request.get_json() or {}
    pending_cards.append(data)
    save_json(PENDING_CARDS_FILE, pending_cards)
    return jsonify({"status": "success", "message": "Kód karty byl odeslán ke schválení."}), 200

@app.route('/admin/pending', methods=['POST'])
def get_pending():
    return jsonify({"pending": pending_cards}), 200

@app.route('/admin/remove-pending', methods=['POST'])
def remove_pending():
    user_done = request.json.get("user")
    global pending_cards
    pending_cards = [c for c in pending_cards if c.get("user") != user_done]
    save_json(PENDING_CARDS_FILE, pending_cards)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run()
