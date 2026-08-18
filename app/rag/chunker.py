from dataclasses import dataclass
from .loader import PageText

@dataclass
class Chunk:
    id: str
    document: str
    page: int
    text: str

def normalize_text(text:str)->str:
    return " ".join(text.split())

def chunk_pages(pages:list[PageText],chunk_size:int=900,overlap:int=120)->list[Chunk]:
    if chunk_size<=0: raise ValueError("chunk_size deve ser maior que zero")
    if overlap<0 or overlap>=chunk_size: raise ValueError("overlap inválido")
    chunks=[]
    for page in pages:
        text=normalize_text(page.text)
        start=index=0
        while start<len(text):
            end=min(start+chunk_size,len(text))
            piece=text[start:end].strip()
            if piece:
                chunks.append(Chunk(f"{page.document}:p{page.page}:c{index}",page.document,page.page,piece))
            if end>=len(text): break
            start=end-overlap; index+=1
    return chunks
