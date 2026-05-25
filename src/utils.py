import os
from pathlib import Path


def create_folder(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def create_file(path: str):
    create_folder(path)
    open(path, "w").close()


def compose_up(target: Path):
    os.system(f"docker compose --file {str(target)} up --build --remove-orphans --force-recreate")


def compose_down(target: Path):
    os.system(f"docker compose --file {str(target)} down")
