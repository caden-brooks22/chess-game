import json
from pathlib import Path

BACK_END_DIR = Path(__file__).resolve().parent
USERS_FILE = BACK_END_DIR / "users.json"

def find_user(username):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["users"].get(username)

def login(username, password):
    user = find_user(username)
    if user and user["password_hash"] == password:
        return user
    return False
        

def add_user(username, password_hash, nationality="unknown", settings=None):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if username in data["users"]:
        return 1  # User already exists
    if username_check(username)!= 0:
        return username_check(username)
    if password_check(password_hash) != 0:
        return password_check(password_hash)
    if settings is None:
        settings = data["users"]["Guest"]["settings"]
        
    data["users"][username] = {
        "username": username,
        "password_hash": password_hash,
        "nationality": nationality,
        "settings": settings
    }
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data["users"][username]

def edit_settings(username, settings):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data["users"][username] != "Guest":
        data["users"][username]["settings"] = settings
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("edited settings!")

def edit_password(username, password):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data["users"][username] != "Guest":
        data["users"][username]["settings"] = password
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("edited password!")

def edit_username(username, new_username):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data["users"][username] != "Guest":
        data["users"][username]["settings"] = new_username
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("edited username!")

def password_check(password):
    if len(password) < 8:
        return 3 # password not long enough
    
    allowed_special_chars = ['!', '?', '*', '-']
    for c in password:
        if not (
            (ord(c) >= ord('a') and ord(c) <= ord('z'))
            or (ord(c) >= ord('A') and ord(c) <= ord('Z'))
            or (ord(c) >= ord('0') and ord(c) <= ord('9'))
            or c in allowed_special_chars
            ):
                
                return 4 # bad charicter found
    
    return 0 # good password

def username_check(username):
    if len(username) < 3:
        return 5 # username is not long enough
    allowed_special_chars = ['!', '?', '_', '-']
    for c in username:
        if not (
            (ord(c) >= ord('a') and ord(c) <= ord('z'))
            or (ord(c) >= ord('A') and ord(c) <= ord('Z'))
            or (ord(c) >= ord('0') and ord(c) <= ord('9'))
            or c in allowed_special_chars
            ):
                
                return 2 # bad charicter found
    
    return 0 # good password
