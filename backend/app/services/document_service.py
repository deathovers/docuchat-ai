import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_pdf(file_content: bytes, filename: str, session_id: str):
    doc = fitz.open(stream=file_content, filetype="pdf")
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    full_text_found = False
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            full_text_found = True
            # Split text within the page to keep metadata accurate
            page_chunks = text_splitter.split_text(text)
            for chunk in page_chunks:
                chunks.append({
                    "text": chunk,
                    "metadata": {
                        "session_id": session_id,
                        "filename": filename,
                        "page_number": page_num + 1
                    }
                })
    
    if not full_text_found:
        raise ValueError("No text found in PDF (OCR not supported)")
        
    return chunks
