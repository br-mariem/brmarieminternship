import schedule
import time
from job import run_download_job

GUIDE_URL = "https://www.cmf.tn/?q=guides"


def job():
    print("\n[ Tâche lancée maintenant]")
    run_download_job(GUIDE_URL)


def main():
    print("🔁Le script a démarré, en attente des tâches...")

    schedule.every().day.at("10:00").do(job)

    job()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
