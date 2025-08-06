from job import run_job

def task_run(base_page: str, output_dir: str = None, hashes_file: str = None):
    if output_dir is None and hashes_file is None:
        run_job(base_page)
    elif hashes_file is None:
        run_job(base_page, output_dir=output_dir)
    else:
        run_job(base_page, output_dir=output_dir, hashes_file=hashes_file)
