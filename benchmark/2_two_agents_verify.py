import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain.agents import create_agent

from config import CONFIG
from src.entity.vulnerability_record_test_paired import \
    VulnerabilityRecordTestPaired
from src.service.evaluation_service import convert_response_bool_to_int
from src.service.llm_service import create_ollama, create_tools
from src.service.primevul_paired_service import find_all_exists
from src.utils import create_file, create_tqdm, get_current_timestamp_formatted
from utils import create_folder

MODEL = "qwen3.6:27b-q8_0"


# MODEL = "gpt-5.5"

@dataclass
class Response:
    is_vulnerable: bool


async def prompt_research(agent, v: VulnerabilityRecordTestPaired) -> dict[str, Any] | Any:
    return await agent.ainvoke(
        {
            "description": "Comprehensive security audit — maps attack surface and discovers vulnerabilities across a codebase.",
            "messages": [
                {
                    "role": "system",
                    "content": 'You are performing a comprehensive security audit on a project.\n\n\n## Confidence & False-Positive Policy\n\nCodeBadger\'s detectors assign a **Confidence** level (HIGH / MEDIUM) to each finding based on:\n- Flow type (direct dereference vs passed-to-function, same-pointer vs alias, intraprocedural vs interprocedural)\n- Reachability from external input (BFS depth 10 over call graph)\n\n**Use the tool\'s confidence levels to structure your report:**\n- **HIGH confidence** findings: Report as confirmed vulnerabilities in the main findings section. These have direct evidence (e.g., same-function usage, confirmed dataflow, direct dereference) or are reachable from external input.\n- **MEDIUM confidence** findings: Include in a "Needs Manual Review" section with explanation of why they are uncertain (e.g., alias-based, passed-to-function without confirmed dereference, not reachable from external input).\n- After gathering tool results, critically evaluate each finding — cross-reference with at least two signals (e.g., confirmed taint flow + dangerous sink without sanitization, or CFG shows reachable path + no bounds check).\n- Discard findings that are likely false positives: dead code paths, safely wrapped calls, test-only code, or sinks that are unreachable from external input.\n- Never pad the report with low-confidence noise. A short report with 3 real findings is far more valuable than a long report with 20 speculative ones.\n\nEach finding also includes **validation context** (function signature, callers, reachability from external input) to help you write targeted PoC triggers and assess exploitability.\n\nFollow this systematic workflow:\n\n## Phase 1: Reconnaissance\n1. Call `get_codebase_summary(codebase_hash="<retrieved hash>")` to understand scope (language, files, methods, calls)\n2. Call `list_source_files(codebase_hash="<retrieved hash>")` to understand the project structure\n3. Call `discover_fixed_vulnerabilities(codebase_hash="<retrieved hash>")` to find historical vulnerability hints from git history\n\n## Phase 2: Attack Surface Mapping\n4. Call `find_taint_sources(codebase_hash="<retrieved hash>")` to enumerate all external input points\n5. Call `find_taint_sinks(codebase_hash="<retrieved hash>")` to enumerate all dangerous operations\n\n## Phase 3: Automated Taint Analysis\n6. Call `find_taint_flows(codebase_hash="<retrieved hash>", mode="auto")` to discover all confirmed source-to-sink data flows\n\n\n## Phase 3b: Memory Safety (if C/C++)\nIf the codebase language is C or C++, also run:\n7. `find_use_after_free(codebase_hash="<retrieved hash>")` — detect use-after-free vulnerabilities\n8. `find_double_free(codebase_hash="<retrieved hash>")` — detect double-free vulnerabilities\n9. `find_bounds_checks(codebase_hash="<retrieved hash>")` — find buffer accesses missing bounds checks\n10. `find_null_pointer_deref(codebase_hash="<retrieved hash>")` — detect null pointer dereference vulnerabilities (CWE-476)\n11. `find_integer_overflow(codebase_hash="<retrieved hash>")` — detect integer overflow/underflow before allocation or array indexing (CWE-190)\n12. `find_toctou(codebase_hash="<retrieved hash>")` — detect TOCTOU race conditions (CWE-367) where access()/stat() is followed by open() on the same path\n\n## Phase 4: Deep Investigation\nFor each confirmed vulnerability or taint flow:\n- Call `get_file_content(codebase_hash="<retrieved hash>", method_name="<vulnerable_function>")` to view the full source\n- Call `get_program_slice(codebase_hash="<retrieved hash>", ...)` to trace data origins backward\n- Call `get_variable_flow(codebase_hash="<retrieved hash>", ...)` for specific variable tracking\n\n## Phase 5: Report\nProduce a structured security audit report with:\n- **Executive Summary**: Overall risk level and key findings count\n- **Findings Table**: Each vulnerability with severity (Critical/High/Medium/Low), CWE ID, affected file:line, and description\n- **Detailed Findings**: For each finding — vulnerable code snippet, data flow path, exploitability assessment, and remediation recommendation\n- **Attack Surface Summary**: Count of input points, dangerous sinks, and confirmed flow paths',
                },
                {
                    "role": "user",
                    "content": f"Find if function {v.func} in file {v.file_name} in codebase {v.extract_preferred_repository_name()} is vulnerable.",
                },
                {
                    "role": "assistant",
                    "content": "I'll perform a systematic security audit following the phased workflow. Let me start with codebase summary in step 1.",
                },
            ],
        }
    )

