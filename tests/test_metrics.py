import pytest

# ── Imports du module ──────────────────────────────────────────────────────────
from src.evaluation.metrics.base import BaseMetric
from src.evaluation.metrics.bleu import BLEUMetric
from src.evaluation.metrics.rouge import (
    ROUGEMetric,
    _ngrams,
    _lcs_length,
    _rouge_n,
    _rouge_l,
)
from src.evaluation.metrics.bertscore import BERTScoreMetric
from src.evaluation.metrics.validator import (
    QuestionValidator,
    ValidationReport,
    MIN_QUESTION_WORDS,
    MCQ_OPTIONS_COUNT,
)
from src.evaluation.metrics.registry import MetricFactory, METRIC_REGISTRY

# ══════════════════════════════════════════════════════════════════════════════
# Fixtures partagées
# ══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_predictions():
    return [
        "The cat sat on the mat",
        "Deep learning uses neural networks",
        "Python is a programming language",
    ]


@pytest.fixture
def sample_references():
    return [
        "The cat sat on the mat",  # perfect match
        "Neural networks power deep learning",  # partial overlap
        "Java is a programming language",  # one word different
    ]


@pytest.fixture
def perfect_predictions():
    return ["The quick brown fox", "Hello world"]


@pytest.fixture
def perfect_references():
    return ["The quick brown fox", "Hello world"]


@pytest.fixture
def mcq_valid():
    return {
        "question": "What is the capital of France?",
        "options": ["A. Paris", "B. London", "C. Berlin", "D. Rome"],
        "answer": "A",
        "explanation": "Paris is the capital and largest city of France.",
    }


@pytest.fixture
def tf_valid():
    return {
        "question": "Is Python a compiled language?",
        "answer": "false",
        "explanation": "Python is an interpreted language.",
    }


@pytest.fixture
def scenario_valid():
    return {
        "scenario": "A student is debugging a memory leak in a C++ application.",
        "question": "Which tool would best help identify the memory leak?",
        "answer": "Valgrind",
        "concepts_tested": ["memory management", "debugging tools"],
        "explanation": "Valgrind is a tool for memory debugging.",
    }


# ══════════════════════════════════════════════════════════════════════════════
# BaseMetric — interface abstraite
# ══════════════════════════════════════════════════════════════════════════════


