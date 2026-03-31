from nltk.translate.bleu_score import (
    SmoothingFunction,
    corpus_bleu,
    sentence_bleu,
)

from src.core.logger import get_logger

from .base import BaseMetric

logger = get_logger("evaluation.metrics.bleu")


class BLEUMetric(BaseMetric):
    """
    BLEU (Bilingual Evaluation Understudy) score metric.

    Measures n-gram overlap between generated answers and reference answers.
    Commonly used to evaluate text generation quality.

    Uses nltk.translate.bleu_score under the hood — no extra dependencies
    beyond what is already in pyproject.toml.

    Score range: 0.0 (no overlap) → 1.0 (perfect match)

    Args:
        max_n:            Maximum n-gram order (default: 4 → BLEU-4).
        smoothing:        Apply smoothing for short sentences (default: True).
    """

    def __init__(self, max_n: int = 4, smoothing: bool = True):
        self.max_n = max_n
        self.smoothing = smoothing
        logger.debug(f"BLEUMetric initialized: max_n={max_n} smoothing={smoothing}")

    @property
    def name(self) -> str:
        return f"BLEU-{self.max_n}"

    def compute(
        self,
        predictions: list[str],
        references: list[str],
    ) -> dict[str, float]:
        """
        Compute corpus-level BLEU and per-order scores.

        Args:
            predictions: Generated answers.
            references:  Reference answers.

        Returns:
            {
                "score":  corpus BLEU score (0.0–1.0),
                "bleu_1": unigram precision,
                "bleu_2": bigram precision,
                "bleu_3": trigram precision,
                "bleu_4": 4-gram precision,
            }
        """
        self._validate_inputs(predictions, references)

        try:
            from nltk.translate.bleu_score import (
                SmoothingFunction,
                corpus_bleu,
                sentence_bleu,
            )
        except ImportError:
            raise ImportError(
                "nltk is required for BLEUMetric. "
                "It is already in pyproject.toml — run: uv sync"
            )

        smoother = SmoothingFunction().method1 if self.smoothing else None

        # Tokenise: split on whitespace (language-agnostic)
        tokenized_preds = [pred.lower().split() for pred in predictions]
        tokenized_refs = [[ref.lower().split()] for ref in references]

        # Corpus-level BLEU
        weights = tuple(1.0 / self.max_n for _ in range(self.max_n))
        corpus_score = corpus_bleu(
            tokenized_refs,
            tokenized_preds,
            weights=weights,
            smoothing_function=smoother,
        )

        # Per-order scores (BLEU-1 to BLEU-4)
        per_order: dict[str, float] = {}
        for n in range(1, min(self.max_n, 4) + 1):
            w = tuple(1.0 if i == n - 1 else 0.0 for i in range(n))
            scores = [
                sentence_bleu(ref, pred, weights=w, smoothing_function=smoother)
                for pred, ref in zip(tokenized_preds, tokenized_refs)
            ]
            per_order[f"bleu_{n}"] = round(sum(scores) / len(scores), 4)

        result = {"score": round(float(corpus_score), 4), **per_order}
        logger.info(f"[{self.name}] score={result['score']:.4f}")
        return result
