import PyPDF2

def read_pdf(file_path):
    """Extracts text from a PDF file"""
    try:
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            
            # Read all pages (or limit to first 20 to save speed)
            for page in reader.pages[:20]: 
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        # Limit text to 20,000 characters so we don't crash the AI memory
        return text[:20000]
    except Exception as e:
        return None