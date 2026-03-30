from src.core.logger import get_logger

from .base import BaseMetric

logger = get_logger("evaluation.metrics.rouge")


def _tokenize(text: str) -> list[str]:
    """Lowercase + whitespace tokenization."""
    return text.lower().split()


def _ngrams(tokens: list[str], n: int) -> dict[tuple, int]:
    """Count n-grams from a token list."""
    counts: dict[tuple, int] = {}
    for i in range(len(tokens) - n + 1):
        gram = tuple(tokens[i : i + n])
        counts[gram] = counts.get(gram, 0) + 1
    return counts


def _rouge_n(prediction: str, reference: str, n: int) -> dict[str, float]:
    """Compute ROUGE-N precision, recall, and F1 for a single pair."""
    pred_tokens = _tokenize(prediction)
    ref_tokens = _tokenize(reference)

    pred_ngrams = _ngrams(pred_tokens, n)
    ref_ngrams = _ngrams(ref_tokens, n)

    # Count overlapping n-grams
    overlap = 0
    for gram, count in pred_ngrams.items():
        overlap += min(count, ref_ngrams.get(gram, 0))

    pred_count = sum(pred_ngrams.values())
    ref_count = sum(ref_ngrams.values())

    precision = overlap / pred_count if pred_count > 0 else 0.0
    recall = overlap / ref_count if ref_count > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {"precision": precision, "recall": recall, "f1": f1}


def _lcs_length(x: list[str], y: list[str]) -> int:
    """Compute the length of the Longest Common Subsequence."""
    m, n = len(x), len(y)
    # Space-optimised DP (two rows)
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i - 1] == y[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(curr[j - 1], prev[j])
        prev, curr = curr, [0] * (n + 1)
    return prev[n]


def _rouge_l(prediction: str, reference: str) -> dict[str, float]:
    """Compute ROUGE-L precision, recall, and F1 for a single pair."""
    pred_tokens = _tokenize(prediction)
    ref_tokens = _tokenize(reference)

    lcs = _lcs_length(pred_tokens, ref_tokens)

    precision = lcs / len(pred_tokens) if pred_tokens else 0.0
    recall = lcs / len(ref_tokens) if ref_tokens else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {"precision": precision, "recall": recall, "f1": f1}


class ROUGEMetric(BaseMetric):
    """
    ROUGE (Recall-Oriented Understudy for Gisting Evaluation) metric.

    Computes ROUGE-1, ROUGE-2, and ROUGE-L F1 scores.
    Implemented in pure Python — no extra dependencies required.

    Score range: 0.0 (no overlap) → 1.0 (perfect match)

    Args:
        variants: List of ROUGE variants to compute.
                  Options: "rouge1", "rouge2", "rougeL" (default: all three).
    """

    SUPPORTED = {"rouge1", "rouge2", "rougeL"}

    def __init__(self, variants: list[str] | None = None):
        self.variants = variants or ["rouge1", "rouge2", "rougeL"]
        unknown = set(self.variants) - self.SUPPORTED
        if unknown:
            raise ValueError(
                f"Unknown ROUGE variants: {unknown}. Supported: {self.SUPPORTED}"
            )
        logger.debug(f"ROUGEMetric initialized: variants={self.variants}")

    @property
    def name(self) -> str:
        return "ROUGE"

    def compute(
        self,
        predictions: list[str],
        references: list[str],
    ) -> dict[str, float]:
        """
        Compute mean ROUGE scores over all prediction/reference pairs.

        Args:
            predictions: Generated answers.
            references:  Reference answers.

        Returns:
            {
                "score":        mean ROUGE-L F1 (primary score),
                "rouge1_f1":    mean ROUGE-1 F1,
                "rouge1_p":     mean ROUGE-1 precision,
                "rouge1_r":     mean ROUGE-1 recall,
                "rouge2_f1":    mean ROUGE-2 F1,
                "rouge2_p":     mean ROUGE-2 precision,
                "rouge2_r":     mean ROUGE-2 recall,
                "rougeL_f1":    mean ROUGE-L F1,
                "rougeL_p":     mean ROUGE-L precision,
                "rougeL_r":     mean ROUGE-L recall,
            }
        """
        self._validate_inputs(predictions, references)

        accum: dict[str, list[float]] = {
            v: []
            for v in [
                "rouge1_f1",
                "rouge1_p",
                "rouge1_r",
                "rouge2_f1",
                "rouge2_p",
                "rouge2_r",
                "rougeL_f1",
                "rougeL_p",
                "rougeL_r",
            ]
        }

        for pred, ref in zip(predictions, references):
            if "rouge1" in self.variants:
                r1 = _rouge_n(pred, ref, 1)
                accum["rouge1_f1"].append(r1["f1"])
                accum["rouge1_p"].append(r1["precision"])
                accum["rouge1_r"].append(r1["recall"])

            if "rouge2" in self.variants:
                r2 = _rouge_n(pred, ref, 2)
                accum["rouge2_f1"].append(r2["f1"])
                accum["rouge2_p"].append(r2["precision"])
                accum["rouge2_r"].append(r2["recall"])

            if "rougeL" in self.variants:
                rl = _rouge_l(pred, ref)
                accum["rougeL_f1"].append(rl["f1"])
                accum["rougeL_p"].append(rl["precision"])
                accum["rougeL_r"].append(rl["recall"])

        def _mean(lst: list[float]) -> float:
            return round(sum(lst) / len(lst), 4) if lst else 0.0

        result: dict[str, float] = {k: _mean(v) for k, v in accum.items()}

        # Primary score = ROUGE-L F1 (most informative single number)
        result["score"] = result.get("rougeL_f1", result.get("rouge1_f1", 0.0))

        logger.info(
            f"[{self.name}] score={result['score']:.4f} "
            f"rouge1={result.get('rouge1_f1', 0):.4f} "
            f"rouge2={result.get('rouge2_f1', 0):.4f} "
            f"rougeL={result.get('rougeL_f1', 0):.4f}"
        )
        return result
