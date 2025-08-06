import os
from api import find_pdf_link_on_page, download_pdf
from utils import sanitize_filename, hash_url, load_hashes, save_hashes
from api import HEADERS

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def create_driver(headless=True, gecko_path=None):
    opts = Options()
    if headless:
        opts.add_argument("--headless")
    if gecko_path:
        driver = webdriver.Firefox(executable_path=gecko_path, options=opts)
    else:
        driver = webdriver.Firefox(options=opts)
    return driver

def run_scrape_job(base_url, html_folder="avis23_pdf", json_file="avis23.json", gecko_path=None, headless=True):
    os.makedirs(html_folder, exist_ok=True)
    existing_hashes = load_hashes(json_file)
    driver = create_driver(headless=headless, gecko_path=gecko_path)

    page = 0
    total_new = 0
    try:
        while True:
            paged = f"{base_url}&page={page}" if "?" in base_url else f"{base_url}?page={page}"
            print(f"\n Lecture de la page {page} : {paged}")

            comms = []
            try:
                from selenium.webdriver.common.by import By
                driver.get(paged)
                driver.implicitly_wait(3)
                rows = driver.find_elements(By.CSS_SELECTOR, "div.views-row")
                for it in rows:
                    try:
                        date_el = it.find_element(By.CSS_SELECTOR, "div.group-left span.date-display-single")
                        a_el = it.find_element(By.CSS_SELECTOR, "div.group-right h2 a")
                        title = a_el.text.strip()
                        date = date_el.text.strip()
                        link = a_el.get_attribute("href")
                        comms.append((title, date, link))
                    except Exception:
                        continue
            except Exception as e:
                print(f" Erreur lecture page {paged} : {e}")
                comms = []

            if not comms:
                print(" Fin de pagination (ou aucune entrée sur la page).")
                break

            new_hashes = set()
            for title, date, link in comms:
                url_hash = hash_url(link)
                if url_hash in existing_hashes or url_hash in new_hashes:
                    print(f" Déjà traité : {title}")
                    continue

                if link.lower().endswith(".pdf"):
                    pdf_url = link
                else:
                    pdf_url = find_pdf_link_on_page(driver, link)
                    if not pdf_url:
                        print(f" Aucun lien PDF trouvé sur la page interne : {link} — on skip.")
                        continue

                filename_base = sanitize_filename(f"{date} - {title}")
                if not filename_base.lower().endswith(".pdf"):
                    filename = filename_base + ".pdf"
                else:
                    filename = filename_base

                filepath = os.path.join(html_folder, filename)
                print(f" Téléchargement PDF : {pdf_url}")
                ok, err = download_pdf(pdf_url, filepath)
                if ok:
                    print(f" PDF sauvegardé : {filepath}")
                    new_hashes.add(url_hash)
                    total_new += 1
                else:
                    print(f" Échec téléchargement {pdf_url} : {err}")

            if new_hashes:
                existing_hashes.update(new_hashes)
                save_hashes(existing_hashes, json_file)
                print(f" {len(new_hashes)} nouvel(le)(s) communiqué(s) sauvegardé(s) — JSON mis à jour.")
            else:
                print(" Aucun nouveau communiqué téléchargé sur cette page.")

            page += 1

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    print(f"\n Fin du job. Total nouveaux PDF téléchargés : {total_new}")
