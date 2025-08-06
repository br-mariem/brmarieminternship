import schedule
import time
from task import task_run

def main():
    base_url = input(" Entrez l'URL de la page des avis : ").strip()
    gecko_path = None

    schedule.every().day.at("10:00").do(task_run, base_url, "avis23_pdf", "avis23.json", gecko_path, True)

    print(" Planification : tous les jours à 10:00")
    print(" Exécution immédiate pour test")
    task_run(base_url, "avis23_pdf", "avis23.json", gecko_path, True)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
