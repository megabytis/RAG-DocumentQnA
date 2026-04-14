from docx import Document


def load_docx(file_path):
    with open(file_path, "rb") as f:
        doc = Document(f)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)

    return full_text
