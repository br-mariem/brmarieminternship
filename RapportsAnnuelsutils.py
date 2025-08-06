import os
import json
import hashlib

def hash_url(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def sanitize_filename(name):
    return "".join(c if c.isalnum() or c in (' ', '_', '-') else "_" for c in name).strip().replace(" ", "_")

def load_hashes(json_path):
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_hashes(hashes, json_path):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(list(hashes), f, indent=2, ensure_ascii=False)
