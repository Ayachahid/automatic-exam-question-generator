import sys
from pathlib import Path

# THIS must come before any src.* import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generation.pipeline import QuestionGenerationPipline


def main():
    file = "src/tests/data_tests/sample.txt"

    print("Creating pipeline...")
    pipeline = QuestionGenerationPipline(file_path=file)
    print("Pipeline created.")

    print("Running pipeline...")
    questions = pipeline.run(question_type="short answer")
    print(f"Generated questions:")
    print(questions)

if __name__ == '__main__':
    main()