class TestBaseMetric:
    """Vérifie que BaseMetric est bien abstraite et que _validate_inputs fonctionne."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            BaseMetric()  # type: ignore

    def test_concrete_subclass_works(self):
        """Une sous-classe concrète doit pouvoir être instanciée."""

        class DummyMetric(BaseMetric):
            @property
            def name(self):
                return "Dummy"

            def compute(self, predictions, references):
                return {"score": 1.0}

        m = DummyMetric()
        assert m.name == "Dummy"
        assert m.compute(["a"], ["b"]) == {"score": 1.0}

    def test_validate_inputs_empty_predictions(self):
        class DummyMetric(BaseMetric):
            @property
            def name(self):
                return "D"

            def compute(self, p, r):
                return {"score": 0.0}

        m = DummyMetric()
        with pytest.raises(ValueError, match="must not be empty"):
            m._validate_inputs([], ["ref"])

    def test_validate_inputs_empty_references(self):
        class DummyMetric(BaseMetric):
            @property
            def name(self):
                return "D"

            def compute(self, p, r):
                return {"score": 0.0}

        m = DummyMetric()
        with pytest.raises(ValueError, match="must not be empty"):
            m._validate_inputs(["pred"], [])

    def test_validate_inputs_length_mismatch(self):
        class DummyMetric(BaseMetric):
            @property
            def name(self):
                return "D"

            def compute(self, p, r):
                return {"score": 0.0}

        m = DummyMetric()
        with pytest.raises(ValueError, match="same length"):
            m._validate_inputs(["a", "b"], ["c"])


# ══════════════════════════════════════════════════════════════════════════════
# BLEUMetric
# ══════════════════════════════════════════════════════════════════════════════


class TestBLEUMetric:

    def test_name(self):
        assert BLEUMetric().name == "BLEU-4"
        assert BLEUMetric(max_n=2).name == "BLEU-2"

    def test_perfect_match(self, perfect_predictions, perfect_references):
        # BLEU-4 cannot score 1.0 on short sentences (< 4 tokens) because
        # 3-gram and 4-gram precisions collapse to 0 — this is a known
        # mathematical property of BLEU. We use BLEU-1 here to test the
        # "perfect match" property in isolation from the n-gram length issue.
        metric = BLEUMetric(max_n=1)
        result = metric.compute(perfect_predictions, perfect_references)
        assert result["score"] == pytest.approx(1.0, abs=0.01)

    def test_perfect_match_bleu4_is_lower_than_1_for_short_sentences(
        self, perfect_predictions, perfect_references
    ):
        # Documents the known BLEU-4 behaviour: identical but short sentences
        # score < 1.0 because higher-order n-grams don't exist.
        # This is expected and correct — not a bug.
        metric = BLEUMetric(max_n=4)
        result = metric.compute(perfect_predictions, perfect_references)
        assert result["score"] > 0.0  # some score
        assert result["score"] <= 1.0  # still bounded
        # bleu_1 should be 1.0 (unigram perfect match)
        assert result["bleu_1"] == pytest.approx(1.0, abs=0.01)

    def test_score_range(self, sample_predictions, sample_references):
        metric = BLEUMetric()
        result = metric.compute(sample_predictions, sample_references)
        assert 0.0 <= result["score"] <= 1.0

    def test_returns_required_keys(self, sample_predictions, sample_references):
        metric = BLEUMetric()
        result = metric.compute(sample_predictions, sample_references)
        assert "score" in result
        for n in range(1, 5):
            assert f"bleu_{n}" in result

    def test_per_order_scores_in_range(self, sample_predictions, sample_references):
        metric = BLEUMetric()
        result = metric.compute(sample_predictions, sample_references)
        for n in range(1, 5):
            assert 0.0 <= result[f"bleu_{n}"] <= 1.0

    def test_partial_overlap_lower_than_perfect(
        self,
        sample_predictions,
        sample_references,
        perfect_predictions,
        perfect_references,
    ):
        metric = BLEUMetric()
        partial = metric.compute(sample_predictions, sample_references)["score"]
        perfect = metric.compute(perfect_predictions, perfect_references)["score"]
        assert partial < perfect

    def test_no_smoothing(self):
        # Phrases quasi-identiques avec ≥ 4 tokens communs à tous les ordres
        # de n-grams — garantit que NLTK ne lève pas de UserWarning sur les
        # 3-grams/4-grams manquants lorsque smoothing=False.
        preds = [
            "the neural network is trained using backpropagation algorithm",
            "the attention mechanism is used in transformer based models",
        ]
        refs = [
            "the neural network is trained using backpropagation algorithm",
            "the attention mechanism is used in transformer based models",
        ]
        metric = BLEUMetric(smoothing=False)
        result = metric.compute(preds, refs)
        assert "score" in result
        assert result["score"] == pytest.approx(1.0, abs=0.01)

    def test_single_pair_bleu1(self):
        # Use BLEU-1 for a 2-token sentence: unigram overlap is perfect.
        metric = BLEUMetric(max_n=1)
        result = metric.compute(["hello world"], ["hello world"])
        assert result["score"] == pytest.approx(1.0, abs=0.01)

    def test_single_pair_bleu4_short_sentence(self):
        # BLEU-4 on a 2-token sentence scores << 1.0 because 3/4-grams are
        # absent — this is mathematically correct behaviour, not a bug.
        # We simply verify the score is positive and bounded.
        metric = BLEUMetric(max_n=4)
        result = metric.compute(["hello world"], ["hello world"])
        assert 0.0 < result["score"] <= 1.0

    def test_single_pair_long_sentence(self):
        # A sentence long enough to produce 4-grams should score ~1.0 on BLEU-4.
        sentence = "the quick brown fox jumps over the lazy dog"
        metric = BLEUMetric(max_n=4)
        result = metric.compute([sentence], [sentence])
        assert result["score"] == pytest.approx(1.0, abs=0.01)

    def test_empty_inputs_raise(self):
        metric = BLEUMetric()
        with pytest.raises(ValueError):
            metric.compute([], [])

    def test_length_mismatch_raises(self):
        metric = BLEUMetric()
        with pytest.raises(ValueError):
            metric.compute(["a", "b"], ["c"])


# ══════════════════════════════════════════════════════════════════════════════
# ROUGE — fonctions internes
# ══════════════════════════════════════════════════════════════════════════════


class TestROUGEInternals:

    def test_ngrams_unigrams(self):
        tokens = ["a", "b", "a"]
        result = _ngrams(tokens, 1)
        assert result[("a",)] == 2
        assert result[("b",)] == 1

    def test_ngrams_bigrams(self):
        tokens = ["a", "b", "c"]
        result = _ngrams(tokens, 2)
        assert result[("a", "b")] == 1
        assert result[("b", "c")] == 1

    def test_ngrams_empty(self):
        assert _ngrams([], 1) == {}

    def test_lcs_identical(self):
        assert _lcs_length(["a", "b", "c"], ["a", "b", "c"]) == 3

    def test_lcs_no_overlap(self):
        assert _lcs_length(["a", "b"], ["c", "d"]) == 0

    def test_lcs_partial(self):
        assert _lcs_length(["a", "b", "c"], ["a", "c"]) == 2

    def test_rouge_n_perfect(self):
        result = _rouge_n("hello world", "hello world", 1)
        assert result["f1"] == pytest.approx(1.0)
        assert result["precision"] == pytest.approx(1.0)
        assert result["recall"] == pytest.approx(1.0)

    def test_rouge_n_no_overlap(self):
        result = _rouge_n("cat sat mat", "dog ran fast", 1)
        assert result["f1"] == pytest.approx(0.0)

    def test_rouge_l_perfect(self):
        result = _rouge_l("the cat sat", "the cat sat")
        assert result["f1"] == pytest.approx(1.0)

    def test_rouge_l_partial(self):
        result = _rouge_l("the cat sat", "the dog sat")
        assert 0.0 < result["f1"] < 1.0


# ══════════════════════════════════════════════════════════════════════════════
# ROUGEMetric
# ══════════════════════════════════════════════════════════════════════════════


class TestROUGEMetric:

    def test_name(self):
        assert ROUGEMetric().name == "ROUGE"

    def test_invalid_variant_raises(self):
        with pytest.raises(ValueError, match="Unknown ROUGE variants"):
            ROUGEMetric(variants=["rouge99"])

    def test_perfect_score(self, perfect_predictions, perfect_references):
        metric = ROUGEMetric()
        result = metric.compute(perfect_predictions, perfect_references)
        assert result["score"] == pytest.approx(1.0)

    def test_score_range(self, sample_predictions, sample_references):
        metric = ROUGEMetric()
        result = metric.compute(sample_predictions, sample_references)
        assert 0.0 <= result["score"] <= 1.0

    def test_returns_all_keys(self, sample_predictions, sample_references):
        metric = ROUGEMetric()
        result = metric.compute(sample_predictions, sample_references)
        expected_keys = [
            "score",
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
        for k in expected_keys:
            assert k in result, f"Missing key: {k}"

    def test_rouge1_only(self, sample_predictions, sample_references):
        metric = ROUGEMetric(variants=["rouge1"])
        result = metric.compute(sample_predictions, sample_references)
        assert "rouge1_f1" in result
        assert result.get("rouge2_f1", 0.0) == 0.0

    def test_primary_score_is_rougeL(self, sample_predictions, sample_references):
        metric = ROUGEMetric()
        result = metric.compute(sample_predictions, sample_references)
        assert result["score"] == result["rougeL_f1"]

    def test_empty_inputs_raise(self):
        with pytest.raises(ValueError):
            ROUGEMetric().compute([], [])

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            ROUGEMetric().compute(["a"], ["b", "c"])


# ══════════════════════════════════════════════════════════════════════════════
# BERTScoreMetric
# ══════════════════════════════════════════════════════════════════════════════


class TestBERTScoreMetric:

    def test_name(self):
        assert BERTScoreMetric().name == "BERTScore"

    def test_default_config(self):
        m = BERTScoreMetric()
        assert m.model_name == "distilbert-base-uncased"
        assert m.batch_size == 16
        assert m._device is None

    def test_custom_config(self):
        m = BERTScoreMetric(model_name="bert-base-uncased", batch_size=8, device="cpu")
        assert m.model_name == "bert-base-uncased"
        assert m.batch_size == 8
        assert m._device == "cpu"

    def test_empty_inputs_raise(self):
        with pytest.raises(ValueError):
            BERTScoreMetric().compute([], [])

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            BERTScoreMetric().compute(["a"], ["b", "c"])

    def test_compute_returns_required_keys(self, sample_predictions, sample_references):
        """Integration test — requiert torch + transformers installés."""
        pytest.importorskip("torch")
        pytest.importorskip("transformers")

        metric = BERTScoreMetric(device="cpu")
        result = metric.compute(sample_predictions, sample_references)

        for key in ("score", "precision", "recall", "f1", "per_sample"):
            assert key in result

    def test_score_range(self, sample_predictions, sample_references):
        pytest.importorskip("torch")
        pytest.importorskip("transformers")

        metric = BERTScoreMetric(device="cpu")
        result = metric.compute(sample_predictions, sample_references)
        assert -1.0 <= result["score"] <= 1.0

    def test_perfect_match_high_score(self, perfect_predictions, perfect_references):
        pytest.importorskip("torch")
        pytest.importorskip("transformers")

        metric = BERTScoreMetric(device="cpu")
        result = metric.compute(perfect_predictions, perfect_references)
        # Identical strings should score very high
        assert result["score"] >= 0.98

    def test_per_sample_length(self, sample_predictions, sample_references):
        pytest.importorskip("torch")
        pytest.importorskip("transformers")

        metric = BERTScoreMetric(device="cpu")
        result = metric.compute(sample_predictions, sample_references)
        assert len(result["per_sample"]) == len(sample_predictions)

    def test_model_lazy_load(self):
        """Le modèle ne doit pas être chargé à l'instanciation."""
        m = BERTScoreMetric()
        assert m._model is None
        assert m._tokenizer is None


