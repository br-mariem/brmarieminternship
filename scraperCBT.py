import os
import requests
import hashlib
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# === Config ===
OUTPUT_DIR = "notes_bct"
HASHES_FILE = "hashes_bct.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# === Get URL from user ===
BASE_PAGE = input("🔗 Entrez l'URL de la page des notes à télécharger : ").strip()
BASE_SITE = BASE_PAGE.rsplit('/', 1)[0] + '/'

# === Utilities ===
def hash_url(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def load_hashes():
    if os.path.exists(HASHES_FILE):
        with open(HASHES_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_hashes(hashes):
    with open(HASHES_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(hashes), f, indent=2)

def extract_year_from_filename(name):
    match = re.search(r'_(20[0-2][0-9])_', name)
    return match.group(1) if match else "unknown"

# === Setup ===
os.makedirs(OUTPUT_DIR, exist_ok=True)
existing_hashes = load_hashes()
new_hashes = set(existing_hashes)

# === Scrape page ===
resp = requests.get(BASE_PAGE, headers=HEADERS)
soup = BeautifulSoup(resp.content, 'html.parser')

# === Extract all <a> tags that link to .pdf in /documents/
all_links = soup.find_all("a", href=True)

for link in all_links:
    href = link["href"].strip()
    if not href.endswith(".pdf") or not "documents/" in href:
        continue

    full_url = urljoin(BASE_SITE, href)
    file_name = os.path.basename(href)
    year = extract_year_from_filename(file_name)
    year_dir = os.path.join(OUTPUT_DIR, year)
    os.makedirs(year_dir, exist_ok=True)
    file_path = os.path.join(year_dir, file_name)
    url_hash = hash_url(full_url)

    if url_hash in existing_hashes:
        print(f"[SKIP] {file_name} déjà téléchargé")
        continue

    print(f"[DOWNLOADING] {file_name} → {year}")
    try:
        r = requests.get(full_url, headers=HEADERS)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("application/pdf"):
            with open(file_path, 'wb') as f:
                f.write(r.content)
            new_hashes.add(url_hash)
        else:
            print(f"[ERREUR] Fichier non trouvé ou invalide : {full_url}")
    except Exception as e:
        print(f"[EXCEPTION] Erreur pour {full_url} → {e}")

# === Save hash list ===
save_hashes(new_hashes)
print("\n Terminé : tous les fichiers ont été traités.")


