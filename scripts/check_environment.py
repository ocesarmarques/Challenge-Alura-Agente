from __future__ import annotations

import importlib.util
from pathlib import Path
import platform
import sys

from app.config import DOCUMENTS_DIR, ROOT_DIR


REQUIRED_IMPORTS = {
    "streamlit": "streamlit",
    "fitz (PyMuPDF)": "fitz",
    "dotenv": "dotenv",
    "numpy": "numpy",
    "faiss": "faiss",
    "oci": "oci",
    "pytest": "pytest",
}


def ok(label: str, detail: str = "") -> None:
    suffix = f" — {detail}" if detail else ""
    print(f"[OK] {label}{suffix}")


def fail(label: str, detail: str = "") -> None:
    suffix = f" — {detail}" if detail else ""
    print(f"[ERRO] {label}{suffix}")


def main() -> int:
    errors = 0

    print("=== ImobIA | Verificação do ambiente ===")
    print(f"Sistema: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Projeto: {ROOT_DIR}")
    print()

    if sys.version_info >= (3, 12):
        ok("Python", "3.12 ou superior")
    else:
        fail("Python", "use Python 3.12 ou superior")
        errors += 1

    for label, module in REQUIRED_IMPORTS.items():
        if importlib.util.find_spec(module) is not None:
            ok(f"Pacote {label}")
        else:
            fail(
                f"Pacote {label}",
                "instale com: python -m pip install -r requirements.txt",
            )
            errors += 1

    pdfs = sorted(Path(DOCUMENTS_DIR).glob("*.pdf"))
    if len(pdfs) == 5:
        ok("Base documental", "5 PDFs encontrados")
    else:
        fail("Base documental", f"esperados 5 PDFs; encontrados {len(pdfs)}")
        errors += 1

    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        ok("Arquivo .env")
    else:
        fail(
            "Arquivo .env",
            "copie .env.example para .env e preencha OCI_COMPARTMENT_ID",
        )
        errors += 1

    print()
    if errors:
        print(f"RESULTADO: {errors} pendência(s) encontrada(s).")
        return 1

    print("RESULTADO: ambiente local pronto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
