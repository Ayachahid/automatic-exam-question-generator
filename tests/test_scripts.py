import importlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_json = importlib.import_module("json")


# Fixtures partagées


@pytest.fixture
def config_file(tmp_path) -> Path:
    """Minimal valid config.yaml for scripts."""
    content = """
model:
  provider: ollama
  name: llama3.2:1b
  base_url: http://localhost:11434
chunker:
  strategy: fixed_size
  chunk_size: 500
  overlap: 50
generation:
  question_type: short_answer
  difficulty: medium
  num_questions: 3
"""
    path = tmp_path / "config.yaml"
    path.write_text(content)
    return path


@pytest.fixture
def txt_file(tmp_path) -> Path:
    """A simple TXT file for testing loaders."""
    p = tmp_path / "course.txt"
    p.write_text(
        "Deep learning is a subset of machine learning. "
        "It uses neural networks with many layers. "
        "These models learn representations from raw data.",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def questions_json(tmp_path) -> Path:
    """A valid JSON file with generated questions."""
    questions = [
        {
            "question": "What is deep learning?",
            "answer": "A subset of machine learning using neural networks.",
            "explanation": "It relies on multi-layer architectures.",
        },
        {
            "question": "What is a neural network?",
            "answer": "A system inspired by the human brain.",
        },
        {
            "question": "What is backpropagation?",
            "answer": "An algorithm to train neural networks.",
            "explanation": "It computes gradients layer by layer.",
        },
    ]
    path = tmp_path / "questions.json"
    path.write_text(_json.dumps({"total": 3, "questions": questions}), encoding="utf-8")
    return path


# preprocess.py


class TestPreprocessResolveOutputPath:
    """Tests for resolve_output_path() helper."""

    def test_uses_output_arg_when_provided(self, tmp_path):
        from src.scripts.preprocess import resolve_output_path

        result = resolve_output_path("input.txt", str(tmp_path / "out.txt"))
        assert result == tmp_path / "out.txt"

    def test_default_output_from_file_stem(self, tmp_path):
        from src.scripts.preprocess import resolve_output_path

        with patch("src.scripts.preprocess.Path"):
            # Use real Path logic
            pass

        result = resolve_output_path("data/raw/course.pdf", None)
        assert "course" in result.name
        assert result.suffix == ".txt"

    def test_default_output_for_url(self):
        from src.scripts.preprocess import resolve_output_path

        result = resolve_output_path("https://example.com/article", None)
        assert "web_content" in result.name

    def test_output_arg_none_creates_processed_dir(self):
        from src.scripts.preprocess import resolve_output_path

        result = resolve_output_path("notes.txt", None)
        assert "processed" in str(result) or result.suffix == ".txt"


class TestPreprocessMain:
    """Tests for preprocess.main()."""

    def test_returns_1_on_missing_config(self, tmp_path):
        from src.scripts.preprocess import main

        with patch(
            "sys.argv",
            ["preprocess", "--input", "file.txt", "--config", "nonexistent.yaml"],
        ):
            result = main()
        assert result == 1

    def test_returns_1_on_loader_error(self, config_file, tmp_path):
        from src.scripts.preprocess import main

        with patch(
            "sys.argv",
            ["preprocess", "--input", "bad.txt", "--config", str(config_file)],
        ):
            with patch("src.scripts.preprocess.LoaderFactory") as mock_factory:
                mock_factory.return_value.get_loader.return_value.load.side_effect = (
                    Exception("cannot read")
                )
                result = main()

        assert result == 1

    def test_returns_0_on_success(self, config_file, txt_file, tmp_path):
        from src.scripts.preprocess import main

        output_file = tmp_path / "output.txt"

        with patch(
            "sys.argv",
            [
                "preprocess",
                "--input",
                str(txt_file),
                "--output",
                str(output_file),
                "--config",
                str(config_file),
            ],
        ):
            result = main()

        assert result == 0

    def test_output_file_created(self, config_file, txt_file, tmp_path):
        from src.scripts.preprocess import main

        output_file = tmp_path / "out.txt"

        with patch(
            "sys.argv",
            [
                "preprocess",
                "--input",
                str(txt_file),
                "--output",
                str(output_file),
                "--config",
                str(config_file),
            ],
        ):
            main()

        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8").strip() != ""

    def test_output_file_contains_cleaned_text(self, config_file, txt_file, tmp_path):
        from src.scripts.preprocess import main

        output_file = tmp_path / "cleaned.txt"

        with patch(
            "sys.argv",
            [
                "preprocess",
                "--input",
                str(txt_file),
                "--output",
                str(output_file),
                "--config",
                str(config_file),
            ],
        ):
            main()

        content = output_file.read_text(encoding="utf-8")
        assert "deep learning" in content.lower() or "neural" in content.lower()

    def test_strategy_override(self, config_file, txt_file, tmp_path):
        from src.scripts.preprocess import main

        output_file = tmp_path / "out.txt"

        with patch(
            "sys.argv",
            [
                "preprocess",
                "--input",
                str(txt_file),
                "--output",
                str(output_file),
                "--strategy",
                "sentence",
                "--config",
                str(config_file),
            ],
        ):
            result = main()

        assert result == 0

    def test_show_chunks_flag(self, config_file, txt_file, tmp_path, capsys):
        from src.scripts.preprocess import main

        output_file = tmp_path / "out.txt"

        with patch(
            "sys.argv",
            [
                "preprocess",
                "--input",
                str(txt_file),
                "--output",
                str(output_file),
                "--show-chunks",
                "--config",
                str(config_file),
            ],
        ):
            main()

        captured = capsys.readouterr()
        assert "chunk" in captured.out.lower() or "Chunk" in captured.out

    def test_summary_printed_to_stdout(self, config_file, txt_file, tmp_path, capsys):
        from src.scripts.preprocess import main

        output_file = tmp_path / "out.txt"

        with patch(
            "sys.argv",
            [
                "preprocess",
                "--input",
                str(txt_file),
                "--output",
                str(output_file),
                "--config",
                str(config_file),
            ],
        ):
            main()

        captured = capsys.readouterr()
        assert "✅" in captured.out or "Preprocessing" in captured.out


# generate.py


class TestGenerateMain:
    """Tests for generate.main()."""

    def _mock_pipeline(self, questions: list[dict]):
        """Return a mock pipeline that returns given questions."""
        mock = MagicMock()
        mock.run.return_value = questions
        return mock

    def test_returns_1_on_missing_config(self):
        from src.scripts.generate import main

        with patch(
            "sys.argv", ["generate", "--text", "hello", "--config", "nonexistent.yaml"]
        ):
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                side_effect=FileNotFoundError("no config"),
            ):
                result = main()

        assert result == 1

    def test_returns_1_on_pipeline_exception(self, config_file):
        from src.scripts.generate import main

        with patch(
            "sys.argv", ["generate", "--text", "hello", "--config", str(config_file)]
        ):
            mock_pipeline = MagicMock()
            mock_pipeline.run.side_effect = Exception("LLM crashed")
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                return_value=mock_pipeline,
            ):
                result = main()

        assert result == 1

    def test_returns_1_on_file_not_found(self, config_file):
        from src.scripts.generate import main

        with patch(
            "sys.argv",
            ["generate", "--input", "ghost.txt", "--config", str(config_file)],
        ):
            mock_pipeline = MagicMock()
            mock_pipeline.run.side_effect = FileNotFoundError("file missing")
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                return_value=mock_pipeline,
            ):
                result = main()

        assert result == 1

    def test_returns_1_on_empty_questions(self, config_file):
        from src.scripts.generate import main

        with patch(
            "sys.argv", ["generate", "--text", "hello", "--config", str(config_file)]
        ):
            mock_pipeline = self._mock_pipeline([])
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                return_value=mock_pipeline,
            ):
                result = main()

        assert result == 1

    def test_returns_0_on_success_stdout(self, config_file, capsys):
        from src.scripts.generate import main

        questions = [{"question": "Q?", "answer": "A"}]

        with patch(
            "sys.argv", ["generate", "--text", "content", "--config", str(config_file)]
        ):
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                return_value=self._mock_pipeline(questions),
            ):
                result = main()

        assert result == 0
        captured = capsys.readouterr()
        data = _json.loads(captured.out)
        assert "questions" in data
        assert data["total"] == 1

    def test_output_saved_to_file(self, config_file, tmp_path):
        from src.scripts.generate import main

        output_file = tmp_path / "questions.json"
        questions = [{"question": "Q?", "answer": "A"}]

        with patch(
            "sys.argv",
            [
                "generate",
                "--text",
                "content",
                "--output",
                str(output_file),
                "--config",
                str(config_file),
            ],
        ):
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                return_value=self._mock_pipeline(questions),
            ):
                main()

        assert output_file.exists()
        data = _json.loads(output_file.read_text())
        assert data["total"] == 1
        assert data["questions"][0]["question"] == "Q?"

    def test_output_contains_metadata(self, config_file, tmp_path):
        from src.scripts.generate import main

        output_file = tmp_path / "out.json"
        questions = [{"question": "Q?", "answer": "A"}]

        with patch(
            "sys.argv",
            [
                "generate",
                "--text",
                "some content",
                "--type",
                "essay",
                "--difficulty",
                "hard",
                "--num",
                "1",
                "--output",
                str(output_file),
                "--config",
                str(config_file),
            ],
        ):
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                return_value=self._mock_pipeline(questions),
            ):
                main()

        data = _json.loads(output_file.read_text())
        assert data["question_type"] == "essay"
        assert data["difficulty"] == "hard"
        assert data["source"] == "direct text"

    def test_pipeline_called_with_correct_args(self, config_file):
        from src.scripts.generate import main

        questions = [{"question": "Q?", "answer": "A"}]
        mock_pipeline = self._mock_pipeline(questions)

        with patch(
            "sys.argv",
            [
                "generate",
                "--text",
                "my content",
                "--type",
                "true_false",
                "--difficulty",
                "easy",
                "--num",
                "4",
                "--config",
                str(config_file),
            ],
        ):
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                return_value=mock_pipeline,
            ):
                main()

        mock_pipeline.run.assert_called_once_with(
            file_path=None,
            text="my content",
            question_type="true_false",
            difficulty="easy",
            num_questions=4,
        )

    def test_input_file_passed_to_pipeline(self, config_file, txt_file):
        from src.scripts.generate import main

        questions = [{"question": "Q?", "answer": "A"}]
        mock_pipeline = self._mock_pipeline(questions)

        with patch(
            "sys.argv",
            [
                "generate",
                "--input",
                str(txt_file),
                "--config",
                str(config_file),
            ],
        ):
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                return_value=mock_pipeline,
            ):
                main()

        call_kwargs = mock_pipeline.run.call_args.kwargs
        assert call_kwargs["file_path"] == str(txt_file)
        assert call_kwargs["text"] is None

    def test_default_question_type_is_multiple_choice(self, config_file):
        from src.scripts.generate import main

        questions = [{"question": "Q?", "answer": "A"}]
        mock_pipeline = self._mock_pipeline(questions)

        with patch(
            "sys.argv", ["generate", "--text", "content", "--config", str(config_file)]
        ):
            with patch(
                "src.scripts.generate.QuestionGenerationPipeline",
                return_value=mock_pipeline,
            ):
                main()

        call_kwargs = mock_pipeline.run.call_args.kwargs
        assert call_kwargs["question_type"] == "multiple_choice"
        assert call_kwargs["difficulty"] == "medium"
        assert call_kwargs["num_questions"] == 5


