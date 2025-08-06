# api.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def find_pdf_link_on_page(driver, page_url, wait_selector="body", timeout=10):

    try:
        driver.get(page_url)
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
    except Exception:

        pass

    try:
        anchors = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
        if anchors:
            href = anchors[0].get_attribute("href")
            return urljoin(page_url, href)
    except Exception:
        pass

    try:
        anchors = driver.find_elements(By.TAG_NAME, "a")
        for a in anchors:
            href = a.get_attribute("href")
            if href and href.lower().endswith(".pdf"):
                return urljoin(page_url, href)
    except Exception:
        pass

    return None

def download_pdf(pdf_url, output_path, timeout=30):

    try:
        resp = requests.get(pdf_url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return True, None
    except Exception as e:
        return False, str(e)
