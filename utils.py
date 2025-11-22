import pypdf

def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file object.
    """
    try:
        pdf_reader = pypdf.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"
