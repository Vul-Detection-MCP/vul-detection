from pathlib import Path

from config import CONFIG
from utils import compose_down, compose_up


def main():
    compose = (Path(CONFIG.PROJECT_DEPLOY_ABS_DIR.value)
               / CONFIG.PROJECT_DEPLOY_COMPOSE_DB_POPULATOR_FILE.value)
    print(f"Populating Codebadger database with {str(compose)}...")
    try:
        compose_up(compose)
    finally:
        compose_down(compose)

if __name__ == '__main__':
    main()
