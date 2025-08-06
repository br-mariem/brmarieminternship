import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_page(url: str, timeout: int = 15) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, "html.parser")

def download_pdf(url: str, dest_path: str, timeout: int = 30) -> bool:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "").lower()
        if not content_type.startswith("application/pdf"):
            if not url.lower().endswith(".pdf"):
                return False
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        return True
    except Exception:
        return False

def make_absolute(base: str, href: str) -> str:
    return urljoin(base, href)
