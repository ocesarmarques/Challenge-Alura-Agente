from __future__ import annotations

from pathlib import Path

from app.config import settings


def main() -> int:
    print("=== ImobIA | Verificação de autenticação OCI ===")

    try:
        import oci
    except ImportError:
        print("[ERRO] Pacote OCI não instalado.")
        print("Execute: python -m pip install -r requirements.txt")
        return 1

    config_file = str(Path(settings.oci_config_file).expanduser())

    try:
        config = oci.config.from_file(
            file_location=config_file,
            profile_name=settings.oci_profile,
        )
        config["region"] = settings.oci_region
        oci.config.validate_config(config)
    except Exception as exc:
        print(f"[ERRO] Não foi possível validar o arquivo OCI: {exc}")
        return 1

    print(f"[OK] Perfil: {settings.oci_profile}")
    print(f"[OK] Região: {settings.oci_region}")
    print(f"[OK] Tenancy OCID presente: {bool(config.get('tenancy'))}")
    print(f"[OK] User OCID presente: {bool(config.get('user'))}")
    print(f"[OK] Fingerprint presente: {bool(config.get('fingerprint'))}")
    print(f"[OK] Key file: {config.get('key_file')}")

    try:
        client = oci.identity.IdentityClient(config)
        regions = client.list_regions().data
        print(f"[OK] OCI respondeu à chamada autenticada ({len(regions)} regiões).")
    except Exception as exc:
        print(f"[ERRO] A autenticação não passou em uma chamada real: {exc}")
        return 1

    if not settings.oci_compartment_id:
        print("[ERRO] OCI_COMPARTMENT_ID ainda está vazio no .env.")
        return 1

    print("[OK] OCI_COMPARTMENT_ID configurado.")
    print("RESULTADO: autenticação OCI pronta.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
