from pdfminer.high_level import extract_text
from docx import Document
import tempfile
import os
def extract_text_from_pdf(file):
    # Read the content of the InMemoryUploadedFile into memory
    content = file.read()
    
    # Create a temporary file to store the content
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(content)
        temp_file_name = temp_file.name
    
    try:
        # Pass the temporary file name to the extract_text function
        return extract_text(temp_file_name)
    finally:
        # Clean up: remove the temporary file
        os.unlink(temp_file_name)

def extract_text_from_docx(file):
    doc = Document(file)
    return " ".join(paragraph.text for paragraph in doc.paragraphs)

def process_uploaded_resume(file, file_type):
    text = ''
    if file_type == 'application/pdf':
        text = extract_text_from_pdf(file)
    elif file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
        text = extract_text_from_docx(file)
    return text
