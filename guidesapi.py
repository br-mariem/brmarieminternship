import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_page(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")

def download_pdf(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.content
