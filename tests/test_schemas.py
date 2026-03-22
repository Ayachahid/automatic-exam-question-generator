import pytest
from pydantic import ValidationError
from src.api.schemas.request import GenerateRequest, QuestionType, Difficulty
from src.api.schemas.response import QuestionResponse, GenerationResponse, UploadResponse


class TestQuestionType:
    """Tests for QuestionType enum."""

    def test_question_type_values(self):
        """Test all question type values."""
        assert QuestionType.MULTIPLE_CHOICE.value == "multiple_choice"
        assert QuestionType.SHORT_ANSWER.value == "short_answer"
        assert QuestionType.TRUE_FALSE.value == "true_false"
        assert QuestionType.ESSAY.value == "essay"

    def test_question_type_from_string(self):
        """Test creating QuestionType from string."""
        assert QuestionType("multiple_choice") == QuestionType.MULTIPLE_CHOICE
        assert QuestionType("short_answer") == QuestionType.SHORT_ANSWER

    def test_question_type_invalid(self):
        """Test invalid question type raises error."""
        with pytest.raises(ValueError):
            QuestionType("invalid_type")


class TestDifficulty:
    """Tests for Difficulty enum."""

    def test_difficulty_values(self):
        """Test all difficulty values."""
        assert Difficulty.EASY.value == "easy"
        assert Difficulty.MEDIUM.value == "medium"
        assert Difficulty.HARD.value == "hard"

    def test_difficulty_from_string(self):
        """Test creating Difficulty from string."""
        assert Difficulty("easy") == Difficulty.EASY
        assert Difficulty("hard") == Difficulty.HARD

    def test_difficulty_invalid(self):
        """Test invalid difficulty raises error."""
        with pytest.raises(ValueError):
            Difficulty("impossible")


class TestGenerateRequest:
    """Tests for GenerateRequest schema."""

    def test_generate_request_text_only(self):
        """Test valid request with text only."""
        request = GenerateRequest(text="Test content")
        assert request.text == "Test content"
        assert request.file_path is None
        assert request.question_type == QuestionType.MULTIPLE_CHOICE
        assert request.difficulty == Difficulty.MEDIUM
        assert request.num_questions == 5

    def test_generate_request_file_path_only(self):
        """Test valid request with file_path only."""
        request = GenerateRequest(file_path="data/raw/test.txt")
        assert request.file_path == "data/raw/test.txt"
        assert request.text is None

    def test_generate_request_all_fields(self):
        """Test request with all fields specified."""
        request = GenerateRequest(
            text="Test",
            question_type=QuestionType.ESSAY,
            difficulty=Difficulty.HARD,
            num_questions=10
        )
        assert request.question_type == QuestionType.ESSAY
        assert request.difficulty == Difficulty.HARD
        assert request.num_questions == 10

    def test_generate_request_no_input_raises(self):
        """Test that no input source raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            GenerateRequest()
        assert "file_path" in str(exc_info.value) or "text" in str(exc_info.value)

    def test_generate_request_both_inputs_raises(self):
        """Test that both inputs raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            GenerateRequest(text="Test", file_path="data/raw/test.txt")
        assert "both" in str(exc_info.value).lower() or "Cannot" in str(exc_info.value)

    def test_generate_request_num_questions_min(self):
        """Test minimum num_questions validation."""
        request = GenerateRequest(text="Test", num_questions=1)
        assert request.num_questions == 1

    def test_generate_request_num_questions_max(self):
        """Test maximum num_questions validation."""
        request = GenerateRequest(text="Test", num_questions=50)
        assert request.num_questions == 50

    def test_generate_request_num_questions_below_min_raises(self):
        """Test num_questions below minimum raises error."""
        with pytest.raises(ValidationError):
            GenerateRequest(text="Test", num_questions=0)

    def test_generate_request_num_questions_above_max_raises(self):
        """Test num_questions above maximum raises error."""
        with pytest.raises(ValidationError):
            GenerateRequest(text="Test", num_questions=51)

    def test_generate_request_string_enums(self):
        """Test that string enums are accepted."""
        request = GenerateRequest(
            text="Test",
            question_type="essay",
            difficulty="hard"
        )
        assert request.question_type == QuestionType.ESSAY
        assert request.difficulty == Difficulty.HARD


class TestQuestionResponse:
    """Tests for QuestionResponse schema."""

    def test_question_response_minimal(self):
        """Test minimal question response."""
        q = QuestionResponse(question="Q?", answer="A")
        assert q.question == "Q?"
        assert q.answer == "A"
        assert q.options is None
        assert q.explanation is None

    def test_question_response_with_options(self):
        """Test question response with options."""
        q = QuestionResponse(
            question="Q?",
            answer="B",
            options=["A", "B", "C"]
        )
        assert q.options == ["A", "B", "C"]

    def test_question_response_with_explanation(self):
        """Test question response with explanation."""
        q = QuestionResponse(
            question="Q?",
            answer="A",
            explanation="This is the correct answer because..."
        )
        assert q.explanation == "This is the correct answer because..."

    def test_question_response_full(self):
        """Test full question response."""
        q = QuestionResponse(
            question="What is AI?",
            options=["ML", "AI", "DL"],
            answer="AI",
            explanation="AI stands for Artificial Intelligence"
        )
        assert q.question == "What is AI?"
        assert q.options == ["ML", "AI", "DL"]
        assert q.answer == "AI"
        assert "Artificial Intelligence" in q.explanation

    def test_question_response_answer_int(self):
        """Test question response with integer answer."""
        q = QuestionResponse(
            question="Q?",
            answer=1
        )
        assert q.answer == 1


class TestGenerationResponse:
    """Tests for GenerationResponse schema."""

    def test_generation_response_empty(self):
        """Test response with no questions."""
        r = GenerationResponse(questions=[], total=0)
        assert r.questions == []
        assert r.total == 0

    def test_generation_response_with_questions(self):
        """Test response with questions."""
        r = GenerationResponse(
            questions=[
                QuestionResponse(question="Q1?", answer="A1"),
                QuestionResponse(question="Q2?", answer="A2")
            ],
            total=2
        )
        assert len(r.questions) == 2
        assert r.total == 2

    def test_generation_response_total_matches_questions(self):
        """Test that total matches actual question count."""
        r = GenerationResponse(
            questions=[QuestionResponse(question="Q?", answer="A")],
            total=1
        )
        assert len(r.questions) == r.total


class TestUploadResponse:
    """Tests for UploadResponse schema."""

    def test_upload_response_basic(self):
        """Test basic upload response."""
        r = UploadResponse(
            filename="test.txt",
            file_path="/data/raw/test.txt",
            file_id="uuid-123"
        )
        assert r.filename == "test.txt"
        assert r.file_path == "/data/raw/test.txt"
        assert r.file_id == "uuid-123"

    def test_upload_response_required_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            UploadResponse(filename="test.txt")  # Missing file_path and file_id