# evaluate.py — metric helpers


class TestComputeCompleteness:
    """Tests for compute_completeness()."""

    def test_all_complete(self):
        from src.scripts.evaluate import compute_completeness

        questions = [
            {"question": "Q1?", "answer": "A1"},
            {"question": "Q2?", "answer": "A2"},
        ]
        result = compute_completeness(questions, ["question", "answer"])
        assert result["complete_count"] == 2
        assert result["completeness_pct"] == 100.0

    def test_some_missing(self):
        from src.scripts.evaluate import compute_completeness

        questions = [
            {"question": "Q1?", "answer": "A1"},
            {"question": "Q2?"},  # missing answer
        ]
        result = compute_completeness(questions, ["question", "answer"])
        assert result["complete_count"] == 1
        assert result["completeness_pct"] == 50.0

    def test_all_missing(self):
        from src.scripts.evaluate import compute_completeness

        questions = [{"bad_field": "x"}, {"bad_field": "y"}]
        result = compute_completeness(questions, ["question", "answer"])
        assert result["complete_count"] == 0
        assert result["completeness_pct"] == 0.0

    def test_empty_list(self):
        from src.scripts.evaluate import compute_completeness

        result = compute_completeness([], ["question", "answer"])
        assert result["completeness_pct"] == 0
        assert result["complete_count"] == 0

    def test_missing_fields_tracked_per_question(self):
        from src.scripts.evaluate import compute_completeness

        questions = [{"question": "Q?"}, {"question": "Q?", "answer": "A"}]
        result = compute_completeness(questions, ["question", "answer"])
        assert result["missing_fields_per_question"][0] == ["answer"]
        assert result["missing_fields_per_question"][1] == []


