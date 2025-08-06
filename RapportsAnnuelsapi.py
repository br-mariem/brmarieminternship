import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_page(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text

def extract_pdf_url_from_inner_page(inner_url):
    try:
        html = fetch_page(inner_url)
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.lower().endswith(".pdf"):
                return urljoin(inner_url, href)
    except Exception as e:
        print(f" Erreur lors de l'extraction depuis {inner_url}: {e}")
    return None

def download_pdf(pdf_url):
    response = requests.get(pdf_url, headers=HEADERS)
    response.raise_for_status()
    return response.content
