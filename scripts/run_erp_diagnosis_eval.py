from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Support the documented direct invocation:
#   python scripts/run_erp_diagnosis_eval.py
# When Python executes a script by path, sys.path[0] is the scripts directory,
# not necessarily the repository root, so add the project root before importing
# the src package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app.business.erp_diagnosis.evaluation import (  # noqa: E402
    DEFAULT_ERP_GOLDEN_FILE,
    run_erp_diagnosis_golden_eval,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run deterministic ERP diagnosis business Golden Cases."
    )
    parser.add_argument(
        "--eval-file",
        default=str(DEFAULT_ERP_GOLDEN_FILE),
        help="Path to ERP diagnosis JSONL Golden Cases.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON report path. reports/ is ignored by git.",
    )
    args = parser.parse_args()

    report = run_erp_diagnosis_golden_eval(args.eval_file)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")

    return 0 if report["summary"]["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
