import os
import json
import hashlib
import re

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

def url_to_hash(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def load_existing_hashes(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_hashes(json_path, hashes_dict):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(hashes_dict, f, indent=4, ensure_ascii=False)
