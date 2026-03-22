import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.schemas.request import QuestionType, Difficulty
from src.api.dependencies import get_pipeline


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_pipeline():
    """Mock pipeline for generate endpoint."""
    pipeline = MagicMock()
    app.dependency_overrides[get_pipeline] = lambda: pipeline
    yield pipeline
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "components" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_welcome(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Welcome" in data["message"]


class TestUploadEndpoint:
    """Tests for file upload endpoint."""

    def test_upload_txt_file(self, client, tmp_path):
        """Test uploading a TXT file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/upload/",
                files={"file": ("test.txt", f, "text/plain")}
            )

        assert response.status_code == 201
        data = response.json()
        assert "filename" in data
        assert data["filename"] == "test.txt"
        assert "file_path" in data
        assert "file_id" in data

    def test_upload_pdf_file(self, client, tmp_path):
        """Test uploading a PDF file."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake pdf")

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/upload/",
                files={"file": ("test.pdf", f, "application/pdf")}
            )

        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.pdf"

    def test_upload_docx_file(self, client, tmp_path):
        """Test uploading a DOCX file."""
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"PK fake docx")

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/upload/",
                files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            )

        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.docx"

    def test_upload_unsupported_extension(self, client, tmp_path):
        """Test uploading unsupported file type."""
        test_file = tmp_path / "test.xyz"
        test_file.write_text("Test content")

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/upload/",
                files={"file": ("test.xyz", f, "application/octet-stream")}
            )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not supported" in data["detail"]

    def test_upload_generates_unique_id(self, client, tmp_path):
        """Test that each upload gets a unique file ID."""
        test_file1 = tmp_path / "test1.txt"
        test_file2 = tmp_path / "test2.txt"
        test_file1.write_text("Content 1")
        test_file2.write_text("Content 2")

        with open(test_file1, "rb") as f1:
            response1 = client.post(
                "/api/v1/upload/",
                files={"file": ("test1.txt", f1, "text/plain")}
            )

        with open(test_file2, "rb") as f2:
            response2 = client.post(
                "/api/v1/upload/",
                files={"file": ("test2.txt", f2, "text/plain")}
            )

        assert response1.json()["file_id"] != response2.json()["file_id"]

    def test_upload_file_saved_to_data_raw(self, client, tmp_path):
        """Test that files are saved to data/raw directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/upload/",
                files={"file": ("test.txt", f, "text/plain")}
            )

        data = response.json()
        # Check for data/raw in path (works on both Windows and Unix)
        assert "data" in data["file_path"]
        assert "raw" in data["file_path"]


class TestGenerateEndpoint:
    """Tests for question generation endpoint."""

    def test_generate_from_text(self, client, mock_pipeline):
        """Test generating questions from text input."""
        mock_pipeline.run.return_value = [
            {"question": "Q1?", "answer": "A1"}
        ]

        response = client.post(
            "/api/v1/generate/",
            json={
                "text": "Test content",
                "question_type": "short_answer",
                "difficulty": "medium",
                "num_questions": 1
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert data["total"] == 1

    def test_generate_from_file_path(self, client, mock_pipeline):
        """Test generating questions from file path."""
        mock_pipeline.run.return_value = [
            {"question": "Q1?", "answer": "A1", "options": ["A", "B"]}
        ]

        response = client.post(
            "/api/v1/generate/",
            json={
                "file_path": "data/raw/test.txt",
                "question_type": "multiple_choice",
                "difficulty": "easy",
                "num_questions": 5
            }
        )

        assert response.status_code == 200
        mock_pipeline.run.assert_called_with(
            file_path="data/raw/test.txt",
            text=None,
            question_type="multiple_choice",
            difficulty="easy",
            num_questions=5
        )

    def test_generate_default_values(self, client, mock_pipeline):
        """Test default values for generation parameters."""
        mock_pipeline.run.return_value = []

        response = client.post(
            "/api/v1/generate/",
            json={"text": "Test content"}
        )

        assert response.status_code == 200
        mock_pipeline.run.assert_called_with(
            file_path=None,
            text="Test content",
            question_type="multiple_choice",  # Default
            difficulty="medium",  # Default
            num_questions=5  # Default
        )

    def test_generate_file_not_found(self, client, mock_pipeline):
        """Test 404 when file not found."""
        mock_pipeline.run.side_effect = FileNotFoundError("File not found")

        response = client.post(
            "/api/v1/generate/",
            json={"file_path": "nonexistent.txt", "text": None}
        )

        assert response.status_code == 404

    def test_generate_pipeline_error(self, client, mock_pipeline):
        """Test 500 on pipeline error."""
        mock_pipeline.run.side_effect = Exception("Pipeline failed")

        response = client.post(
            "/api/v1/generate/",
            json={"text": "Test content"}
        )

        assert response.status_code == 500
        data = response.json()
        assert "Pipeline error" in data["detail"]

    def test_generate_no_input_source(self, client, mock_pipeline):
        """Test validation error when no input source."""
        response = client.post(
            "/api/v1/generate/",
            json={}
        )

        assert response.status_code == 422  # Validation error

    def test_generate_both_inputs(self, client, mock_pipeline):
        """Test validation error when both inputs provided."""
        response = client.post(
            "/api/v1/generate/",
            json={
                "file_path": "test.txt",
                "text": "Some text"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_generate_all_question_types(self, client, mock_pipeline):
        """Test all question types."""
        mock_pipeline.run.return_value = []

        for q_type in ["multiple_choice", "short_answer", "true_false", "essay"]:
            response = client.post(
                "/api/v1/generate/",
                json={
                    "text": "Test",
                    "question_type": q_type,
                    "num_questions": 1
                }
            )
            assert response.status_code == 200

    def test_generate_all_difficulties(self, client, mock_pipeline):
        """Test all difficulty levels."""
        mock_pipeline.run.return_value = []

        for diff in ["easy", "medium", "hard"]:
            response = client.post(
                "/api/v1/generate/",
                json={
                    "text": "Test",
                    "difficulty": diff,
                    "num_questions": 1
                }
            )
            assert response.status_code == 200

    def test_generate_num_questions_bounds(self, client, mock_pipeline):
        """Test num_questions validation bounds."""
        mock_pipeline.run.return_value = []

        # Valid: minimum
        response = client.post(
            "/api/v1/generate/",
            json={"text": "Test", "num_questions": 1}
        )
        assert response.status_code == 200

        # Valid: maximum
        response = client.post(
            "/api/v1/generate/",
            json={"text": "Test", "num_questions": 50}
        )
        assert response.status_code == 200

        # Invalid: below minimum
        response = client.post(
            "/api/v1/generate/",
            json={"text": "Test", "num_questions": 0}
        )
        assert response.status_code == 422

        # Invalid: above maximum
        response = client.post(
            "/api/v1/generate/",
            json={"text": "Test", "num_questions": 51}
        )
        assert response.status_code == 422

    def test_generate_response_format(self, client, mock_pipeline):
        """Test response format is correct."""
        mock_pipeline.run.return_value = [
            {
                "question": "What is AI?",
                "answer": "Artificial Intelligence",
                "options": ["ML", "AI", "DL"],
                "explanation": "AI stands for Artificial Intelligence"
            }
        ]

        response = client.post(
            "/api/v1/generate/",
            json={"text": "Test", "num_questions": 1}
        )

        data = response.json()
        assert "questions" in data
        assert "total" in data
        assert len(data["questions"]) == 1
        q = data["questions"][0]
        assert "question" in q
        assert "answer" in q
        assert "options" in q
        assert "explanation" in q


class TestAPIIntegration:
    """Integration tests for API."""

    def test_upload_then_generate(self, client, mock_pipeline, tmp_path):
        """Test full flow: upload file then generate questions."""
        # Upload
        test_file = tmp_path / "course.txt"
        test_file.write_text("Deep Learning content")

        with open(test_file, "rb") as f:
            upload_response = client.post(
                "/api/v1/upload/",
                files={"file": ("course.txt", f, "text/plain")}
            )

        assert upload_response.status_code == 201
        file_path = upload_response.json()["file_path"]

        # Generate
        mock_pipeline.run.return_value = [
            {"question": "Q about DL?", "answer": "A"}
        ]

        generate_response = client.post(
            "/api/v1/generate/",
            json={"file_path": file_path, "num_questions": 1}
        )

        assert generate_response.status_code == 200
        assert generate_response.json()["total"] == 1
