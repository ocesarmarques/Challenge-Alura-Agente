from dataclasses import dataclass
from pathlib import Path
import pymupdf

@dataclass
class PageText:
    document: str
    page: int
    text: str

def load_pdf(pdf_path: str | Path) -> list[PageText]:
    path=Path(pdf_path)
    if not path.exists(): raise FileNotFoundError(f"PDF não encontrado: {path}")
    if path.suffix.lower()!=".pdf": raise ValueError("O arquivo precisa ser PDF")
    pages=[]
    with pymupdf.open(path) as doc:
        for n,page in enumerate(doc,start=1):
            text=page.get_text("text").strip()
            if text: pages.append(PageText(path.name,n,text))
    return pages

def load_documents(directory: str | Path) -> list[PageText]:
    directory=Path(directory)
    pdfs=sorted(directory.glob("*.pdf"))
    if not pdfs: raise FileNotFoundError(f"Nenhum PDF encontrado em {directory}")
    pages=[]
    for pdf in pdfs: pages.extend(load_pdf(pdf))
    return pages
