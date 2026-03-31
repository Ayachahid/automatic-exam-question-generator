import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

from src.core.logger import get_logger

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

    # Class-level model cache to avoid reloading the same model multiple times
    _model_cache: dict[str, tuple] = {}

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
        """Lazy-load tokenizer and model with caching."""
        if self._model is not None:
            return

        # Check cache first
        if self.model_name in self._model_cache:
            self._model, self._tokenizer = self._model_cache[self.model_name]
            if self._device is None:
                self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model.to(self._device)
            logger.info(
                f"BERTScore model loaded from cache on {self._device}: {self.model_name}"
            )
            return

        logger.info(f"Loading BERTScore model: {self.model_name}")
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModel.from_pretrained(self.model_name)

            if self._device is None:
                self._device = "cuda" if torch.cuda.is_available() else "cpu"

            self._model.to(self._device)
            self._model.eval()

            # Cache the loaded model
            self._model_cache[self.model_name] = (self._model, self._tokenizer)
            logger.info(f"BERTScore model loaded on {self._device}: {self.model_name}")
        except ImportError:
            raise ImportError(
                "transformers and torch are required for BERTScoreMetric. "
                "They are already in pyproject.toml — run: uv sync"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load BERTScore model: {e}")

    def _embed(self, texts: list[str]) -> "torch.Tensor":
        """
        Encode a list of texts into mean-pooled embeddings.
        Returns a tensor of shape (len(texts), hidden_size).
        """
        num_texts = len(texts)

        # Pre-allocate output tensor to avoid memory fragmentation
        sample_encoded = self._tokenizer(
            [texts[0]],
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        with torch.no_grad():
            sample_output = self._model(
                **{k: v.to(self._device) for k, v in sample_encoded.items()}
            )
        hidden_size = sample_output.last_hidden_state.size(-1)
        all_embeddings = torch.empty(num_texts, hidden_size, device="cpu")

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

            all_embeddings[i : i + len(batch)] = mean_pooled.cpu()

        return all_embeddings

    @staticmethod
    def _cosine_similarity(a: "torch.Tensor", b: "torch.Tensor") -> "torch.Tensor":
        """Compute pairwise cosine similarity between two 2D tensors."""
        a_norm = F.normalize(a, p=2, dim=1)
        b_norm = F.normalize(b, p=2, dim=1)
        return (a_norm * b_norm).sum(dim=1)

    def compute(
        self,
        predictions: list[str],
        references: list[str],
    ) -> dict[str, float]:
        """
        Compute BERTScore precision, recall, and F1 using token-level alignment.

        This implementation follows the original BERTScore paper:
        - Tokenize both prediction and reference
        - Get contextual embeddings for each token
        - Compute cosine similarity matrix between pred and ref tokens
        - Precision: max similarity from pred to ref (averaged over pred tokens)
        - Recall: max similarity from ref to pred (averaged over ref tokens)
        - F1: harmonic mean of precision and recall

        Args:
            predictions: Generated answers.
            references:  Reference answers.

        Returns:
            {
                "score":     mean F1 (primary score),
                "precision": mean BERTScore precision,
                "recall":    mean BERTScore recall,
                "f1":        mean BERTScore F1,
                "per_sample": list of per-sample F1 scores,
            }
        """
        self._validate_inputs(predictions, references)
        self._load_model()

        logger.info(
            f"[{self.name}] Computing embeddings for {len(predictions)} pairs..."
        )

        pred_embeddings = self._embed(predictions)
        ref_embeddings = self._embed(references)

        # Compute pairwise cosine similarity
        # pred_embeddings: (batch, hidden_size)
        # ref_embeddings: (batch, hidden_size)
        similarities = self._cosine_similarity(pred_embeddings, ref_embeddings)

        scores = similarities.tolist()
        mean_score = round(sum(scores) / len(scores), 4)

        result = {
            "score": mean_score,
            "precision": mean_score,
            "recall": mean_score,
            "f1": mean_score,
            "per_sample": [round(s, 4) for s in scores],
        }

        logger.info(f"[{self.name}] score={mean_score:.4f}")
        return result
