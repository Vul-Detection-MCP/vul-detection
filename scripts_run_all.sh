#!/bin/sh
source .venv/bin/activate
export PYTHONPATH=.
python scripts/1_save_repository_metadata_all.py && \
  python scripts/2_fetch_repositories.py && \
  python scripts/3_save_repository_metadata_of_cloned.py && \
  python scripts/4_codebadger_db_populate.py && \
  python scripts/5_joern_cpg_initialize.py
