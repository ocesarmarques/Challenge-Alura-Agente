import pytest
from app.rag.loader import PageText
from app.rag.chunker import chunk_pages

def test_chunking():
    chunks=chunk_pages([PageText("x.pdf",1,"A"*2000)],500,50)
    assert len(chunks)>1

def test_unique_ids():
    chunks=chunk_pages([PageText("a.pdf",1,"Texto "*300),PageText("b.pdf",1,"Outro "*300)],100,20)
    assert len({c.id for c in chunks})==len(chunks)

def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_pages([PageText("x.pdf",1,"Texto")],100,100)
