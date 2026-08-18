from __future__ import annotations

from hashlib import blake2b
import re
from typing import Protocol, Sequence

import numpy as np

from app.config import settings
from app.services.oci_auth import create_genai_inference_client


class EmbeddingProvider(Protocol):
    """Contrato para qualquer provedor de embeddings usado pelo RAG."""

    @property
    def dimension(self) -> int:
        ...

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        ...

    def embed_query(self, text: str) -> np.ndarray:
        ...


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype="float32")
    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class OCIEmbeddingProvider:
    """Embeddings de produção usando OCI Generative AI.

    O import do SDK é feito de forma tardia para que os testes locais que não
    usam a OCI possam rodar sem credenciais.
    """

    def __init__(
        self,
        compartment_id: str | None = None,
        model_id: str | None = None,
        dimension: int | None = None,
        batch_size: int | None = None,
    ) -> None:
        self.compartment_id = compartment_id or settings.oci_compartment_id
        self.model_id = model_id or settings.oci_embedding_model_id
        self._dimension = dimension or settings.embedding_dimensions
        self.batch_size = batch_size or settings.embedding_batch_size

        if not self.compartment_id:
            raise ValueError(
                "OCI_COMPARTMENT_ID não foi configurado. "
                "Copie .env.example para .env e informe o OCID do compartment."
            )

        try:
            import oci
        except ImportError as exc:
            raise RuntimeError(
                "O pacote 'oci' não está instalado. Execute: pip install -r requirements.txt"
            ) from exc

        self._oci = oci
        self._client = create_genai_inference_client(oci)

    @property
    def dimension(self) -> int:
        return self._dimension

    def _embed_batch(self, texts: Sequence[str], input_type: str) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype="float32")

        models = self._oci.generative_ai_inference.models
        details = models.EmbedTextDetails(
            serving_mode=models.OnDemandServingMode(
                serving_type="ON_DEMAND",
                model_id=self.model_id,
            ),
            compartment_id=self.compartment_id,
            inputs=list(texts),
            truncate="END",
            input_type=input_type,
            output_dimensions=self.dimension,
        )

        response = self._client.embed_text(embed_text_details=details)

        raw_embeddings = response.data.embeddings

        if raw_embeddings is None:
            by_type = getattr(response.data, "embeddings_by_type", None)
            if isinstance(by_type, dict):
                raw_embeddings = by_type.get("float")
            elif by_type is not None:
                raw_embeddings = getattr(by_type, "float", None)

        if raw_embeddings is None:
            raise RuntimeError(
                "A OCI respondeu à chamada de embeddings, mas não retornou "
                "vetores float em 'embeddings' nem em 'embeddings_by_type'."
            )

        embeddings = np.asarray(raw_embeddings, dtype="float32")

        if embeddings.shape != (len(texts), self.dimension):
            raise RuntimeError(
                "Dimensão inesperada retornada pela OCI: "
                f"{embeddings.shape}; esperado ({len(texts)}, {self.dimension})."
            )

        return _normalize_rows(embeddings)

    def _embed_many(self, texts: Sequence[str], input_type: str) -> np.ndarray:
        rows: list[np.ndarray] = []
        texts = list(texts)

        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            rows.append(self._embed_batch(batch, input_type=input_type))

        if not rows:
            return np.empty((0, self.dimension), dtype="float32")
        return np.vstack(rows).astype("float32")

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        return self._embed_many(texts, input_type="SEARCH_DOCUMENT")

    def embed_query(self, text: str) -> np.ndarray:
        return self._embed_batch([text], input_type="SEARCH_QUERY")[0]


class HashEmbeddingProvider:
    """Embedder determinístico e leve para testes automatizados.

    Não é o modelo usado em produção. Ele existe apenas para testar o pipeline
    de indexação/recuperação sem consumir a API da OCI.
    """

    def __init__(self, dimension: int = 256) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def _embed_one(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dimension, dtype="float32")
        tokens = re.findall(r"\w+", text.lower(), flags=re.UNICODE)

        for token in tokens:
            digest = blake2b(token.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "little")
            index = value % self.dimension
            sign = 1.0 if ((value >> 8) & 1) else -1.0
            vector[index] += sign

        return _normalize_rows(vector)[0]

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype="float32")
        return np.vstack([self._embed_one(text) for text in texts])

    def embed_query(self, text: str) -> np.ndarray:
        return self._embed_one(text)
