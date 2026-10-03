from pathlib import Path
from tempfile import TemporaryDirectory

from backend.tools.pdf_tool import index_pdf_file


def index_pdf(file_name: str, file_content: bytes) -> int:
    if Path(file_name).suffix.casefold() != ".pdf":
        raise ValueError("Only PDF files can be indexed.")
    if not file_content:
        raise ValueError("The uploaded PDF is empty.")

    with TemporaryDirectory(prefix="researchpilot-") as temp_dir:
        pdf_path = Path(temp_dir) / "upload.pdf"
        pdf_path.write_bytes(file_content)
        return index_pdf_file(pdf_path, source_name=file_name)
