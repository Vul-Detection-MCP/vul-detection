import csv
import json
from pathlib import Path
from typing import TypeVar

from config import CONFIG
from src.entity.vulnerability_record_test_paired import \
    VulnerabilityRecordTestPaired
from src.service.primevul_paired_service import find_all
from src.utils import load_jsonl

T = TypeVar("T")


def load_repo_sizes(path: Path) -> dict[str, int]:
    with open(path, "r") as f:
        return {row[0]: int(row[1]) for row in csv.reader(f)}


def create_pairs(arr: list[T]) -> list[tuple[T, T]]:
    return [(arr[i], arr[i + 1]) for i in range(0, len(arr), 2)]


def find_size(pair: tuple[VulnerabilityRecordTestPaired, VulnerabilityRecordTestPaired],
              size_map: dict[str, int]) -> int:
    # Original commit ID is in the right value (index 1)
    preferred_hash = pair[1].extract_preferred_repository_name()
    value = size_map.get(preferred_hash)
    if value is None:
        return 9999999
    return value


def find_index(pair: tuple[dict, dict], records: list[VulnerabilityRecordTestPaired]) -> int:
    key = pair[1]["project_url"] + pair[1]["commit_id"]

    for (idx, record) in enumerate(records):
        current = str(record.project_url) + record.commit_id
        if current == key:
            return idx

    raise BaseException


def is_alternating(seq):
    targets = [int(i["target"]) for i in seq]
    return all(x == (i + 1) % 2 for i, x in enumerate(targets))


def flatten(items: list[tuple[T, T]]) -> list[T]:
    return [item for pair in items for item in pair]


if __name__ == '__main__':
    target = (Path(CONFIG.PROJECT_ASSETS_ABS_DIR.value)
              / CONFIG.PROJECT_ASSETS_PRIMEVUL_TEST_UPDATED_PAIRED_FILE.value)
    repo_sizes_path = (Path(CONFIG.PROJECT_METADATA_ABS_DIR.value)
                       / CONFIG.PROJECT_METADATA_CSV_REPOSITORIES_SIZE_BYTES_FILE.value)
    size_map = load_repo_sizes(repo_sizes_path)

    all_records = find_all()
    paired_records = create_pairs(all_records)
    pairs_records_sorted = sorted(paired_records, key=lambda x: find_size(x, size_map))
    flat_records_sorted = flatten(pairs_records_sorted)

    dataset_rows = load_jsonl(str(target))
    paired_dataset_rows = create_pairs(dataset_rows)
    paired_dataset_rows_sorted = sorted(paired_dataset_rows, key=lambda x: find_index(x, flat_records_sorted))
    flat_dataset_rows_sorted = flatten(paired_dataset_rows_sorted)

    for pair in pairs_records_sorted[:20]:
        print(
            pair[1].extract_preferred_repository_name(),
            find_size(pair, size_map)
        )

    if not is_alternating(flat_dataset_rows_sorted):
        raise BaseException("wrong sorting")

    with open(target, 'w') as outfile:
        for entry in flat_dataset_rows_sorted:
            json.dump(entry, outfile)
            outfile.write('\n')
