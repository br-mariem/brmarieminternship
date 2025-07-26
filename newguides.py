import os
import requests
import hashlib
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

OUTPUT_DIR = "newguides"
HASH_FILE = "newguides.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def hash_url(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

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

def sanitize_filename(url):
    return os.path.basename(url).replace(" ", "_")

def main():
    page_url = input("🔗 Entrez l'URL de la page des guides du CMF : ").strip()
    if not page_url.startswith("http"):
        print("[❌] URL invalide.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    existing_hashes = load_hashes()
    new_hashes = set(existing_hashes)

    try:
        response = requests.get(page_url, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"[❌] Erreur de chargement de la page : {e}")
        return

    links = soup.find_all("a", href=True)
    total_found = 0
    for link in links:
        href = link["href"]
        if href.lower().endswith(".pdf") and "/documentation/guides/" in href:
            full_url = urljoin(page_url, href)
            url_hash = hash_url(full_url)

            if url_hash in existing_hashes:
                print(f"[SKIP] Déjà téléchargé : {full_url}")
                continue

            try:
                print(f"[DOWNLOAD] {full_url}")
                pdf_data = requests.get(full_url, headers=HEADERS).content
                filename = sanitize_filename(href)
                filepath = os.path.join(OUTPUT_DIR, filename)

                with open(filepath, "wb") as f:
                    f.write(pdf_data)

                new_hashes.add(url_hash)
                total_found += 1

            except Exception as e:
                print(f"[ERROR] Échec du téléchargement de {full_url}: {e}")

    save_hashes(new_hashes)
    print(f"\n [DONE] {total_found} nouveau(x) guide(s) téléchargé(s).")
    print(f" Dossier : '{OUTPUT_DIR}/' | Hashs : '{HASH_FILE}'")

if __name__ == "__main__":
    main()
