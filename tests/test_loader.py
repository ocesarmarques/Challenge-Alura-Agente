from pathlib import Path
from app.config import DOCUMENTS_DIR
from app.rag.loader import load_documents

def test_base_contains_five_pdfs():
    assert len(list(Path(DOCUMENTS_DIR).glob("*.pdf")))==5

def test_load_documents():
    pages=load_documents(DOCUMENTS_DIR)
    assert pages and all(p.text for p in pages)