# ══════════════════════════════════════════════════════════════════════════════
# QuestionValidator — validate_one
# ══════════════════════════════════════════════════════════════════════════════


class TestQuestionValidatorOne:

    # ── Cas valides ────────────────────────────────────────────────────────────

    def test_valid_default_question(self):
        v = QuestionValidator()
        q = {"question": "What is machine learning?", "answer": "A subset of AI."}
        result = v.validate_one(q)
        assert result.is_valid
        assert result.errors == []

    def test_valid_mcq(self, mcq_valid):
        v = QuestionValidator(question_type="multiple_choice")
        result = v.validate_one(mcq_valid)
        assert result.is_valid

    def test_valid_true_false(self, tf_valid):
        v = QuestionValidator(question_type="true_false")
        result = v.validate_one(tf_valid)
        assert result.is_valid

    def test_valid_scenario(self, scenario_valid):
        v = QuestionValidator(question_type="scenario_based")
        result = v.validate_one(scenario_valid)
        assert result.is_valid

    # ── Champs manquants ───────────────────────────────────────────────────────

    def test_missing_question_field(self):
        v = QuestionValidator()
        result = v.validate_one({"answer": "Some answer"})
        assert not result.is_valid
        assert any("question" in e for e in result.errors)

    def test_missing_answer_field(self):
        v = QuestionValidator()
        result = v.validate_one({"question": "What is Python?"})
        assert not result.is_valid

    def test_missing_options_mcq(self):
        v = QuestionValidator(question_type="multiple_choice")
        q = {"question": "What is ML?", "answer": "A", "explanation": "ok"}
        result = v.validate_one(q)
        assert not result.is_valid
        assert any("options" in e for e in result.errors)

    # ── Question trop courte ───────────────────────────────────────────────────

    def test_question_too_short(self):
        v = QuestionValidator()
        q = {"question": "What?", "answer": "Yes"}  # 1 mot < MIN_QUESTION_WORDS
        result = v.validate_one(q)
        assert not result.is_valid
        assert any("short" in e for e in result.errors)

    def test_question_exactly_min_words(self):
        """Question avec exactement MIN_QUESTION_WORDS mots doit passer."""
        v = QuestionValidator()
        question_text = " ".join(["word"] * MIN_QUESTION_WORDS) + "?"
        q = {"question": question_text, "answer": "answer"}
        result = v.validate_one(q)
        # Pas d'erreur de longueur
        assert not any("short" in e for e in result.errors)

    # ── MCQ — nombre d'options ─────────────────────────────────────────────────

    def test_mcq_wrong_option_count(self):
        v = QuestionValidator(question_type="multiple_choice")
        q = {
            "question": "What is deep learning about?",
            "options": ["A. Neural nets", "B. ML"],  # 2 options au lieu de 4
            "answer": "A",
            "explanation": "Deep learning uses neural networks.",
        }
        result = v.validate_one(q)
        assert not result.is_valid
        assert any(str(MCQ_OPTIONS_COUNT) in e for e in result.errors)

    def test_mcq_exactly_four_options(self, mcq_valid):
        v = QuestionValidator(question_type="multiple_choice")
        result = v.validate_one(mcq_valid)
        assert not any(str(MCQ_OPTIONS_COUNT) in e for e in result.errors)

    # ── True/False — valeurs invalides ─────────────────────────────────────────

    def test_tf_invalid_answer(self):
        v = QuestionValidator(question_type="true_false")
        q = {
            "question": "Is Python compiled language?",
            "answer": "maybe",
            "explanation": "It depends.",
        }
        result = v.validate_one(q)
        assert not result.is_valid
        assert any("true/false" in e.lower() for e in result.errors)

    @pytest.mark.parametrize("answer", ["true", "false", "True", "False", "1", "0"])
    def test_tf_valid_answers(self, answer):
        v = QuestionValidator(question_type="true_false")
        q = {
            "question": "Is Python an interpreted language?",
            "answer": answer,
            "explanation": "Python is interpreted.",
        }
        result = v.validate_one(q)
        assert not any("true/false" in e.lower() for e in result.errors)

    # ── Warnings ───────────────────────────────────────────────────────────────

    def test_warning_no_explanation(self):
        v = QuestionValidator(question_type="multiple_choice")
        q = {
            "question": "What is backpropagation used for?",
            "options": ["A. opt", "B. reg", "C. train", "D. pred"],
            "answer": "C",
        }
        result = v.validate_one(q)
        assert any("explanation" in w.lower() for w in result.warnings)

    def test_warning_question_no_punctuation(self):
        v = QuestionValidator()
        q = {"question": "What is machine learning", "answer": "A subset of AI"}
        result = v.validate_one(q)
        assert any("?" in w or "." in w or ":" in w for w in result.warnings)

    def test_strict_mode_warnings_become_errors(self):
        v = QuestionValidator(strict=True)
        q = {
            "question": "What is machine learning",  # missing punctuation → warning
            "answer": "A subset of AI.",
        }
        result = v.validate_one(q)
        # In strict mode, warnings make is_valid=False
        assert not result.is_valid

    # ── Index ──────────────────────────────────────────────────────────────────

    def test_result_index(self):
        v = QuestionValidator()
        q = {"question": "What is deep learning?", "answer": "A field of ML."}
        result = v.validate_one(q, index=5)
        assert result.index == 5

    # ── to_dict ────────────────────────────────────────────────────────────────

    def test_to_dict_structure(self, mcq_valid):
        v = QuestionValidator(question_type="multiple_choice")
        result = v.validate_one(mcq_valid)
        d = result.to_dict()
        assert set(d.keys()) == {"index", "is_valid", "errors", "warnings"}


