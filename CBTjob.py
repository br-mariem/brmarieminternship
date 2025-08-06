import os
from api import fetch_page, download_pdf, make_absolute
from utils import (
    OUTPUT_DIR,
    HASHES_FILE,
    hash_url,
    load_hashes,
    save_hashes,
    create_directory,
    extract_year_from_filename,
)

def run_job(base_page: str, output_dir: str = OUTPUT_DIR, hashes_file: str = HASHES_FILE) -> None:
    create_directory(output_dir)
    existing_hashes = load_hashes(hashes_file)
    processed_hashes = set(existing_hashes)

    try:
        soup = fetch_page(base_page)
    except Exception as e:
        print(f"[ERREUR] Impossible de charger la page : {e}")
        return
    base_site = base_page.rsplit("/", 1)[0] + "/"

    links = soup.find_all("a", href=True)
    total_new = 0

    for link in links:
        href_raw = link["href"].strip()
        if not href_raw.lower().endswith(".pdf") or "documents/" not in href_raw:
            continue

        full_url = make_absolute(base_site, href_raw)
        file_name = os.path.basename(href_raw)
        year = extract_year_from_filename(file_name)
        year_dir = os.path.join(output_dir, year)
        create_directory(year_dir)
        file_path = os.path.join(year_dir, file_name)

        url_hash = hash_url(full_url)
        if url_hash in processed_hashes:
            print(f"[SKIP] {file_name} déjà téléchargé")
            continue

        print(f"[DOWNLOADING] {file_name} → {year}")
        ok = download_pdf(full_url, file_path)
        if ok:
            processed_hashes.add(url_hash)
            total_new += 1
        else:
            print(f"[ERROR] Échec téléchargement ou fichier non-PDF : {full_url}")

    if processed_hashes:
        save_hashes(hashes_file, processed_hashes)

    print(f"\nTerminé : {total_new} nouveau(x) fichier(s) téléchargé(s).")
