import sys
from pathlib import Path

# THIS must come before any src.* import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generation.pipeline import QuestionGenerationPipline


def main():
    file = "src/tests/data_tests/sample.txt"

    print("Creating pipeline...")
    pipeline = QuestionGenerationPipline()
    print("Pipeline created.")
    
    print(f"Loading file: {file}")
    pipeline.put_file_path(file)
    print("File path set.")
    
    print("Running pipeline...")
    questions = pipeline.run(file, question_type="multiple_choice", difficulty="easy", num_questions=2)
    print(f"Generated {len(questions)} questions")

    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q}")

if __name__ == '__main__':
    main()