# ══════════════════════════════════════════════════════════════════════════════
# QuestionValidator — validate_batch
# ══════════════════════════════════════════════════════════════════════════════


class TestQuestionValidatorBatch:

    def _make_valid(self, question_text: str = "What is machine learning?"):
        return {"question": question_text, "answer": "A subset of AI."}

    def test_empty_batch_returns_zero_counts(self):
        v = QuestionValidator()
        report = v.validate_batch([])
        assert report.total == 0
        assert report.valid_count == 0
        assert report.invalid_count == 0

    def test_all_valid(self):
        v = QuestionValidator()
        questions = [self._make_valid(f"What is concept {i}?") for i in range(5)]
        report = v.validate_batch(questions)
        assert report.valid_count == 5
        assert report.invalid_count == 0
        assert report.validity_pct == 100.0

    def test_all_invalid(self):
        v = QuestionValidator()
        questions = [{"question": "Hi", "answer": ""}] * 3
        report = v.validate_batch(questions)
        # All invalid due to duplicates + short question + empty answer
        assert report.invalid_count > 0

    def test_duplicate_detection(self):
        v = QuestionValidator()
        same_q = self._make_valid("What is deep learning exactly?")
        questions = [
            same_q,
            same_q,
            self._make_valid("How does gradient descent work?"),
        ]
        report = v.validate_batch(questions)
        duplicate_results = [
            r for r in report.results if any("Duplicate" in e for e in r.errors)
        ]
        assert len(duplicate_results) == 1  # second occurrence is invalid

    def test_report_total_count(self):
        v = QuestionValidator()
        questions = [self._make_valid(f"Question number {i}?") for i in range(7)]
        report = v.validate_batch(questions)
        assert report.total == 7

    def test_validity_pct_calculation(self):
        v = QuestionValidator()
        questions = [
            self._make_valid("What is Python used for?"),  # 5 words ✓
            self._make_valid("What is Java mainly used for?"),  # 6 words ✓
            {"question": "Hi", "answer": ""},  # invalid — too short + empty answer
            self._make_valid("What programming language is Rust?"),  # 5 words ✓
        ]
        report = v.validate_batch(questions)
        # 3 valid out of 4 = 75.0%
        assert report.valid_count == 3
        assert report.validity_pct == 75.0

    def test_report_to_dict(self):
        v = QuestionValidator()
        questions = [self._make_valid("What is machine learning?")]
        report = v.validate_batch(questions)
        d = report.to_dict()
        assert set(d.keys()) == {
            "total",
            "valid_count",
            "invalid_count",
            "validity_pct",
            "results",
        }
        assert isinstance(d["results"], list)

    def test_results_length_matches_input(self):
        v = QuestionValidator()
        questions = [self._make_valid(f"Question {i}?") for i in range(4)]
        report = v.validate_batch(questions)
        assert len(report.results) == 4

    def test_mixed_types_in_batch(self):
        """Validator should handle all types without crashing."""
        v = QuestionValidator(question_type="multiple_choice")
        questions = [
            {
                "question": "What is the loss function used for?",
                "options": ["A. Training", "B. Predicting", "C. Both", "D. Neither"],
                "answer": "C",
                "explanation": "Loss functions guide training.",
            },
            {"question": "Bad", "answer": ""},  # invalid
        ]
        report = v.validate_batch(questions)
        assert report.total == 2


