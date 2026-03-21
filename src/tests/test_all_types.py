import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generation.pipeline import QuestionGenerationPipeline


def main():
    file = "src/tests/data_tests/sample.txt"
    question_types = ["true_false", "mcq", "short_answer", "essay", "scenario_based"]

    print("Creating pipeline...")
    pipeline = QuestionGenerationPipeline(file_path=file)
    print("Pipeline created.")

    for q_type in question_types:
        print(f"\n--- Testing {q_type} ---")
        try:
            questions = pipeline.run(question_type=q_type)
            print(f"Generated {len(questions)} questions:")
            for q in questions:
                print(q)
        except Exception as e:
            print(f"Error generating {q_type}: {e}")

if __name__ == '__main__':
    main()
