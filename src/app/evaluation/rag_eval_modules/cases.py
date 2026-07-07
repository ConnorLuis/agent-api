import json
from pathlib import Path
from typing import Any

DEFAULT_RAG_EVAL_FILE = Path("eval_cases/rag_agentic_eval.jsonl")


def load_rag_eval_cases(
    eval_file: Path | str = DEFAULT_RAG_EVAL_FILE,
) -> list[dict[str, Any]]:
    path = Path(eval_file)

    cases: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()

            if not stripped:
                continue

            cases.append(json.loads(stripped))

    return cases


def _normalize_expected_terms(case: dict[str, Any]) -> list[str]:
    raw_terms = case.get("expected_terms", [])

    return [
        str(term).lower()
        for term in raw_terms
        if str(term).strip()
    ]