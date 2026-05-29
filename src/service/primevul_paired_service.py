import os
from pathlib import Path
from typing import List

from config import CONFIG
from entity.vulnerability_record_test_paired import \
    VulnerabilityRecordTestPaired
from utils import load_jsonl


def exists(record: VulnerabilityRecordTestPaired):
    target = (Path(CONFIG.PROJECT_TARGET_JOERN_ABS_DIR.value)
              / CONFIG.PROJECT_TARGET_JOERN_CODEBASES_DIR.value /
              record.extract_preferred_repository_name())
    return os.path.isdir(target)


def find_all_exists_original() -> List[VulnerabilityRecordTestPaired]:
    all_records = find_all_original()
    return [r for r in all_records if exists(r)]


def find_all_original() -> List[VulnerabilityRecordTestPaired]:
    original_dataset = (Path(CONFIG.PROJECT_ASSETS_ABS_DIR.value)
                        / CONFIG.PROJECT_ASSETS_PRIMEVUL_TEST_ORIGINAL_PAIRED_FILE.value)
    return find_all_path(original_dataset)


def find_all_exists() -> List[VulnerabilityRecordTestPaired]:
    all_records = find_all()
    return [r for r in all_records if exists(r)]


def find_all() -> List[VulnerabilityRecordTestPaired]:
    updated_dataset = (Path(CONFIG.PROJECT_ASSETS_ABS_DIR.value)
                       / CONFIG.PROJECT_ASSETS_PRIMEVUL_TEST_UPDATED_PAIRED_FILE.value)
    return find_all_path(updated_dataset)


def find_all_path(target: Path) -> List[VulnerabilityRecordTestPaired]:
    json_records = load_jsonl(str(target))
    total = []
    for json_record in json_records:
        record = VulnerabilityRecordTestPaired(**json_record)

        if record.file_name is None:
            # C++ handles more cases
            record.language = "cpp"
        else:
            got = record.file_name.split(".")[-1]
            if got == "c":
                record.language = "c"
        total.append(record)

    return total


if __name__ == "__main__":
    loaded = find_all()
    print("")
