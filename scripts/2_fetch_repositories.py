from pathlib import Path

import utils
from config import CONFIG


def main():
    print("Fetching Git repositories at specific commits...")
    compose = (Path(CONFIG.PROJECT_DEPLOY_ABS_DIR.value)
               / CONFIG.PROJECT_DEPLOY_COMPOSE_GIT_CLONE_FILE.value)
    try:
        utils.compose_up(compose)
    finally:
        utils.compose_down(compose)

if __name__ == "__main__":
    main()
