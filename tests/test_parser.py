import pytest
from src.generation.parser import QuestionParser


class TestQuestionParser:
    """Tests for QuestionParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QuestionParser()

    def test_parse_clean_json_array(self):
        """Test parsing clean JSON array."""
        raw = '[{"question": "Q1?", "answer": "A1"}]'
        result = self.parser.parse(raw)

        assert len(result) == 1
        assert result[0]["question"] == "Q1?"
        assert result[0]["answer"] == "A1"

    def test_parse_clean_json_object(self):
        """Test parsing single JSON object (wrapped in list)."""
        raw = '{"question": "Q1?", "answer": "A1"}'
        result = self.parser.parse(raw)

        assert len(result) == 1
        assert result[0]["question"] == "Q1?"

    def test_parse_with_markdown_fences(self):
        """Test parsing JSON with markdown code fences."""
        raw = '''```json
[{"question": "Q1?", "answer": "A1"}]
```'''
        result = self.parser.parse(raw)

        assert len(result) == 1
        assert result[0]["question"] == "Q1?"

    def test_parse_with_text_before_json(self):
        """Test parsing JSON embedded in text."""
        raw = '''Here are the questions:
[{"question": "Q1?", "answer": "A1"}, {"question": "Q2?", "answer": "A2"}]
Hope this helps!'''
        result = self.parser.parse(raw)

        assert len(result) == 2
        assert result[0]["question"] == "Q1?"
        assert result[1]["question"] == "Q2?"

    def test_parse_with_multiple_choice_options(self):
        """Test parsing questions with options."""
        raw = '''[{"question": "What is 2+2?", "answer": "4", "options": ["3", "4", "5"]}]'''
        result = self.parser.parse(raw)

        assert len(result) == 1
        assert result[0]["options"] == ["3", "4", "5"]

    def test_parse_with_explanation(self):
        """Test parsing questions with explanations."""
        raw = '''[{"question": "Q?", "answer": "A", "explanation": "Because..."}]'''
        result = self.parser.parse(raw)

        assert len(result) == 1
        assert result[0]["explanation"] == "Because..."

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = self.parser.parse("")
        assert result == []

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON returns empty list."""
        raw = "This is not JSON at all"
        result = self.parser.parse(raw)
        assert result == []

    def test_parse_malformed_json(self):
        """Test parsing malformed JSON returns empty list."""
        raw = '{"question": "Q1?", "answer":}'
        result = self.parser.parse(raw)
        assert result == []

    def test_parse_multiple_questions(self):
        """Test parsing multiple questions."""
        raw = '''
        [
            {"question": "Q1?", "answer": "A1"},
            {"question": "Q2?", "answer": "A2"},
            {"question": "Q3?", "answer": "A3"}
        ]
        '''
        result = self.parser.parse(raw)

        assert len(result) == 3
        assert result[0]["question"] == "Q1?"
        assert result[1]["question"] == "Q2?"
        assert result[2]["question"] == "Q3?"

    def test_parse_complex_json(self):
        """Test parsing complex question structure."""
        raw = '''
        [{
            "question": "What is AI?",
            "answer": "Artificial Intelligence",
            "options": ["ML", "AI", "DL"],
            "explanation": "AI stands for Artificial Intelligence",
            "difficulty": "easy"
        }]
        '''
        result = self.parser.parse(raw)

        assert len(result) == 1
        assert result[0]["question"] == "What is AI?"
        assert result[0]["answer"] == "Artificial Intelligence"
        assert result[0]["options"] == ["ML", "AI", "DL"]
        assert result[0]["explanation"] == "AI stands for Artificial Intelligence"
        assert result[0]["difficulty"] == "easy"

    def test_parse_json_with_special_characters(self):
        """Test parsing JSON with special characters."""
        raw = '''[{"question": "What is café?", "answer": "A café is..."}]'''
        result = self.parser.parse(raw)

        assert len(result) == 1
        assert "café" in result[0]["question"]

    def test_parse_json_with_newlines_in_values(self):
        """Test parsing JSON with newlines in values."""
        raw = '''[{"question": "Q?", "answer": "Line1\\nLine2"}]'''
        result = self.parser.parse(raw)

        assert len(result) == 1
        assert "\n" in result[0]["answer"]
