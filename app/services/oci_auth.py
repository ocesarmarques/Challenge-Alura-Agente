from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import settings


SUPPORTED_AUTH_MODES = {
    "config_file",
    "instance_principal",
}


def normalize_auth_mode(value: str | None = None) -> str:
    mode = (value or settings.oci_auth_mode).strip().lower()

    if mode not in SUPPORTED_AUTH_MODES:
        supported = ", ".join(sorted(SUPPORTED_AUTH_MODES))
        raise ValueError(
            f"OCI_AUTH_MODE inválido: {mode!r}. "
            f"Use um destes valores: {supported}."
        )

    return mode


def build_oci_auth(oci_module: Any) -> tuple[dict, object | None]:
    """Retorna config e signer para clientes do OCI SDK.

    - config_file: usa ~/.oci/config (execução local).
    - instance_principal: usa a identidade da própria VM OCI, sem PEM.
    """
    mode = normalize_auth_mode()

    if mode == "instance_principal":
        signer = (
            oci_module.auth.signers
            .InstancePrincipalsSecurityTokenSigner()
        )
        return {"region": settings.oci_region}, signer

    config_file = str(
        Path(settings.oci_config_file).expanduser()
    )
    config = oci_module.config.from_file(
        file_location=config_file,
        profile_name=settings.oci_profile,
    )
    config["region"] = settings.oci_region
    return config, None


def create_genai_inference_client(oci_module: Any):
    config, signer = build_oci_auth(oci_module)

    kwargs: dict[str, object] = {
        "retry_strategy": oci_module.retry.DEFAULT_RETRY_STRATEGY,
    }

    if signer is not None:
        kwargs["signer"] = signer

    if settings.oci_genai_endpoint:
        kwargs["service_endpoint"] = settings.oci_genai_endpoint

    return (
        oci_module.generative_ai_inference
        .GenerativeAiInferenceClient(
            config=config,
            **kwargs,
        )
    )
