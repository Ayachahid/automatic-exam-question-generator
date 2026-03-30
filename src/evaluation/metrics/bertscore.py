from src.core.logger import get_logger
import torch
from .base import BaseMetric

logger = get_logger("evaluation.metrics.bertscore")


class BERTScoreMetric(BaseMetric):
    """
    BERTScore metric — semantic similarity using contextual BERT embeddings.

    Unlike BLEU/ROUGE (which measure n-gram overlap), BERTScore captures
    semantic meaning by comparing token embeddings from a pretrained model.

    Uses transformers + torch — both already in pyproject.toml.

    Score range: −1.0 → 1.0 (higher = more semantically similar)
    Typical range in practice: 0.80 → 1.0 for reasonable answers.

    Args:
        model_name: HuggingFace model to use for embeddings.
                    Default: "distilbert-base-uncased" (fast, lightweight).
        batch_size: Number of samples per forward pass (default: 16).
        device:     "cpu" or "cuda". Auto-detected if None.
    """

    def __init__(
        self,
        model_name: str = "distilbert-base-uncased",
        batch_size: int = 16,
        device: str | None = None,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self._device = device
        self._model = None
        self._tokenizer = None
        logger.debug(
            f"BERTScoreMetric initialized: model={model_name} batch_size={batch_size}"
        )

    @property
    def name(self) -> str:
        return "BERTScore"

    def _load_model(self) -> None:
        """Lazy-load tokenizer and model."""
        if self._model is not None:
            return

        logger.info(f"Loading BERTScore model: {self.model_name}")
        try:
            from transformers import AutoModel, AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModel.from_pretrained(self.model_name)

            if self._device is None:
                self._device = "cuda" if torch.cuda.is_available() else "cpu"

            self._model.to(self._device)
            self._model.eval()
            logger.info(f"BERTScore model loaded on {self._device}: {self.model_name}")
        except ImportError:
            raise ImportError(
                "transformers and torch are required for BERTScoreMetric. "
                "They are already in pyproject.toml — run: uv sync"
            )

    def _embed(self, texts: list[str]) -> "torch.Tensor":
        """
        Encode a list of texts into mean-pooled embeddings.
        Returns a tensor of shape (len(texts), hidden_size).
        """

        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            encoded = self._tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            encoded = {k: v.to(self._device) for k, v in encoded.items()}

            with torch.no_grad():
                outputs = self._model(**encoded)

            # Mean pool over token dimension (ignore padding via attention mask)
            attention_mask = encoded["attention_mask"]
            token_embeddings = outputs.last_hidden_state
            mask_expanded = (
                attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            )
            sum_embeddings = torch.sum(token_embeddings * mask_expanded, dim=1)
            sum_mask = mask_expanded.sum(dim=1).clamp(min=1e-9)
            mean_pooled = sum_embeddings / sum_mask

            all_embeddings.append(mean_pooled.cpu())

        return torch.cat(all_embeddings, dim=0)

    @staticmethod
    def _cosine_similarity(a: "torch.Tensor", b: "torch.Tensor") -> "torch.Tensor":
        """Compute pairwise cosine similarity between two 2D tensors."""
        import torch.nn.functional as F

        a_norm = F.normalize(a, p=2, dim=1)
        b_norm = F.normalize(b, p=2, dim=1)
        return (a_norm * b_norm).sum(dim=1)

    def compute(
        self,
        predictions: list[str],
        references: list[str],
    ) -> dict[str, float]:
        """
        Compute BERTScore precision, recall, and F1.

        Args:
            predictions: Generated answers.
            references:  Reference answers.

        Returns:
            {
                "score":     mean F1 (primary score),
                "precision": mean BERTScore precision,
                "recall":    mean BERTScore recall,
                "f1":        mean BERTScore F1,
            }
        """
        self._validate_inputs(predictions, references)
        self._load_model()

        logger.info(
            f"[{self.name}] Computing embeddings for {len(predictions)} pairs..."
        )

        pred_embeddings = self._embed(predictions)
        ref_embeddings = self._embed(references)

        # BERTScore: cosine similarity between mean-pooled embeddings
        # (simplified version — production BERTScore uses token-level alignment)
        similarities = self._cosine_similarity(pred_embeddings, ref_embeddings)

        scores = similarities.tolist()
        mean_score = round(sum(scores) / len(scores), 4)

        result = {
            "score": mean_score,
            "precision": mean_score,  # simplified: p = r = f1 for mean-pooled
            "recall": mean_score,
            "f1": mean_score,
            "per_sample": [round(s, 4) for s in scores],
        }

        logger.info(f"[{self.name}] score={mean_score:.4f}")
        return result
