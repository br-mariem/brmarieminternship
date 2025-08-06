from job import run_scrape_job

def task_run(base_url, folder="avis23_pdf", json_file="avis23.json", gecko_path=None, headless=True):
    run_scrape_job(base_url, html_folder=folder, json_file=json_file, gecko_path=gecko_path, headless=headless)
