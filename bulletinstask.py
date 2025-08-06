from api import get_bulletins_from_page
from job import download_bulletins

def task_run(base_url):
    print(f"\n[Task] Récupération des bulletins depuis : {base_url}")
    all_bulletins = []
    page = 0

    while True:
        paged_url = f"{base_url}&page={page}" if "?" in base_url else f"{base_url}?page={page}"
        print(f"\n Lecture de la page {page} : {paged_url}")
        bulletins = get_bulletins_from_page(paged_url)

        if not bulletins:
            print(" Fin de la pagination.")
            break

        all_bulletins.extend(bulletins)
        page += 1

    print(f"\n Total de bulletins trouvés : {len(all_bulletins)}")
    download_bulletins(all_bulletins)
