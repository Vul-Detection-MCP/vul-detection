from pathlib import Path

from config import CONFIG
from utils import compose_down, compose_up


def main():
    compose = (Path(CONFIG.PROJECT_DEPLOY_ABS_DIR.value)
               / CONFIG.PROJECT_DEPLOY_COMPOSE_JOERN_CPG_INITIALIZER_FILE.value)
    print(f"Initializing Joern's CPG with {str(compose)}...")
    print("It make take a while. Please stand by...")
    try:
        compose_up(compose)
    finally:
        compose_down(compose)

if __name__ == '__main__':
    main()