class TestComputeUniqueness:
    """Tests for compute_uniqueness()."""

    def test_all_unique(self):
        from src.scripts.evaluate import compute_uniqueness

        questions = [
            {"question": "What is AI?"},
            {"question": "What is ML?"},
            {"question": "What is DL?"},
        ]
        result = compute_uniqueness(questions)
        assert result["unique_count"] == 3
        assert result["duplicate_count"] == 0
        assert result["uniqueness_pct"] == 100.0

    def test_with_duplicates(self):
        from src.scripts.evaluate import compute_uniqueness

        questions = [
            {"question": "What is AI?"},
            {"question": "What is AI?"},  # duplicate
            {"question": "What is ML?"},
        ]
        result = compute_uniqueness(questions)
        assert result["duplicate_count"] == 1
        assert result["unique_count"] == 2

    def test_case_insensitive_duplicate_detection(self):
        from src.scripts.evaluate import compute_uniqueness

        questions = [
            {"question": "What is AI?"},
            {"question": "WHAT IS AI?"},  # same after lower()
        ]
        result = compute_uniqueness(questions)
        assert result["duplicate_count"] == 1

    def test_empty_list(self):
        from src.scripts.evaluate import compute_uniqueness

        result = compute_uniqueness([])
        assert result["uniqueness_pct"] == 0


