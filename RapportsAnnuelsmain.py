# main.py
import schedule
import time
from task import task_run

def main():
    base_url = input(" Entrer l'URL de la page des rapports annuels : ").strip()

    schedule.every().day.at("10:00").do(task_run, base_url)

    print(" Planification : tous les jours à 10:00")
    print(" Exécution immédiate pour test")
    task_run(base_url)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
