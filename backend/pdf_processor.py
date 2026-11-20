"""Extract text from uploaded contract PDFs."""

from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file: BytesIO) -> str:
    reader = PdfReader(uploaded_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