class TestComputeAvgLength:
    """Tests for compute_avg_length()."""

    def test_basic_avg(self):
        from src.scripts.evaluate import compute_avg_length

        questions = [
            {"question": "What is AI?"},  # 3 words
            {"question": "Define deep learning"},  # 3 words
        ]
        result = compute_avg_length(questions)
        assert result["avg_words_per_question"] == 3.0

    def test_min_max(self):
        from src.scripts.evaluate import compute_avg_length

        questions = [
            {"question": "Short?"},  # 1 word
            {"question": "This is a much longer question"},  # 6 words
        ]
        result = compute_avg_length(questions)
        assert result["min_words"] == 1
        assert result["max_words"] == 6

    def test_empty_list(self):
        from src.scripts.evaluate import compute_avg_length

        result = compute_avg_length([])
        assert result["avg_words_per_question"] == 0
        assert result["min_words"] == 0
        assert result["max_words"] == 0


class TestComputeEmptyAnswers:
    """Tests for compute_empty_answers()."""

    def test_no_empty_answers(self):
        from src.scripts.evaluate import compute_empty_answers

        questions = [{"answer": "A"}, {"answer": "B"}]
        result = compute_empty_answers(questions)
        assert result["empty_answer_count"] == 0
        assert result["empty_answer_pct"] == 0.0

    def test_some_empty_answers(self):
        from src.scripts.evaluate import compute_empty_answers

        questions = [{"answer": "A"}, {"answer": ""}, {"answer": "  "}]
        result = compute_empty_answers(questions)
        assert result["empty_answer_count"] == 2

    def test_missing_answer_key_counted_as_empty(self):
        from src.scripts.evaluate import compute_empty_answers

        questions = [{"question": "Q?"}]  # no "answer" key
        result = compute_empty_answers(questions)
        assert result["empty_answer_count"] == 1


class TestComputeFieldCoverage:
    """Tests for compute_field_coverage()."""

    def test_optional_fields_counted(self):
        from src.scripts.evaluate import compute_field_coverage

        questions = [
            {"question": "Q?", "answer": "A", "explanation": "Because..."},
            {"question": "Q?", "answer": "A"},
        ]
        result = compute_field_coverage(questions)
        assert result["explanation"]["count"] == 1
        assert result["explanation"]["pct"] == 50.0

    def test_no_optional_fields(self):
        from src.scripts.evaluate import compute_field_coverage

        questions = [{"question": "Q?", "answer": "A"}]
        result = compute_field_coverage(questions)
        for field in ["explanation", "options", "scenario", "concepts_tested"]:
            assert result[field]["count"] == 0
            assert result[field]["pct"] == 0.0


class TestDetectQuestionType:
    """Tests for detect_question_type()."""

    def test_detects_multiple_choice(self):
        from src.scripts.evaluate import detect_question_type

        questions = [{"question": "Q?", "options": ["A", "B"], "answer": "A"}]
        assert detect_question_type(questions) == "multiple_choice"

    def test_detects_scenario_based(self):
        from src.scripts.evaluate import detect_question_type

        questions = [{"scenario": "...", "question": "Q?", "answer": "A"}]
        assert detect_question_type(questions) == "scenario_based"

    def test_defaults_to_default(self):
        from src.scripts.evaluate import detect_question_type

        questions = [{"question": "Q?", "answer": "A"}]
        assert detect_question_type(questions) == "default"

    def test_empty_list_returns_default(self):
        from src.scripts.evaluate import detect_question_type

        assert detect_question_type([]) == "default"


