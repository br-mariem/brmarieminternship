import os
import requests
import hashlib
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}

def hash_url(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

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

def extract_pdf_url_from_inner_page(inner_url):
    try:
        response = requests.get(inner_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.lower().endswith(".pdf"):
                return urljoin(inner_url, href)
    except Exception as e:
        print(f"[!] Erreur lors de l'extraction depuis {inner_url}: {e}")
    return None

def main():
    base_url = input("🔗 Entrer l'URL de la page des rapports annuels : ").strip()
    output_dir = "newrapports"
    json_path = "newrapports.json"

    os.makedirs(output_dir, exist_ok=True)
    existing_hashes = load_hashes(json_path)
    new_hashes = set()

    try:
        print("[...] Chargement de la page des rapports annuels")
        response = requests.get(base_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.find_all("a", href=True)
        total_downloaded = 0

        for link in links:
            href = link["href"]
            if "rapport-annuel" in href:
                full_page_url = urljoin(base_url, href)
                pdf_url = extract_pdf_url_from_inner_page(full_page_url)

                if pdf_url:
                    hashed = hash_url(pdf_url)
                    if hashed not in existing_hashes:
                        try:
                            pdf_response = requests.get(pdf_url, headers=HEADERS)
                            pdf_response.raise_for_status()

                            filename = sanitize_filename(link.text or os.path.basename(pdf_url))
                            if not filename.lower().endswith(".pdf"):
                                filename += ".pdf"

                            filepath = os.path.join(output_dir, filename)
                            with open(filepath, "wb") as f:
                                f.write(pdf_response.content)
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
        print(f"[✔] {total_downloaded} fichiers téléchargés et sauvegardés dans '{output_dir}/'")
    else:
        print("[i] Aucun nouveau fichier à télécharger.")

if __name__ == "__main__":
    main()
