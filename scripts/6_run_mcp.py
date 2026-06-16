from pathlib import Path

from config import CONFIG
from utils import compose_down, compose_up_tee, get_current_timestamp_formatted


def main():
    file_timestamp = get_current_timestamp_formatted()
    compose = (Path(CONFIG.PROJECT_DEPLOY_ABS_DIR.value)
               / CONFIG.PROJECT_DEPLOY_COMPOSE_MCP.value)
    logs_file = (Path(CONFIG.PROJECT_TARGET_BENCHMARK_ABS_DIR.value)
                / f"{file_timestamp}.log")
    print(f"Starting MCP with {str(compose)}...")
    try:
        compose_up_tee(compose, logs_file)
    finally:
        compose_down(compose)


if __name__ == '__main__':
    main()
