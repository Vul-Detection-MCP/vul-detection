# vul-detection

This repository stores experiments to verify possibilities finding software vulnerabilities
based on PrimeVul dataset.

## Prerequisites

1. Docker Compose.
2. `uv` build tool.
3. An available LLM, e.g., Ollama.

## Initialization

Run `init.sh`.

To change LLM host and port, adjust `.env`.

To add additional environment variables, please use `.env.additional`.

## Cleanup

Run `cleanup.sh`.

## Project Structure

### Persistent Folders

- `benchmark` - contains experiments. The intent is derived from name.
- `cmd` - scripts, e.g., to evaluate results and tool calls.
- `dataset-scripts` - reproduction of dataset that derives from PrimeVul. You should not
  run it, since it is for demonstration-only, since the updated dataset is already present
  in the repository.
- `deploy` - `compose-*.yaml` files to assist with services scaffold.
- `scripts` - dataset initialization.
- `src` - base source code.

The primary folder to work with is `scripts` and `benchmark`.

### Temporary Folders

During scripts execution `target` folder gets created with the following possible folders.

- `target/benchmark` - results on running benchmarks.

`*.log` contains MCP server (Codebadger) logs.

`*.csv` contains evaluation results to be parsed.

Folders store agent responses with regards to each dataset record to analyze. 

- `codebadger` - stores persistent `codebadger.db` storage Codebadger uses.

- `joern` - stores codebases and generated CPGs to assist code navigation.

- `metadata` - project metadata, i.e., list of all repositories, list of cloned repositories.

## Running The Experiments

### Scaffold

To start working with the project, run all `scripts/*` files. It initializes every step 
necessary. Then, it starts an MCP server in the end.

Note: to adjust amount of repositories, adjust `primevul_paired_service.find_all_exists()`
and `primevul_paired_service.find_all()` to get part of the array.

E.g. `primevul_paired_service.find_all_exists()[:100]` will make the project to work 
only with the first 100 records from the dataset.

All repositories to clone amount to ~200 GB.

### Benchmark

Benchmarks are represented by one file each. Simply run the file to start.

It might take a while (3h, 5h, 20h), especially when running on a lot of records (>50).

### Evaluation

- `python cmd/analyze_tool_calls.py target/benchmark/log-file.log` outputs amount of 
  called MCP tools.
- `python cmd/evaluate_results.py target/benchmark/csv-file.csv` outputs evaluation 
  metrics for a run.

## Datasets

- `primevul_test_paired_original.jsonl` - represents the original PrimeVul 0.1 test_paired, 
  as per https://github.com/DLVulDet/PrimeVul.
- `primevul_test_paired_original_sorted.jsonl` - represents the original PrimeVul 0.1,
  sorted by project size in increasing order to support faster runs on smaller
  amount of rows to check.
- `primevul_test_paired_updated.jsonl` - represents the modified PrimeVul 0.1,
  sorted, with updated commit IDs for vulnerable records.

Paired dataset is used to check if LLM is able to find subtle differences between benign
and vulnerable codebases.

The important distinction to have different commit IDs between vulnerable and benign
versions to check, since two commits might differ significantly.

`primevul_test_paired_updated.jsonl` is used by default. 
Please change `.env` to try other dataset variations.
