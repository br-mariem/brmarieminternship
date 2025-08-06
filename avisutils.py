import os
import re
import json
import hashlib

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

def hash_url(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def load_hashes(json_path):
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data) if isinstance(data, list) else set()
        except Exception:
            return set()
    return set()

def save_hashes(hashes_set, json_path):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(hashes_set)), f, ensure_ascii=False, indent=2)
