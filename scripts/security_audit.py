from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_TRACKED_NAMES = {
    ".env",
    "oci_api_key.pem",
}

FORBIDDEN_SUFFIXES = {
    ".pem",
    ".key",
}

SECRET_PATTERNS = {
    "private_key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "github_token": re.compile(
        r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"
    ),
    "aws_access_key": re.compile(
        r"\bAKIA[0-9A-Z]{16}\b"
    ),
}

TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".sh", ".ps1", ".example",
}


def is_git_repository() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def git_tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        Path(line)
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def project_files_for_preflight() -> list[Path]:
    return [
        path.relative_to(ROOT)
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".venv" not in path.parts
        and "venv" not in path.parts
        and ".git" not in path.parts
    ]


def main() -> int:
    violations: list[str] = []
    in_git_repo = is_git_repository()

    if in_git_repo:
        files = git_tracked_files()
        mode = "arquivos rastreados pelo Git"
    else:
        files = project_files_for_preflight()
        mode = "arquivos locais (pré-publicação)"

    for rel in files:
        path = ROOT / rel

        # Arquivos sensíveis locais são permitidos antes do clone,
        # pois o script de publicação os exclui via rsync/.gitignore.
        # Eles só bloqueiam a publicação se estiverem realmente rastreados.
        if in_git_repo:
            if rel.name in FORBIDDEN_TRACKED_NAMES:
                violations.append(
                    f"arquivo sensível rastreado: {rel}"
                )

            if rel.suffix.lower() in FORBIDDEN_SUFFIXES:
                violations.append(
                    f"chave potencialmente sensível rastreada: {rel}"
                )

        if not path.exists() or not path.is_file():
            continue

        # Não abre arquivos sensíveis locais na auditoria prévia.
        if not in_git_repo and (
            rel.name == ".env"
            or rel.suffix.lower() in FORBIDDEN_SUFFIXES
        ):
            continue

        if (
            path.suffix.lower() not in TEXT_SUFFIXES
            and path.name not in {".gitignore", ".dockerignore"}
        ):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                violations.append(
                    f"padrão {label} encontrado em {rel}"
                )

    print("=== ImobIA | Auditoria de segurança Git ===")
    print(f"Modo: {mode}")
    print(f"Arquivos avaliados: {len(files)}")

    if not in_git_repo:
        print(
            "[INFO] .env/PEM/KEY locais são permitidos nesta etapa e "
            "serão excluídos da cópia para o GitHub."
        )

    if violations:
        print("\n[ERRO] Publicação bloqueada:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("[OK] Nenhum segredo crítico detectado.")
    if in_git_repo:
        print("[OK] .env, PEM e KEY não estão rastreados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
