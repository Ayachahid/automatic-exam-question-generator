from src.data.loaders.registry import LoaderFactory

def main():
    factory = LoaderFactory()

    # Example: load any file
    file_path = "src/tests/data_tests/example.docx"
    loader = factory.get_loader(file_path)
    content = loader.load(file_path)

    print(f"Content of {file_path}:")
    print(content)

if __name__ == "__main__":
    main()