from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = ROOT_DIR / "data" / "documents"
VECTOR_STORE_DIR = ROOT_DIR / "data" / "vector_store"

load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_title: str = os.getenv("APP_TITLE", "ImobIA")
    top_k: int = int(os.getenv("TOP_K", "5"))
    min_relevance_score: float = float(
        os.getenv("MIN_RELEVANCE_SCORE", "0.32")
    )

    chunk_size: int = int(os.getenv("CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))

    oci_config_file: str = os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
    oci_profile: str = os.getenv("OCI_PROFILE", "DEFAULT")
    oci_region: str = os.getenv("OCI_REGION", "sa-saopaulo-1")
    oci_compartment_id: str = os.getenv("OCI_COMPARTMENT_ID", "")
    oci_genai_endpoint: str = os.getenv("OCI_GENAI_ENDPOINT", "")

    oci_embedding_model_id: str = os.getenv(
        "OCI_EMBEDDING_MODEL_ID", "cohere.embed-v4.0"
    )
    embedding_dimensions: int = int(
        os.getenv("EMBEDDING_DIMENSIONS", "1024")
    )
    embedding_batch_size: int = int(
        os.getenv("EMBEDDING_BATCH_SIZE", "32")
    )

    oci_chat_model_id: str = os.getenv(
        "OCI_CHAT_MODEL_ID", "cohere.command-a-03-2025"
    )
    chat_temperature: float = float(
        os.getenv("CHAT_TEMPERATURE", "0.10")
    )
    chat_max_tokens: int = int(
        os.getenv("CHAT_MAX_TOKENS", "700")
    )


settings = Settings()
