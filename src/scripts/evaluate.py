import argparse
import importlib
import sys
from pathlib import Path

from src.core.logger import get_logger

logger = get_logger("scripts.evaluate")

_json = importlib.import_module("json")

# Required fields per question type
REQUIRED_FIELDS: dict[str, list[str]] = {
    "multiple_choice": ["question", "options", "answer"],
    "true_false": ["question", "answer"],
    "short_answer": ["question", "answer"],
    "essay": ["question", "answer"],
    "scenario_based": ["scenario", "question", "answer", "concepts_tested"],
    "default": ["question", "answer"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate quality metrics of generated exam questions.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the JSON file containing generated questions.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to save the evaluation report as JSON. Defaults to stdout.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed per-question analysis.",
    )
    parser.add_argument(
        "--type",
        default=None,
        dest="question_type",
        choices=list(REQUIRED_FIELDS.keys()),
        help="Question type for completeness check. Auto-detected if not provided.",
    )
    return parser.parse_args()


# Metric helpers


def compute_completeness(questions: list[dict], required_fields: list[str]) -> dict:
    """Check that each question has all required fields with non-empty values."""
    complete = 0
    missing_per_q = []

    for q in questions:
        missing = [f for f in required_fields if not q.get(f)]
        if not missing:
            complete += 1
        missing_per_q.append(missing)

    return {
        "complete_count": complete,
        "total": len(questions),
        "completeness_pct": (
            round(complete / len(questions) * 100, 1) if questions else 0
        ),
        "missing_fields_per_question": missing_per_q,
    }


def compute_uniqueness(questions: list[dict]) -> dict:
    """Check for duplicate question texts."""
    texts = [q.get("question", "").strip().lower() for q in questions]
    unique = len(set(texts))
    duplicates = len(texts) - unique

    return {
        "unique_count": unique,
        "duplicate_count": duplicates,
        "uniqueness_pct": round(unique / len(texts) * 100, 1) if texts else 0,
    }


def compute_avg_length(questions: list[dict]) -> dict:
    """Compute average word count of question texts."""
    lengths = [len(q.get("question", "").split()) for q in questions]
    avg = sum(lengths) / len(lengths) if lengths else 0

    return {
        "avg_words_per_question": round(avg, 1),
        "min_words": min(lengths) if lengths else 0,
        "max_words": max(lengths) if lengths else 0,
    }


def compute_empty_answers(questions: list[dict]) -> dict:
    """Check for questions with empty answers."""
    empty = sum(1 for q in questions if not str(q.get("answer", "")).strip())
    return {
        "empty_answer_count": empty,
        "empty_answer_pct": round(empty / len(questions) * 100, 1) if questions else 0,
    }


def compute_field_coverage(questions: list[dict]) -> dict:
    """Count presence of optional fields across all questions."""
    optional_fields = ["explanation", "options", "scenario", "concepts_tested"]
    coverage = {}
    for field in optional_fields:
        count = sum(1 for q in questions if q.get(field))
        coverage[field] = {
            "count": count,
            "pct": round(count / len(questions) * 100, 1) if questions else 0,
        }
    return coverage


def detect_question_type(questions: list[dict]) -> str:
    """Auto-detect question type from fields present."""
    if not questions:
        return "default"
    sample = questions[0]
    if "scenario" in sample:
        return "scenario_based"
    if "options" in sample:
        return "multiple_choice"
    return "default"


def print_report(report: dict, verbose: bool = False):
    """Pretty-print the evaluation report to stdout."""
    q_type = report["question_type"]
    total = report["summary"]["total_questions"]

    print(f"\n{'='*55}")
    print(f"  Evaluation Report — [{q_type}]")
    print(f"{'='*55}")
    print(f"  Total questions   : {total}")
    print(f"  Completeness      : {report['completeness']['completeness_pct']}%")
    print(f"  Uniqueness        : {report['uniqueness']['uniqueness_pct']}%")
    print(
        f"  Avg question len  : {report['avg_length']['avg_words_per_question']} words"
    )
    print(f"  Empty answers     : {report['empty_answers']['empty_answer_pct']}%")

    print("\n  Optional field coverage:")
    for field, data in report["field_coverage"].items():
        bar = " " * int(data["pct"] / 10)
        print(f"    {field:<20} {data['pct']:>5}%  {bar}")

    if report["uniqueness"]["duplicate_count"] > 0:
        print(
            f"\n   {report['uniqueness']['duplicate_count']} duplicate question(s) detected!"
        )

    if report["empty_answers"]["empty_answer_count"] > 0:
        print(
            f"   {report['empty_answers']['empty_answer_count']} question(s) with empty answers!"
        )

    if verbose:
        print(f"\n{'─'*55}")
        print("  Per-question analysis:")
        missing_list = report["completeness"]["missing_fields_per_question"]
        for i, missing in enumerate(missing_list, 1):
            status = " complete " if not missing else f" missing: {missing}"
            print(f"    Q{i:02d}: {status}")

    print(f"{'='*55}\n")


def main() -> int:
    args = parse_args()

    # Load questions file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1

    logger.info(f"Loading questions from: {input_path}")
    try:
        raw = _json.loads(input_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        return 1

    # Support both {"questions": [...]} and plain list [...]
    questions = raw.get("questions", raw) if isinstance(raw, dict) else raw
    if not isinstance(questions, list) or not questions:
        logger.error("No questions found in the input file.")
        return 1

    logger.info(f"Evaluating {len(questions)} questions...")

    # Detect question type
    q_type = (
        args.question_type
        or raw.get("question_type")
        or detect_question_type(questions)
    )
    required_fields = REQUIRED_FIELDS.get(q_type, REQUIRED_FIELDS["default"])
    logger.info(f"Question type detected: {q_type}")

    # Compute metrics
    report = {
        "source_file": str(input_path),
        "question_type": q_type,
        "summary": {"total_questions": len(questions)},
        "completeness": compute_completeness(questions, required_fields),
        "uniqueness": compute_uniqueness(questions),
        "avg_length": compute_avg_length(questions),
        "empty_answers": compute_empty_answers(questions),
        "field_coverage": compute_field_coverage(questions),
    }

    # Output
    print_report(report, verbose=args.verbose)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Remove per-question details from saved report (keep it lightweight)
        saved_report = {k: v for k, v in report.items() if k != "completeness"}
        saved_report["completeness"] = {
            k: v
            for k, v in report["completeness"].items()
            if k != "missing_fields_per_question"
        }
        out_path.write_text(
            _json.dumps(saved_report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info(f"Evaluation report saved to: {out_path}")
        print(f" Report saved to: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
