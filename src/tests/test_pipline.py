import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generation.pipeline import QuestionGenerationPipline


def main():
    file = "src/tests/data_tests/sample.txt"

    print("Creating pipeline...")
    pipeline = QuestionGenerationPipline(file_path=file)
    print("Pipeline created.")

    print("Running pipeline...")
    questions = pipeline.run(question_type="true_false")
    print(f"Generated questions:")
    for q in questions:
        print(q)

if __name__ == '__main__':
    main()
