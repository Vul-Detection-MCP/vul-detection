import datetime
import json
import os
import time
from pathlib import Path

from tqdm import tqdm


def create_tqdm(total):
    return tqdm(
        total=total,
        bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed} < {remaining}, {rate_fmt}]"
    )


def load_jsonl(path: str):
    with open(path) as f:
        return [json.loads(line) for line in f]


def save_jsonl(dicts: list[dict], path: Path):
    with open(path, 'w') as f:
        for d in dicts:
            json.dump(d, f)
            f.write("\n")


def get_current_timestamp_formatted():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d%H-%M-%S')


def create_folder(path: Path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def create_file(path: Path):
    create_folder(path)
    open(path, "w").close()


def compose_up(target: Path):
    os.system(f"docker compose --file {str(target)} up --build --remove-orphans --force-recreate")


def compose_down(target: Path):
    os.system(f"docker compose --file {str(target)} down")