# ══════════════════════════════════════════════════════════════════════════════
# ValidationReport — propriétés
# ══════════════════════════════════════════════════════════════════════════════


class TestValidationReport:

    def test_validity_pct_zero_total(self):
        report = ValidationReport(total=0, valid_count=0, invalid_count=0)
        assert report.validity_pct == 0.0

    def test_validity_pct_full(self):
        report = ValidationReport(total=4, valid_count=4, invalid_count=0)
        assert report.validity_pct == 100.0

    def test_validity_pct_partial(self):
        report = ValidationReport(total=10, valid_count=7, invalid_count=3)
        assert report.validity_pct == 70.0


# ══════════════════════════════════════════════════════════════════════════════
# MetricFactory
# ══════════════════════════════════════════════════════════════════════════════


class TestMetricFactory:

    def test_get_bleu(self):
        factory = MetricFactory()
        metric = factory.get_metric("bleu")
        assert isinstance(metric, BLEUMetric)

    def test_get_rouge(self):
        factory = MetricFactory()
        metric = factory.get_metric("rouge")
        assert isinstance(metric, ROUGEMetric)

    def test_get_bertscore(self):
        factory = MetricFactory()
        metric = factory.get_metric("bertscore")
        assert isinstance(metric, BERTScoreMetric)

    def test_case_insensitive(self):
        factory = MetricFactory()
        assert isinstance(factory.get_metric("BLEU"), BLEUMetric)
        assert isinstance(factory.get_metric("Rouge"), ROUGEMetric)
        assert isinstance(factory.get_metric("BERTScore"), BERTScoreMetric)

    def test_unknown_metric_raises(self):
        factory = MetricFactory()
        with pytest.raises(ValueError, match="Unknown metric"):
            factory.get_metric("meteor")

    def test_get_all_metrics(self):
        factory = MetricFactory()
        metrics = factory.get_all_metrics()
        assert len(metrics) == len(METRIC_REGISTRY)
        assert all(isinstance(m, BaseMetric) for m in metrics)

    def test_supported_metrics(self):
        supported = MetricFactory.supported_metrics()
        assert "bleu" in supported
        assert "rouge" in supported
        assert "bertscore" in supported

    def test_get_validator_default(self):
        v = MetricFactory.get_validator()
        assert isinstance(v, QuestionValidator)
        assert v.question_type == "default"
        assert v.strict is False

    def test_get_validator_strict(self):
        v = MetricFactory.get_validator(question_type="multiple_choice", strict=True)
        assert v.question_type == "multiple_choice"
        assert v.strict is True

    def test_kwargs_passed_to_metric(self):
        factory = MetricFactory()
        metric = factory.get_metric("bleu", max_n=2)
        assert metric.max_n == 2

    def test_registry_completeness(self):
        """Chaque entrée du registre doit être une sous-classe de BaseMetric."""
        for name, cls in METRIC_REGISTRY.items():
            assert issubclass(cls, BaseMetric), f"{name} is not a BaseMetric subclass"


