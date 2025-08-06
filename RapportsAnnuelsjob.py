import os
from urllib.parse import urljoin
from api import fetch_page, extract_pdf_url_from_inner_page, download_pdf
from utils import hash_url, sanitize_filename, load_hashes, save_hashes

def run_download_job(base_url, output_dir="newrapports", json_path="newrapports.json"):
    os.makedirs(output_dir, exist_ok=True)
    existing_hashes = load_hashes(json_path)
    new_hashes = set()
    total_downloaded = 0

    try:
        print(f"[JOB] Démarrage de l'extraction depuis : {base_url}")
        html = fetch_page(base_url)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            href = link["href"]
            if "rapport-annuel" in href:
                full_page_url = urljoin(base_url, href)
                pdf_url = extract_pdf_url_from_inner_page(full_page_url)

                if pdf_url:
                    hashed = hash_url(pdf_url)
                    if hashed not in existing_hashes:
                        try:
                            pdf_content = download_pdf(pdf_url)
                            filename = sanitize_filename(link.text or os.path.basename(pdf_url))
                            if not filename.lower().endswith(".pdf"):
                                filename += ".pdf"
                            filepath = os.path.join(output_dir, filename)
                            with open(filepath, "wb") as f:
                                f.write(pdf_content)
                            print(f"[✓] Téléchargé : {pdf_url}")
                            new_hashes.add(hashed)
                            total_downloaded += 1
                        except Exception as e:
                            print(f"[!] Erreur de téléchargement {pdf_url} : {e}")
                    else:
                        print(f"[-] Déjà existant : {pdf_url}")

    except Exception as e:
        print(f"[!] Erreur lors du chargement de la page principale : {e}")

    if new_hashes:
        save_hashes(existing_hashes.union(new_hashes), json_path)
        print(f" {total_downloaded} fichiers téléchargés et sauvegardés dans '{output_dir}/'")
    else:
        print(" Aucun nouveau fichier à télécharger.")
