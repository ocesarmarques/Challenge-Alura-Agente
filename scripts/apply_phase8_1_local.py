from pathlib import Path
import re

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"

TARGET = "MIN_RELEVANCE_SCORE=0.32"

if not ENV_PATH.exists():
    raise SystemExit(
        "Arquivo .env não encontrado. Execute a partir do projeto ImobIA."
    )

content = ENV_PATH.read_text(encoding="utf-8")

if re.search(r"^MIN_RELEVANCE_SCORE=.*$", content, flags=re.MULTILINE):
    content = re.sub(
        r"^MIN_RELEVANCE_SCORE=.*$",
        TARGET,
        content,
        flags=re.MULTILINE,
    )
else:
    if content and not content.endswith("\n"):
        content += "\n"
    content += TARGET + "\n"

ENV_PATH.write_text(content, encoding="utf-8")
print("[OK] MIN_RELEVANCE_SCORE atualizado para 0.32 em .env")
