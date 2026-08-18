from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app.evaluation.closure_eval import (  # noqa: E402
    DEFAULT_GOLDEN_PATH,
    DEFAULT_TRACE_DB_PATH,
    load_golden_cases,
    render_markdown_report,
    run_closure_eval,
    validate_golden_cases,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run agent-api closure golden evaluation")
    parser.add_argument("--cases", default=str(DEFAULT_GOLDEN_PATH))
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--output", default="reports/agent_closure/latest.json")
    parser.add_argument("--markdown-output", default="reports/agent_closure/latest.md")
    parser.add_argument("--trace-db", default=str(DEFAULT_TRACE_DB_PATH))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases = load_golden_cases(args.cases)
    validation = validate_golden_cases(cases)
    if args.validate_only:
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 0 if validation["valid"] else 1
    if not validation["valid"]:
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 1

    report = run_closure_eval(cases, trace_db_path=args.trace_db)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    markdown_path = Path(args.markdown_output)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        render_markdown_report(report) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"report={output_path}")
    print(f"markdown_report={markdown_path}")
    print(f"trace_db={args.trace_db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
