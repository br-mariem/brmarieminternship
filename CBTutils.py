import os
import re
import json
import hashlib

HASHES_FILE = "hashes_bct.json"
OUTPUT_DIR = "notes_bct"

def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def load_hashes(path: str = HASHES_FILE) -> set:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return set(data) if isinstance(data, list) else set()
            except Exception:
                return set()
    return set()

def save_hashes(path: str, hashes: set) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(hashes)), f, ensure_ascii=False, indent=2)

def create_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def extract_year_from_filename(name: str) -> str:
    match = re.search(r'_(20[0-2][0-9])_', name)
    return match.group(1) if match else "unknown"
