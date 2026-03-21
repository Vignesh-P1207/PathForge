"""Text extraction from PDF, DOCX, and TXT files."""

from io import BytesIO


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Extract plain text from an uploaded file based on its extension.

    Args:
        filename: Original filename with extension.
        file_bytes: Raw file content as bytes.

    Returns:
        Extracted plain text string.

    Raises:
        ValueError: If the file type is not supported.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return _extract_docx(file_bytes)
    elif ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Use PDF, DOCX, or TXT.")


def _extract_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF using PyMuPDF."""
    import fitz  # type: ignore  # PyMuPDF

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)


def _extract_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    from docx import Document  # type: ignore

    doc = Document(BytesIO(file_bytes))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)
