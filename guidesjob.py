import os
from api import fetch_page, download_pdf
from task import extract_pdf_links, save_pdf
from utils import load_hashes, save_hashes, hash_url

OUTPUT_DIR = "newguides"

def run_download_job(url):
    print(f"[JOB] Démarrage de l'extraction depuis : {url}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    soup = fetch_page(url)
    links = extract_pdf_links(soup, url)

    existing_hashes = load_hashes()
    new_hashes = set(existing_hashes)

    total_found = 0
    for full_url, href in links:
        url_hash = hash_url(full_url)
        if url_hash in existing_hashes:
            print(f"[SKIP] Déjà téléchargé : {full_url}")
            continue

        try:
            print(f"[DOWNLOAD] {full_url}")
            content = download_pdf(full_url)
            save_pdf(content, OUTPUT_DIR, href)
            new_hashes.add(url_hash)
            total_found += 1
        except Exception as e:
            print(f"[ERROR] Échec du téléchargement : {e}")

    save_hashes(new_hashes)
    print(f"[DONE] {total_found} nouveau(x) guide(s) téléchargé(s).")
