from pathlib import Path
import json
import os
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.app.evaluation.semantic_review import (
    build_semantic_backend_review,
    render_semantic_backend_review_markdown,
)


DEFAULT_INPUT_PATH = "reports/day41_semantic_extended_backend_eval.json"
DEFAULT_OUTPUT_PATH = "reports/day41_semantic_backend_review.md"


def main() -> None:
    input_path = Path(
        os.getenv("DAY41_SEMANTIC_EVAL_INPUT", DEFAULT_INPUT_PATH)
    )
    output_path = Path(
        os.getenv("DAY41_SEMANTIC_REVIEW_OUTPUT", DEFAULT_OUTPUT_PATH)
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Semantic eval report not found: {input_path}. "
            "Run scripts/validate_semantic_extended_backend_eval.py first."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    comparison = json.loads(input_path.read_text(encoding="utf-8"))

    review = build_semantic_backend_review(comparison)
    markdown = render_semantic_backend_review_markdown(review)

    output_path.write_text(markdown, encoding="utf-8")

    print("== Day41 semantic backend review ==")
    print("input_path =", input_path)
    print("output_path =", output_path)
    print("review_decision =", review["review_decision"])
    print(
        "semantic_candidate_validated =",
        review["semantic_candidate_validated"],
    )
    print("candidate_backend =", review["candidate_backend"])
    print("default_backend =", review["default_backend"])
    print("common_failed_cases =", review["common_failed_cases"])
    print("blocking_reasons =", review["blocking_reasons"])
    print()
    print("wrote:", output_path)


if __name__ == "__main__":
    main()