# evaluate.py — main()


class TestEvaluateMain:
    """Integration tests for evaluate.main()."""

    def test_returns_1_on_missing_file(self):
        from src.scripts.evaluate import main

        with patch("sys.argv", ["evaluate", "--input", "nonexistent.json"]):
            result = main()

        assert result == 1

    def test_returns_1_on_invalid_json(self, tmp_path):
        from src.scripts.evaluate import main

        bad_file = tmp_path / "bad.json"
        bad_file.write_text("this is not json", encoding="utf-8")

        with patch("sys.argv", ["evaluate", "--input", str(bad_file)]):
            result = main()

        assert result == 1

    def test_returns_1_on_empty_questions(self, tmp_path):
        from src.scripts.evaluate import main

        empty_file = tmp_path / "empty.json"
        empty_file.write_text(_json.dumps({"questions": []}), encoding="utf-8")

        with patch("sys.argv", ["evaluate", "--input", str(empty_file)]):
            result = main()

        assert result == 1

    def test_returns_0_on_valid_input(self, questions_json):
        from src.scripts.evaluate import main

        with patch("sys.argv", ["evaluate", "--input", str(questions_json)]):
            result = main()

        assert result == 0

    def test_report_printed_to_stdout(self, questions_json, capsys):
        from src.scripts.evaluate import main

        with patch("sys.argv", ["evaluate", "--input", str(questions_json)]):
            main()

        captured = capsys.readouterr()
        assert "Evaluation Report" in captured.out
        assert "3" in captured.out  # total questions

    def test_report_saved_to_file(self, questions_json, tmp_path):
        from src.scripts.evaluate import main

        output_file = tmp_path / "report.json"

        with patch(
            "sys.argv",
            ["evaluate", "--input", str(questions_json), "--output", str(output_file)],
        ):
            main()

        assert output_file.exists()
        report = _json.loads(output_file.read_text())
        assert "completeness" in report
        assert "uniqueness" in report
        assert "avg_length" in report
        assert "empty_answers" in report
        assert "field_coverage" in report

    def test_report_total_matches_questions(self, questions_json, tmp_path):
        from src.scripts.evaluate import main

        output_file = tmp_path / "report.json"

        with patch(
            "sys.argv",
            ["evaluate", "--input", str(questions_json), "--output", str(output_file)],
        ):
            main()

        report = _json.loads(output_file.read_text())
        assert report["summary"]["total_questions"] == 3

    def test_accepts_plain_list_input(self, tmp_path):
        from src.scripts.evaluate import main

        plain_list = tmp_path / "plain.json"
        plain_list.write_text(
            _json.dumps([{"question": "Q?", "answer": "A"}]), encoding="utf-8"
        )

        with patch("sys.argv", ["evaluate", "--input", str(plain_list)]):
            result = main()

        assert result == 0

    def test_question_type_override(self, questions_json, tmp_path):
        from src.scripts.evaluate import main

        output_file = tmp_path / "report.json"

        with patch(
            "sys.argv",
            [
                "evaluate",
                "--input",
                str(questions_json),
                "--type",
                "essay",
                "--output",
                str(output_file),
            ],
        ):
            main()

        report = _json.loads(output_file.read_text())
        assert report["question_type"] == "essay"

    def test_verbose_flag_shows_per_question(self, questions_json, capsys):
        from src.scripts.evaluate import main

        with patch(
            "sys.argv",
            ["evaluate", "--input", str(questions_json), "--verbose"],
        ):
            main()

        captured = capsys.readouterr()
        assert "Q01" in captured.out or "Q1" in captured.out

    def test_report_does_not_contain_missing_fields_detail(
        self, questions_json, tmp_path
    ):
        """Saved report should not contain verbose per-question missing_fields list."""
        from src.scripts.evaluate import main

        output_file = tmp_path / "report.json"

        with patch(
            "sys.argv",
            ["evaluate", "--input", str(questions_json), "--output", str(output_file)],
        ):
            main()

        report = _json.loads(output_file.read_text())
        assert "missing_fields_per_question" not in report.get("completeness", {})
