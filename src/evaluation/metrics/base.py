from abc import ABC, abstractmethod

from src.core.logger import get_logger

logger = get_logger("evaluation.metrics.base")


class BaseMetric(ABC):
    """
    Abstract base class for all evaluation metrics.

    Each metric takes a list of generated answers and a list of reference
    answers and returns a score dict with at least a 'score' key.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the metric."""

    @abstractmethod
    def compute(
        self,
        predictions: list[str],
        references: list[str],
    ) -> dict[str, float]:
        """
        Compute the metric between predictions and references.

        Args:
            predictions: List of generated/predicted strings.
            references:  List of ground-truth reference strings.

        Returns:
            Dict with at least {"score": float} plus optional sub-scores.

        Raises:
            ValueError: If predictions and references have different lengths
                        or are empty.
        """

    def _validate_inputs(
        self,
        predictions: list[str],
        references: list[str],
    ) -> None:
        """Shared input validation for all metrics."""
        if not predictions or not references:
            raise ValueError(
                f"[{self.name}] predictions and references must not be empty."
            )
        if len(predictions) != len(references):
            raise ValueError(
                f"[{self.name}] predictions ({len(predictions)}) and "
                f"references ({len(references)}) must have the same length."
            )
        logger.debug(
            f"[{self.name}] Computing on {len(predictions)} prediction/reference pairs"
        )
