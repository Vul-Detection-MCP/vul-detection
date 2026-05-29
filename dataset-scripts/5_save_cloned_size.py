import csv
import os
from pathlib import Path

from config import CONFIG


def get_size(start_path: str):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def export_folder_sizes(parent_folder, output_csv):
    rows = []

    for entry in os.scandir(parent_folder):
        if entry.is_dir():
            size_bytes = get_size(entry.path)
            rows.append([entry.name, size_bytes])

    rows.sort(key=lambda x: x[1], reverse=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

    print(f"Saved {len(rows)} folder records to {output_csv}")


if __name__ == "__main__":
    parent_folder = (Path(CONFIG.PROJECT_TARGET_JOERN_ABS_DIR.value)
                     / CONFIG.PROJECT_TARGET_JOERN_CODEBASES_DIR.value)
    output_csv = (Path(CONFIG.PROJECT_METADATA_ABS_DIR.value)
                  / CONFIG.PROJECT_METADATA_CSV_REPOSITORIES_SIZE_BYTES_FILE.value)

    export_folder_sizes(parent_folder, output_csv)
