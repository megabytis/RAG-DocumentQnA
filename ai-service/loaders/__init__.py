from .pdf_loader import load_pdf
from .text_loader import load_text
from .doc_loader import load_docx


def load_file(file_path, file_type):
    if file_type == ".pdf":
        return load_pdf(file_path)
    elif file_type == ".txt":
        return load_text(file_path)
    elif file_type == ".docx":
        return load_docx(file_path)
