import os
import re
import json
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Configurations
METADATA_FILE = "avis23.json"
HTML_FOLDER = "avis23_html"

# Init driver headless
opts = Options()
opts.add_argument("--headless")
driver = webdriver.Firefox(options=opts)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

def load_hashes():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_hashes(hashes):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(hashes), f, ensure_ascii=False, indent=2)

def hash_url(url):
    import hashlib
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def download_html_from_url(url, output_path):
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        html = driver.page_source
        if len(html.strip()) < 200:
            print(f"[!] Page vide ou peu de contenu : {url}")
            return False

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[+] HTML sauvegardé : {output_path}")
        return True
    except TimeoutException:
        print(f"[!] Timeout Selenium sur {url}")
        return False
    except Exception as e:
        print(f"[!] Erreur téléchargement HTML {url} : {e}")
        return False

def download_communiques(comms, existing_hashes, folder=HTML_FOLDER):
    os.makedirs(folder, exist_ok=True)
    new_hashes = set()

    for title, date, url in comms:
        h = hash_url(url)
        if h in existing_hashes or h in new_hashes:
            print(f"[!] URL déjà traitée, ignorée : {url}")
            continue

        filename = sanitize_filename(f"{date} - {title}") + ".html"
        fp = os.path.join(folder, filename)
        success = download_html_from_url(url, fp)

        if success:
            new_hashes.add(h)
        else:
            print(f"[!] Échec téléchargement pour {url} — hash non ajouté")

    return new_hashes

def get_communiques_from_page(url, timeout=10):
    driver.get(url)
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.views-row"))
        )
    except TimeoutException:
        print(f"[!] Timeout sur la page {url}")
        return []

    comms = []
    for it in driver.find_elements(By.CSS_SELECTOR, "div.views-row"):
        try:
            d = it.find_element(By.CSS_SELECTOR, "div.group-left span.date-display-single").text.strip()
            a = it.find_element(By.CSS_SELECTOR, "div.group-right h2 a")
            comms.append((a.text.strip(), d, a.get_attribute("href")))
        except NoSuchElementException:
            continue

    print(f"Nombre d'avis extraits : {len(comms)}")
    return comms

def scrape_all_pages(base):
    existing_hashes = load_hashes()
    page = 0
    while True:
        url = f"{base}&page={page}" if "?" in base else f"{base}?page={page}"
        print(f"➡️ Lecture de la page {page} : {url}")
        comms = get_communiques_from_page(url)
        if not comms:
            print("✅ Fin de pagination")
            break

        new_hashes = download_communiques(comms, existing_hashes)
        if new_hashes:
            existing_hashes.update(new_hashes)
            save_hashes(existing_hashes)
        else:
            print("📦 Aucun nouveau communiqué téléchargé sur cette page")

        page += 1

    driver.quit()

if __name__ == "__main__":
    scrape_all_pages("https://www.cmf.tn/?q=avis-et-d-cisions-du-cmf")

