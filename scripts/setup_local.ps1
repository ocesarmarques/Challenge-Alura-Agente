$ErrorActionPreference = "Stop"

Write-Host "=== ImobIA | Setup local Windows PowerShell ==="

if (-not (Test-Path ".venv")) {
    py -3.12 -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "Arquivo .env criado."
    Write-Host "Abra o .env e preencha OCI_COMPARTMENT_ID antes de continuar."
}

Write-Host ""
Write-Host "Setup concluído."
Write-Host "Próximo comando: python scripts/check_environment.py"
