import pytest
from src.generation.prompter import Prompter


class TestPrompter:
    """Tests for Prompter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.prompter = Prompter()

    def test_build_prompt_short_answer(self):
        """Test building prompt for short answer questions."""
        chunk = "Deep Learning is a subset of machine learning."
        prompt = self.prompter.build_prompt(
            chunk=chunk,
            question_type="short_answer",
            difficulty="medium",
            num_questions=3
        )

        assert "Deep Learning" in prompt
        assert "medium" in prompt
        assert "3" in prompt

    def test_build_prompt_multiple_choice(self):
        """Test building prompt for multiple choice questions."""
        chunk = "Python is a programming language."
        prompt = self.prompter.build_prompt(
            chunk=chunk,
            question_type="multiple_choice",
            difficulty="easy",
            num_questions=5
        )

        assert "Python" in prompt
        assert "easy" in prompt
        assert "5" in prompt

    def test_build_prompt_true_false(self):
        """Test building prompt for true/false questions."""
        chunk = "The sky is blue."
        prompt = self.prompter.build_prompt(
            chunk=chunk,
            question_type="true_false",
            difficulty="easy",
            num_questions=10
        )

        assert "sky" in prompt
        assert "10" in prompt

    def test_build_prompt_essay(self):
        """Test building prompt for essay questions."""
        chunk = "Climate change affects the environment."
        prompt = self.prompter.build_prompt(
            chunk=chunk,
            question_type="essay",
            difficulty="hard",
            num_questions=2
        )

        assert "Climate change" in prompt
        assert "hard" in prompt

    def test_build_prompt_scenario_based(self):
        """Test building prompt for scenario-based questions."""
        chunk = "A patient comes to the emergency room."
        prompt = self.prompter.build_prompt(
            chunk=chunk,
            question_type="scenario_based",
            difficulty="hard",
            num_questions=1
        )

        assert "patient" in prompt
        assert "emergency" in prompt

    def test_build_prompt_unknown_type_fallback(self):
        """Test that unknown question type falls back to file name."""
        chunk = "Test content."
        # This should raise FileNotFoundError since no prompt file exists for unknown type
        with pytest.raises(FileNotFoundError):
            self.prompter.build_prompt(
                chunk=chunk,
                question_type="unknown_type",
                difficulty="medium",
                num_questions=1
            )

    def test_build_prompt_preserves_chunk(self):
        """Test that the entire chunk is included in the prompt."""
        chunk = "This is a very specific and unique piece of text for testing."
        prompt = self.prompter.build_prompt(
            chunk=chunk,
            question_type="short_answer",
            difficulty="medium",
            num_questions=1
        )

        assert chunk in prompt

    def test_build_prompt_injects_all_parameters(self):
        """Test that all parameters are correctly injected."""
        chunk = "Test"
        prompt = self.prompter.build_prompt(
            chunk=chunk,
            question_type="short_answer",
            difficulty="hard",
            num_questions=7
        )

        assert "hard" in prompt
        assert "7" in prompt
        assert "Test" in prompt

    def test_prompt_caching(self):
        """Test that templates are cached after first load."""
        chunk = "Test content."
        # First call loads template
        self.prompter.build_prompt(
            chunk=chunk,
            question_type="short_answer",
            difficulty="medium",
            num_questions=1
        )

        # Template should now be cached
        assert "short_answer" in self.prompter._templates

        # Second call should use cached template
        prompt2 = self.prompter.build_prompt(
            chunk=chunk,
            question_type="short_answer",
            difficulty="easy",
            num_questions=2
        )

        assert "easy" in prompt2
        assert "2" in prompt2

    def test_build_prompt_question_type_with_spaces(self):
        """Test handling of question types with spaces."""
        chunk = "Test."
        prompt = self.prompter.build_prompt(
            chunk=chunk,
            question_type="Scenario Based",
            difficulty="medium",
            num_questions=1
        )

        assert "Scenario Based".lower().replace(" ", "_") in prompt or "scenario" in prompt.lower()

    def test_build_prompt_question_type_uppercase(self):
        """Test handling of uppercase question types."""
        chunk = "Test."
        prompt = self.prompter.build_prompt(
            chunk=chunk,
            question_type="SHORT_ANSWER",
            difficulty="medium",
            num_questions=1
        )

        # The prompt should contain "short answer" (lowercase from template)
        assert "short answer" in prompt.lower()

    def test_multiple_build_prompts_same_type(self):
        """Test building multiple prompts of the same type."""
        chunk1 = "First chunk."
        chunk2 = "Second chunk."

        prompt1 = self.prompter.build_prompt(
            chunk=chunk1,
            question_type="short_answer",
            difficulty="easy",
            num_questions=1
        )

        prompt2 = self.prompter.build_prompt(
            chunk=chunk2,
            question_type="short_answer",
            difficulty="hard",
            num_questions=5
        )

        assert "First chunk." in prompt1
        assert "Second chunk." in prompt2
        assert "easy" in prompt1
        assert "hard" in prompt2
