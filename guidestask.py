from urllib.parse import urljoin
from utils import hash_url, sanitize_filename
import os

def extract_pdf_links(soup, base_url):
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf") and "/documentation/guides/" in href:
            full_url = urljoin(base_url, href)
            links.append((full_url, href))
    return links

def save_pdf(content, output_dir, href):
    filename = sanitize_filename(href)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    return filename
