import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import re
import json
import hashlib

HEADERS = {"User-Agent": "Mozilla/5.0"}

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

def extract_numero_bulletin(title):
    match = re.search(r"N°\s?(\d+)", title)
    return match.group(1) if match else "Inconnu"

def get_bulletins_from_page(page_url):
    response = requests.get(page_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(page_url))
    bulletins = []

    for row in soup.find_all('div', class_='views-row'):
        title_tag = row.select_one('div.field-item.even h2')
        link_tag = row.select_one('div.ds-3col-equal.node-teaser a')

        day_tag = row.select_one('div.field-name-field-jour div.field-item')
        month_tag = row.select_one('div.field-name-field-moisbulletin div.field-item')
        year_tag = row.select_one('div.field-name-field-ann-es div.field-item')

        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            link = urljoin(base_url, link_tag['href'])

            if day_tag and month_tag and year_tag:
                day = day_tag.get_text(strip=True)
                month = month_tag.get_text(strip=True)
                year = year_tag.get_text(strip=True)
                date = f"{day} {month} {year}"
            else:
                date = "Date inconnue"

            numero = extract_numero_bulletin(title)

            bulletins.append({
                "title": title,
                "url": link,
                "date": date,
                "numero": numero
            })

    return bulletins

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
            print(f"[↓] Téléchargement : {bulletin['title']}")
            response = requests.get(bulletin["url"], headers=HEADERS, timeout=10)

            content_type = response.headers.get("Content-Type", "").lower()
            extension = ".pdf" if "pdf" in content_type else ".html"

            filename = sanitize_filename(f"{bulletin['date']} - {bulletin['title']}") + extension
            filepath = os.path.join(folder_name, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            new_hashes[url_hash] = True

        except Exception as e:
            print(f"[!] Erreur lors du téléchargement de {bulletin['title']} : {e}")

    # ✅ Always update the JSON file
    all_hashes = {**existing_hashes, **new_hashes}
    save_hashes(json_file, all_hashes)

    if new_hashes:
        print(f"\n✅ {len(new_hashes)} nouveau(x) bulletin(s) téléchargé(s).")
    else:
        print(f"\nℹ️ Aucun nouveau bulletin à télécharger.")

    print(f"📁 Fichier JSON sauvegardé dans : {os.path.abspath(json_file)}")

def scrape_all_pages(base_url):
    all_bulletins = []
    page = 0

    while True:
        paged_url = f"{base_url}&page={page}" if "?" in base_url else f"{base_url}?page={page}"
        print(f"\n📄 Lecture de la page {page} : {paged_url}")
        bulletins = get_bulletins_from_page(paged_url)

        if not bulletins:
            print("🛑 Fin de la pagination.")
            break

        all_bulletins.extend(bulletins)
        page += 1

    return all_bulletins

if __name__ == "__main__":
    print("📂 Dossier de travail courant :", os.getcwd())
    main_url = input("🔗 Entrez l'URL de la page des bulletins officiels : ").strip()
    bulletins = scrape_all_pages(main_url)
    print(f"\n📊 Total de bulletins trouvés : {len(bulletins)}")
    download_bulletins(bulletins)



