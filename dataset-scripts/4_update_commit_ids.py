import json
import subprocess
from pathlib import Path

from config import CONFIG
from src.entity.vulnerability_record_test_paired import \
    VulnerabilityRecordTestPaired
from src.service.primevul_paired_service import find_all_exists_original
from src.utils import load_jsonl


def exists(row: dict, records: list[VulnerabilityRecordTestPaired]) -> int:
    target = row["project_url"] + row["commit_id"]
    for record in records:
        if str(record.project_url) + record.commit_id == target:
            return True

    return False

def get_matching(row: dict, records: list[VulnerabilityRecordTestPaired]) -> VulnerabilityRecordTestPaired:
    target = row["project_url"] + row["commit_id"]
    for record in records:
        if str(record.project_url) + record.commit_id == target:
            return record

    raise BaseException

def extract_parent_commit(given: Path) -> str:
    result = subprocess.check_output(
        ["git", "rev-parse", "HEAD^"],
        cwd=given,
        text=True
    )

    return result.strip()


def main():
    source = (Path(CONFIG.PROJECT_ASSETS_ABS_DIR.value)
              / CONFIG.PROJECT_ASSETS_PRIMEVUL_TEST_ORIGINAL_PAIRED_FILE.value)
    target = (Path(CONFIG.PROJECT_ASSETS_ABS_DIR.value)
              / CONFIG.PROJECT_ASSETS_PRIMEVUL_TEST_UPDATED_PAIRED_FILE.value)
    base_codebases_path = (Path(CONFIG.PROJECT_TARGET_JOERN_ABS_DIR.value)
                           / CONFIG.PROJECT_TARGET_JOERN_CODEBASES_DIR.value)

    existing_records = find_all_exists_original()
    all_rows = load_jsonl(str(source))
    existing_rows = [i for i in all_rows if exists(i, existing_records)]
    # Update commit ID of vulnerable records (target=1) with actually vulnerable commits
    for i in range(0, len(existing_rows), 2):
        matching_record = get_matching(existing_rows[i], existing_records)
        codebase_hash = matching_record.extract_preferred_repository_name()
        try:
            existing_rows[i]["commit_id"] = extract_parent_commit(base_codebases_path / codebase_hash)
        except:
            print(codebase_hash)

    with open(target, 'w') as outfile:
        for entry in existing_rows:
            json.dump(entry, outfile)
            outfile.write('\n')

if __name__ == '__main__':
    main()
