from pathlib import Path
from app.config import DOCUMENTS_DIR, settings
from .loader import load_documents
from .chunker import chunk_pages

def build_document_chunks(documents_dir:str|Path=DOCUMENTS_DIR):
    pages=load_documents(documents_dir)
    return pages, chunk_pages(pages,settings.chunk_size,settings.chunk_overlap)
