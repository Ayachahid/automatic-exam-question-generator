from dataclasses import dataclass, field

from src.core.logger import get_logger

logger = get_logger("evaluation.metrics.validator")

# Required fields per question type
REQUIRED_FIELDS: dict[str, list[str]] = {
    "multiple_choice": ["question", "options", "answer", "explanation"],
    "true_false": ["question", "answer", "explanation"],
    "short_answer": ["question", "answer"],
    "essay": ["question", "answer"],
    "scenario_based": ["scenario", "question", "answer", "concepts_tested"],
    "default": ["question", "answer"],
}

# Minimum word counts for quality checks
MIN_QUESTION_WORDS = 4
MIN_ANSWER_WORDS = 1
MCQ_OPTIONS_COUNT = 4


@dataclass
class QuestionValidationResult:
    """Result of validating a single question."""

    index: int
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass
class ValidationReport:
    """Aggregated validation report for a batch of questions."""

    total: int
    valid_count: int
    invalid_count: int
    results: list[QuestionValidationResult] = field(default_factory=list)

    @property
    def validity_pct(self) -> float:
        return round(self.valid_count / self.total * 100, 1) if self.total else 0.0

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "validity_pct": self.validity_pct,
            "results": [r.to_dict() for r in self.results],
        }


class QuestionValidator:
    """
    Validates the structure and quality of generated exam questions.

    Checks:
        - Required fields are present and non-empty
        - Question text meets minimum word count
        - Answer is non-empty
        - MCQ has exactly 4 options
        - No duplicate question texts in the batch
        - Explanation is present (warning if missing)
        - Answer for true/false is a boolean-like value

    Args:
        question_type: Type of questions to validate against.
                       Uses "default" if not specified.
        strict:        If True, treat warnings as errors (default: False).
    """

    def __init__(
        self,
        question_type: str = "default",
        strict: bool = False,
    ):
        self.question_type = question_type
        self.strict = strict
        self.required_fields = REQUIRED_FIELDS.get(
            question_type, REQUIRED_FIELDS["default"]
        )
        logger.debug(
            f"QuestionValidator initialized: type={question_type} strict={strict}"
        )

    def validate_one(self, question: dict, index: int = 0) -> QuestionValidationResult:
        """
        Validate a single question dict.

        Args:
            question: The question dict from the pipeline.
            index:    Position in the batch (for reporting).

        Returns:
            QuestionValidationResult with errors and warnings.
        """
        errors: list[str] = []
        warnings: list[str] = []

        # ── Required fields ────────────────────────────────────────────────────
        for field_name in self.required_fields:
            value = question.get(field_name)
            if value is None or (isinstance(value, (str, list)) and not value):
                errors.append(f"Missing or empty required field: '{field_name}'")

        # ── Question text quality ──────────────────────────────────────────────
        question_text = question.get("question", "")
        if isinstance(question_text, str):
            word_count = len(question_text.split())
            if word_count < MIN_QUESTION_WORDS:
                errors.append(
                    f"Question too short: {word_count} words "
                    f"(minimum: {MIN_QUESTION_WORDS})"
                )
            if question_text and not question_text.strip().endswith(("?", ".", ":")):
                warnings.append("Question does not end with '?', '.', or ':'")

        # ── Answer quality ─────────────────────────────────────────────────────
        answer = question.get("answer", "")
        answer_str = str(answer).strip()
        if len(answer_str.split()) < MIN_ANSWER_WORDS:
            errors.append("Answer is empty or too short.")

        # ── MCQ-specific checks ────────────────────────────────────────────────
        if self.question_type == "multiple_choice":
            options = question.get("options", [])
            if isinstance(options, list):
                if len(options) != MCQ_OPTIONS_COUNT:
                    errors.append(
                        f"MCQ must have exactly {MCQ_OPTIONS_COUNT} options, "
                        f"got {len(options)}"
                    )
                # Answer must be a valid option letter or option text
                valid_letters = {"A", "B", "C", "D"}
                if (
                    answer_str.upper() not in valid_letters
                    and answer_str not in options
                ):
                    warnings.append(
                        f"Answer '{answer_str}' is not a valid option letter "
                        f"(A/B/C/D) or option text."
                    )

        # ── True/False-specific checks ─────────────────────────────────────────
        if self.question_type == "true_false":
            valid_tf = {"true", "false", "1", "0", "yes", "no", "t", "f"}
            if answer_str.lower() not in valid_tf:
                errors.append(
                    f"True/False answer must be true/false, got: '{answer_str}'"
                )

        # ── Scenario-based checks ──────────────────────────────────────────────
        if self.question_type == "scenario_based":
            concepts = question.get("concepts_tested", [])
            if isinstance(concepts, list) and len(concepts) < 2:
                warnings.append(
                    f"concepts_tested has only {len(concepts)} item(s); "
                    "expected 2–4 concepts."
                )

        # ── Optional field warnings ────────────────────────────────────────────
        if not question.get("explanation") and self.question_type not in (
            "short_answer",
            "essay",
        ):
            warnings.append(
                "No 'explanation' provided — recommended for exam feedback."
            )

        is_valid = len(errors) == 0
        if self.strict:
            is_valid = is_valid and len(warnings) == 0

        return QuestionValidationResult(
            index=index,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
        )

    def validate_batch(self, questions: list[dict]) -> ValidationReport:
        """
        Validate a list of questions and return a full report.

        Args:
            questions: List of question dicts from the pipeline.

        Returns:
            ValidationReport with per-question results and aggregate stats.
        """
        if not questions:
            logger.warning("validate_batch called with empty list")
            return ValidationReport(total=0, valid_count=0, invalid_count=0)

        logger.info(
            f"Validating {len(questions)} questions "
            f"[type={self.question_type}, strict={self.strict}]"
        )

        results: list[QuestionValidationResult] = []

        # ── Duplicate detection ────────────────────────────────────────────────
        seen_questions: dict[str, int] = {}
        for i, q in enumerate(questions):
            text = q.get("question", "").strip().lower()
            if text in seen_questions:
                # Mark current as duplicate
                dup_result = QuestionValidationResult(
                    index=i,
                    is_valid=False,
                    errors=[
                        f"Duplicate question (same as index {seen_questions[text]})"
                    ],
                )
                results.append(dup_result)
            else:
                seen_questions[text] = i
                results.append(self.validate_one(q, index=i))

        valid_count = sum(1 for r in results if r.is_valid)
        invalid_count = len(results) - valid_count

        report = ValidationReport(
            total=len(questions),
            valid_count=valid_count,
            invalid_count=invalid_count,
            results=results,
        )

        logger.info(
            f"Validation complete: {valid_count}/{len(questions)} valid "
            f"({report.validity_pct}%)"
        )
        return report
