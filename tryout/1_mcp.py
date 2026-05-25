import asyncio
from typing import Any

from langchain.agents import create_agent
from llm_service import create_chatgpt

from entity.vulnerability_record_test_paired import \
    VulnerabilityRecordTestPaired
from service import primevul_paired_service
from service.llm_service import create_tools

# MODEL = "ollama:qwen3-coder-next:cloud"
# MODEL = "qwen3-coder-next:q4_K_M"
# MODEL = "gpt-oss:20b"
# MODEL = "ollama:qwen3.5:9b"
MODEL = "gpt-5.4"


async def prompt2(agent, v: VulnerabilityRecordTestPaired) -> dict[str, Any] | Any:
    return await agent.ainvoke(
        {
            "description": "Comprehensive security audit — maps attack surface and discovers vulnerabilities across a codebase.",
            "messages": [
                {
                    "role": "system",
                    "content": f'You are performing a comprehensive security audit on project {v.extract_preferred_repository_name()}.\n\n\n## Confidence & False-Positive Policy\n\nCodeBadger\'s detectors assign a **Confidence** level (HIGH / MEDIUM) to each finding based on:\n- Flow type (direct dereference vs passed-to-function, same-pointer vs alias, intraprocedural vs interprocedural)\n- Reachability from external input (BFS depth 10 over call graph)\n\n**Use the tool\'s confidence levels to structure your report:**\n- **HIGH confidence** findings: Report as confirmed vulnerabilities in the main findings section. These have direct evidence (e.g., same-function usage, confirmed dataflow, direct dereference) or are reachable from external input.\n- **MEDIUM confidence** findings: Include in a "Needs Manual Review" section with explanation of why they are uncertain (e.g., alias-based, passed-to-function without confirmed dereference, not reachable from external input).\n- After gathering tool results, critically evaluate each finding — cross-reference with at least two signals (e.g., confirmed taint flow + dangerous sink without sanitization, or CFG shows reachable path + no bounds check).\n- Discard findings that are likely false positives: dead code paths, safely wrapped calls, test-only code, or sinks that are unreachable from external input.\n- Never pad the report with low-confidence noise. A short report with 3 real findings is far more valuable than a long report with 20 speculative ones.\n\nEach finding also includes **validation context** (function signature, callers, reachability from external input) to help you write targeted PoC triggers and assess exploitability.\n\nFollow this systematic workflow:\n\n## Phase 1: Reconnaissance\n1. Call `get_codebase_summary(codebase_hash="<retrieved hash>")` to understand scope (language, files, methods, calls)\n2. Call `list_source_files(codebase_hash="<retrieved hash>")` to understand the project structure\n3. Call `discover_fixed_vulnerabilities(codebase_hash="<retrieved hash>")` to find historical vulnerability hints from git history\n\n## Phase 2: Attack Surface Mapping\n4. Call `find_taint_sources(codebase_hash="<retrieved hash>")` to enumerate all external input points\n5. Call `find_taint_sinks(codebase_hash="<retrieved hash>")` to enumerate all dangerous operations\n\n## Phase 3: Automated Taint Analysis\n6. Call `find_taint_flows(codebase_hash="<retrieved hash>", mode="auto")` to discover all confirmed source-to-sink data flows\n\n\n## Phase 3b: Memory Safety (if C/C++)\nIf the codebase language is C or C++, also run:\n7. `find_use_after_free(codebase_hash="<retrieved hash>")` — detect use-after-free vulnerabilities\n8. `find_double_free(codebase_hash="<retrieved hash>")` — detect double-free vulnerabilities\n9. `find_bounds_checks(codebase_hash="<retrieved hash>")` — find buffer accesses missing bounds checks\n10. `find_null_pointer_deref(codebase_hash="<retrieved hash>")` — detect null pointer dereference vulnerabilities (CWE-476)\n11. `find_integer_overflow(codebase_hash="<retrieved hash>")` — detect integer overflow/underflow before allocation or array indexing (CWE-190)\n12. `find_toctou(codebase_hash="<retrieved hash>")` — detect TOCTOU race conditions (CWE-367) where access()/stat() is followed by open() on the same path\n\n## Phase 4: Deep Investigation\nFor each confirmed vulnerability or taint flow:\n- Call `get_file_content(codebase_hash="<retrieved hash>", method_name="<vulnerable_function>")` to view the full source\n- Call `get_program_slice(codebase_hash="<retrieved hash>", ...)` to trace data origins backward\n- Call `get_variable_flow(codebase_hash="<retrieved hash>", ...)` for specific variable tracking\n\n## Phase 5: Report\nProduce a structured security audit report with:\n- **Executive Summary**: Overall risk level and key findings count\n- **Findings Table**: Each vulnerability with severity (Critical/High/Medium/Low), CWE ID, affected file:line, and description\n- **Detailed Findings**: For each finding — vulnerable code snippet, data flow path, exploitability assessment, and remediation recommendation\n- **Attack Surface Summary**: Count of input points, dangerous sinks, and confirmed flow paths',
                },
                {
                    "role": "user",
                    "content": f"Find if function {v.func} in file {v.file_name} is vulnerable.",
                },
                {
                    "role": "assistant",
                    "content": "I'll perform a systematic security audit following the phased workflow. Let me start with codebase load.",
                },
            ],
        }
    )


async def main():
    base_chat_model = create_chatgpt(MODEL)
    agent = create_agent(
        model=base_chat_model,
        tools=await create_tools(),
        # response_format=Response
    )

    vulnerability_records = primevul_paired_service.find_all_exists()
    result = await prompt2(agent, vulnerability_records[0])
    print("")


if __name__ == "__main__":
    asyncio.run(main())
