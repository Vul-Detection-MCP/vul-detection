# Since not all repositories might be fetched, filter is applied
import csv
from pathlib import Path

from config import CONFIG
from service import primevul_paired_service
from utils import create_file


def main():
    target = (Path(CONFIG.PROJECT_METADATA_ABS_DIR.value)
              / CONFIG.PROJECT_METADATA_CSV_REPOSITORIES_CLONED_FILE.value)
    create_file(target)

    exists = primevul_paired_service.find_all_exists()
    repositories = {
        (str(r.project_url), r.commit_id, r.extract_preferred_repository_name(), r.language)
        for r in exists
    }
    with open(target, "w") as f:
        w = csv.writer(f)
        for repository in repositories:
            w.writerow(repository)


if __name__ == '__main__':
    main()