# ══════════════════════════════════════════════════════════════════════════════
# Tests d'intégration — pipeline end-to-end
# ══════════════════════════════════════════════════════════════════════════════


class TestEndToEnd:
    """
    Simule un pipeline complet : génération → validation → évaluation.
    Ne requiert pas de vrai modèle de génération.
    """

    GENERATED = [
        "Backpropagation is an algorithm used to train neural networks.",
        "Overfitting occurs when a model performs well on training data but poorly on test data.",
        "The attention mechanism allows models to focus on relevant parts of the input.",
    ]

    REFERENCES = [
        "Backpropagation is the algorithm used for training deep neural networks.",
        "Overfitting is when a model memorizes training data and fails to generalize.",
        "Attention mechanisms enable models to weigh different parts of the input.",
    ]

    QUESTIONS = [
        {
            "question": "What is backpropagation used for?",
            "options": [
                "A. Training",
                "B. Inference",
                "C. Preprocessing",
                "D. Evaluation",
            ],
            "answer": "A",
            "explanation": "Backpropagation adjusts weights during training.",
        },
        {
            "question": "What problem does dropout help prevent?",
            "options": [
                "A. Underfitting",
                "B. Overfitting",
                "C. Slow training",
                "D. High bias",
            ],
            "answer": "B",
            "explanation": "Dropout randomly disables neurons to prevent overfitting.",
        },
    ]

    def test_bleu_rouge_pipeline(self):
        factory = MetricFactory()
        bleu = factory.get_metric("bleu")
        rouge = factory.get_metric("rouge")

        bleu_result = bleu.compute(self.GENERATED, self.REFERENCES)
        rouge_result = rouge.compute(self.GENERATED, self.REFERENCES)

        assert 0.0 <= bleu_result["score"] <= 1.0
        assert 0.0 <= rouge_result["score"] <= 1.0

    def test_validation_pipeline(self):
        validator = MetricFactory.get_validator(question_type="multiple_choice")
        report = validator.validate_batch(self.QUESTIONS)

        assert report.total == 2
        assert report.valid_count == 2
        assert report.validity_pct == 100.0

    def test_all_metrics_pipeline(self):
        factory = MetricFactory()
        all_metrics = factory.get_all_metrics()

        for metric in all_metrics:
            if isinstance(metric, BERTScoreMetric):
                # Skip heavy model unless torch is installed
                try:
                    import torch  # noqa: F401
                    import transformers  # noqa: F401
                except ImportError:
                    continue
            result = metric.compute(self.GENERATED, self.REFERENCES)
            assert "score" in result
            assert isinstance(result["score"], float)
