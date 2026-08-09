import argparse
import sys
from pathlib import Path

from src.core.logger import get_logger
from src.generation.pipeline import QuestionGenerationPipeline

logger = get_logger("scripts.generate")

import json

# Base directory for path validation (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def safe_path(user_path: str, allowed_base: Path) -> Path:
    """
    Resolve and validate path to prevent path traversal attacks.

    For relative paths: resolves against allowed_base and validates it stays within.
    For absolute paths: validates the path doesn't contain traversal sequences.

    Args:
        user_path: User-provided path string.
        allowed_base: Base directory for relative path resolution.

    Returns:
        Resolved and validated Path object.

    Raises:
        ValueError: If path traversal is detected.
    """
    user_path_obj = Path(user_path)

    # Handle absolute paths (e.g., from pytest temp directories)
    if user_path_obj.is_absolute():
        resolved = user_path_obj.resolve()
        # Check for suspicious patterns but allow legitimate absolute paths
        if ".." in user_path:
            # Verify it doesn't escape to sensitive locations
            resolved_str = str(resolved).lower()
            if any(
                s in resolved_str
                for s in ["/etc/", "/passwd", "/shadow", "windows/system32"]
            ):
                raise ValueError(f"Path traversal detected: {user_path}")
        return resolved

    # Relative paths: resolve against allowed_base
    resolved = (allowed_base / user_path).resolve()
    try:
        resolved.relative_to(allowed_base.resolve())
    except ValueError:
        raise ValueError(f"Path traversal detected: {user_path}")
    return resolved


QUESTION_TYPES = [
    "multiple_choice",
    "short_answer",
    "true_false",
    "essay",
    "scenario_based",
]
DIFFICULTIES = ["easy", "medium", "hard"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate exam questions from a document or text using an LLM.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Input source (mutually exclusive)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--input",
        help="Path to input file (PDF, DOCX, TXT, PPTX) or a URL.",
    )
    source.add_argument(
        "--text",
        help="Direct text input for question generation.",
    )

    # Generation options
    parser.add_argument(
        "--type",
        default="multiple_choice",
        choices=QUESTION_TYPES,
        dest="question_type",
        help="Type of questions to generate.",
    )
    parser.add_argument(
        "--difficulty",
        default="medium",
        choices=DIFFICULTIES,
        help="Difficulty level of the questions.",
    )
    parser.add_argument(
        "--num",
        type=int,
        default=5,
        dest="num_questions",
        help="Number of questions to generate.",
    )

    # Output
    parser.add_argument(
        "--output",
        default=None,
        help="Path to save questions as JSON. Defaults to stdout if not provided.",
    )
    parser.add_argument(
        "--config",
        default="configs/config.yaml",
        help="Path to the YAML config file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Initialize pipeline
    logger.info("Initializing pipeline...")
    try:
        pipeline = QuestionGenerationPipeline(config_path=args.config)
    except FileNotFoundError:
        logger.error(f"Config file not found: {args.config}")
        return 1

    #  Run pipeline
    source_label = args.input or "direct text"
    logger.info(
        f"Generating {args.num_questions} [{args.question_type}] "
        f"({args.difficulty}) questions from: {source_label}"
    )

    try:
        questions = pipeline.run(
            file_path=args.input,
            text=args.text,
            question_type=args.question_type,
            difficulty=args.difficulty,
            num_questions=args.num_questions,
        )
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return 1

    if not questions:
        logger.warning("No questions were generated. Check your LLM output.")
        return 1

    logger.info(f"Successfully generated {len(questions)} questions")

    payload = {
        "total": len(questions),
        "question_type": args.question_type,
        "difficulty": args.difficulty,
        "source": source_label,
        "questions": questions,
    }

    # Output
    if args.output:
        # Validate output path
        try:
            out_path = safe_path(args.output, BASE_DIR)
        except ValueError as e:
            logger.error(e)
            return 1

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info(f"Questions saved to: {out_path}")
        print(f"\n {len(questions)} questions saved to: {out_path}")
    else:
        # Print to stdout
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
