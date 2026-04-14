import PyPDF2

def load_pdf(file_path):
    with open(file_path,'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text=""
        for page in reader.pages:
            text += page.extract_text()
            
    return text

