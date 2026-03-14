from docx import Document
from docx import Document
from pathlib import Path

# import your DOCXLoader
from docx import Document
from .docx import DOCXLoader  # relative import from loaders folder

def main():
    loader = DOCXLoader()

    file_path = Path(r"C:/Users/hp/Desktop/maths pr ia/maths1/lab\Lab 3.docx")

    text = loader.load(file_path)
    print(text)


if __name__ == "__main__":
    main()