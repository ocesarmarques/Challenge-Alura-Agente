from app.rag.pipeline import build_document_chunks

def test_pipeline():
    pages,chunks=build_document_chunks()
    assert len(pages)>0 and len(chunks)>0
