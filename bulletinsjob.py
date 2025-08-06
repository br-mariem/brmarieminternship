import os
import requests
from utils import sanitize_filename, url_to_hash, load_existing_hashes, save_hashes

def download_bulletins(bulletins, folder_name="bulletins22", json_file="bulletin_hashes.json"):
    os.makedirs(folder_name, exist_ok=True)
    existing_hashes = load_existing_hashes(json_file)
    new_hashes = {}

    for bulletin in bulletins:
        url_hash = url_to_hash(bulletin["url"])
        if url_hash in existing_hashes:
            print(f"[!] Déjà existant (hash) : {bulletin['title']}")
            continue

        try:
            print(f" Téléchargement : {bulletin['title']}")
            response = requests.get(bulletin["url"], headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

            content_type = response.headers.get("Content-Type", "").lower()
            extension = ".pdf" if "pdf" in content_type else ".html"

            filename = sanitize_filename(f"{bulletin['date']} - {bulletin['title']}") + extension
            filepath = os.path.join(folder_name, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            new_hashes[url_hash] = True

        except Exception as e:
            print(f" Erreur lors du téléchargement de {bulletin['title']} : {e}")

    all_hashes = {**existing_hashes, **new_hashes}
    save_hashes(json_file, all_hashes)

    if new_hashes:
        print(f"\n {len(new_hashes)} nouveau(x) bulletin(s) téléchargé(s).")
    else:
        print(f"\n Aucun nouveau bulletin à télécharger.")

    print(f" Fichier JSON sauvegardé dans : {os.path.abspath(json_file)}")
