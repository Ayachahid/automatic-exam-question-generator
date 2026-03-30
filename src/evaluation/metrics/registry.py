from src.core.logger import get_logger

from .base import BaseMetric
from .bertscore import BERTScoreMetric
from .bleu import BLEUMetric
from .rouge import ROUGEMetric
from .validator import QuestionValidator

logger = get_logger("evaluation.metrics.registry")

METRIC_REGISTRY: dict[str, type[BaseMetric]] = {
    "bleu": BLEUMetric,
    "rouge": ROUGEMetric,
    "bertscore": BERTScoreMetric,
}


class MetricFactory:
    """
    Factory for instantiating evaluation metrics by name.

    Supported metrics:
        - "bleu"       → BLEUMetric
        - "rouge"      → ROUGEMetric
        - "bertscore"  → BERTScoreMetric

    Example:
        factory = MetricFactory()
        metric  = factory.get_metric("bleu")
        result  = metric.compute(predictions, references)
    """

    def get_metric(self, name: str, **kwargs) -> BaseMetric:
        """
        Instantiate and return a metric by name.

        Args:
            name:    Metric name (case-insensitive): "bleu", "rouge", "bertscore".
            **kwargs: Extra arguments passed to the metric constructor.

        Returns:
            Instance of the requested BaseMetric subclass.

        Raises:
            ValueError: If the metric name is not supported.
        """
        key = name.lower().strip()
        if key not in METRIC_REGISTRY:
            raise ValueError(
                f"Unknown metric: '{name}'. "
                f"Supported: {list(METRIC_REGISTRY.keys())}"
            )
        logger.info(f"Creating metric: {key}")
        return METRIC_REGISTRY[key](**kwargs)

    def get_all_metrics(self, **kwargs) -> list[BaseMetric]:
        """
        Return one instance of every registered metric.

        Args:
            **kwargs: Passed to each metric constructor.

        Returns:
            List of all available BaseMetric instances.
        """
        logger.info("Creating all metrics")
        return [cls(**kwargs) for cls in METRIC_REGISTRY.values()]

    @staticmethod
    def supported_metrics() -> list[str]:
        """Return list of supported metric names."""
        return list(METRIC_REGISTRY.keys())

    @staticmethod
    def get_validator(
        question_type: str = "default", strict: bool = False
    ) -> QuestionValidator:
        """
        Convenience method to get a QuestionValidator.

        Args:
            question_type: One of "multiple_choice", "true_false",
                           "short_answer", "essay", "scenario_based", "default".
            strict:        If True, treat warnings as errors.

        Returns:
            Configured QuestionValidator instance.
        """
        logger.info(f"Creating QuestionValidator: type={question_type} strict={strict}")
        return QuestionValidator(question_type=question_type, strict=strict)
