from pathlib import Path

from backend.rag.loader import load_pdf
from backend.rag.splitter import split_documents
from backend.rag.vectorstore import create_vectorstore


def index_pdf_file(file_path: str | Path, source_name: str | None = None) -> int:
    documents = load_pdf(file_path)
    if not documents:
        raise ValueError("The PDF did not contain any readable pages.")

    source = source_name or Path(file_path).name
    for document in documents:
        document.metadata["source"] = Path(source).name

    chunks = split_documents(documents)
    if not chunks:
        raise ValueError("No text could be extracted from the PDF.")

    create_vectorstore(chunks)
    return len(chunks)
