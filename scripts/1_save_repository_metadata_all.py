import csv
from pathlib import Path

from config import CONFIG
from service import primevul_paired_service
from utils import create_file


def main():
    target = (Path(CONFIG.PROJECT_METADATA_ABS_DIR.value)
              / CONFIG.PROJECT_METADATA_CSV_REPOSITORIES_ALL_FILE.value)
    create_file(str(target))

    all_records = primevul_paired_service.find_all()[:3]
    repositories = {
        (r.project_url, r.commit_id, r.extract_preferred_repository_name(), r.language)
        for r in all_records
    }
    with open(target, "w") as f:
        w = csv.writer(f)
        for repository in repositories:
            w.writerow(repository)

if __name__ == '__main__':
    main()
