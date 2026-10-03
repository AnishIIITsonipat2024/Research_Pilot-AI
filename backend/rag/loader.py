from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_pdf(file_path):
    path = Path(file_path)
    if path.suffix.casefold() != ".pdf":
        raise ValueError(f"Expected a PDF file, received: {path.name}")

    return PyPDFLoader(str(path)).load()