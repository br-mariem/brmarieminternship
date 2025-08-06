import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_page(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.text

def get_bulletins_from_page(page_url):
    html = fetch_page(page_url)
    soup = BeautifulSoup(html, "html.parser")
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

            bulletins.append({
                "title": title,
                "url": link,
                "date": date
            })

    return bulletins
