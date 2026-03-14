from docx import Document
from docx import Document
from pathlib import Path

# import your DOCXLoader
from docx import Document
from .docx import DOCXLoader  # relative import from loaders folder

def main():
    loader = DOCXLoader()

    # replace with the path to a real docx file on your computer
    file_path = Path("C:/Users/hp/automatic-exam-question-generator/sample.docx")

    text = loader.load(file_path)
    print(text)


if __name__ == "__main__":
    main()