async def prompt_verify(agent, user_content):
    return await agent.ainvoke(
        {
            "description": "You are a binary classifier of software vulnerability reports (vulnerable, not vulnerable). You output only boolean expressions (true, false).",
            "messages": [
                {
                    "role": "system",
                    "content": "Return:\n- true = the text asserts the existence of a problem, vulnerability, defect, risk, error, failure, weakness, or negative condition (severity medium or higher).\n- false = the text does not assert such a condition, is a denial, uncertainty, or lacks a clear conclusion (severity low or none).\n"
                },
                {
                    "role": "user",
                    "content": user_content,
                },
                {
                    "role": "assistant",
                    "content": '"This function is extremely vulnerable. Severity: HIGH." -> true\n"A critical bug exists." -> true\n"The system is insecure." -> true\n"No issues found. Severity: LOW." -> false\n"No." -> false\n"Yes" -> true\n"I don\'t know." -> false\n"There are problems, but nothing important. Severity: LOW." -> false'
                }
            ]
        }
    )


def get_message_logs_abs_file(base: Path, prefix: str) -> Path:
    return base / f"{prefix}_{get_current_timestamp_formatted()}.csv"


async def main():
    file_timestamp = get_current_timestamp_formatted()
    target = (Path(CONFIG.PROJECT_TARGET_BENCHMARK_ABS_DIR.value)
              / f"{Path(__file__).stem}_{file_timestamp}.csv")
    logs_folder = (Path(CONFIG.PROJECT_TARGET_BENCHMARK_ABS_DIR.value)
                   / f"{Path(__file__).stem}_{file_timestamp}")

    base_model = create_ollama(MODEL)
    security_researcher_agent = create_agent(
        model=base_model,
        tools=await create_tools()
    )
    verifier_agent = create_agent(
        model=base_model
        # response_format=Response
    )

    records = find_all_exists()[:200]
    print(f"Total: {len(records)}")
    pbar = create_tqdm(len(records))

    create_file(target)
    create_folder(logs_folder)
    with open(target, "a") as f:
        f.write(",".join(["project_url", "commit_id", "codebase_hash", "target", "actual", "elapsed_s"]))
        f.write("\n")

    for record in records:
        start = time.time()
        try:
            answer = await prompt_research(security_researcher_agent, record)
            actual = convert_response_bool_to_int((await prompt_verify(verifier_agent, answer["messages"][-1].content))["messages"][-1].content)
            for message in answer["messages"]:
                print(message.content)
            message_logs_abs_file = get_message_logs_abs_file(logs_folder, record.extract_preferred_repository_name())
            with open(message_logs_abs_file, "w") as f:
                for message in answer["messages"]:
                    content: str | list[str] = message.content
                    if isinstance(content, list):
                        content = "\n".join(map(str, content))
                    f.write(content)
                    f.write("\n")
        except Exception as err:
            print(err)
            actual = "EXCEPTION"
        # actual = 1
        elapsed = time.time() - start
        with open(target, "a") as f:
            row = ",".join([
                str(record.project_url),
                record.commit_id,
                record.extract_preferred_repository_name(),
                str(record.target),
                str(actual),
                "%.2f" % elapsed
            ])
            print()
            print("Processed: " + row)
            f.write(row)
            f.write("\n")
        pbar.update()
    print("Ended at " + get_current_timestamp_formatted())


if __name__ == '__main__':
    asyncio.run(main())
