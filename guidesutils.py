import os
import hashlib
import json

HASH_FILE = "newguides.json"

def hash_url(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def sanitize_filename(url):
    return os.path.basename(url).replace(" ", "_")

def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return set(item if isinstance(item, str) else item["hash"] for item in data)
            except Exception as e:
                print(f"[ERROR] Erreur de lecture de {HASH_FILE} : {e}")
    return set()

def save_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(list(hashes), f, indent=2)
