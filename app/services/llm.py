from __future__ import annotations

from typing import Protocol

from app.agent.prompts import SYSTEM_PROMPT, build_rag_prompt
from app.config import settings
from app.services.oci_auth import create_genai_inference_client


class ChatProvider(Protocol):
    def generate(self, question: str, context: str) -> str:
        ...


class OCIChatProvider:
    """Geração de resposta usando OCI Generative AI e Cohere Command A."""

    def __init__(
        self,
        compartment_id: str | None = None,
        model_id: str | None = None,
    ) -> None:
        self.compartment_id = compartment_id or settings.oci_compartment_id
        self.model_id = model_id or settings.oci_chat_model_id

        if not self.compartment_id:
            raise ValueError(
                "OCI_COMPARTMENT_ID não foi configurado. "
                "Copie .env.example para .env e informe o OCID do compartment."
            )

        try:
            import oci
        except ImportError as exc:
            raise RuntimeError(
                "O pacote 'oci' não está instalado. "
                "Execute: pip install -r requirements.txt"
            ) from exc

        self._oci = oci
        self._client = create_genai_inference_client(oci)

    def generate(self, question: str, context: str) -> str:
        models = self._oci.generative_ai_inference.models

        request = models.CohereChatRequest(
            api_format="COHERE",
            message=build_rag_prompt(question, context),
            preamble_override=SYSTEM_PROMPT,
            max_tokens=settings.chat_max_tokens,
            temperature=settings.chat_temperature,
            top_p=0.8,
            prompt_truncation="AUTO_PRESERVE_ORDER",
            safety_mode="CONTEXTUAL",
            is_stream=False,
        )

        details = models.ChatDetails(
            compartment_id=self.compartment_id,
            serving_mode=models.OnDemandServingMode(
                serving_type="ON_DEMAND",
                model_id=self.model_id,
            ),
            chat_request=request,
        )

        response = self._client.chat(chat_details=details)
        chat_response = response.data.chat_response
        text = getattr(chat_response, "text", None)

        if not text or not str(text).strip():
            raise RuntimeError(
                "O OCI Generative AI retornou uma resposta vazia."
            )

        return str(text).strip()


class StaticChatProvider:
    """Provider simples para testes automatizados, sem chamadas externas."""

    def __init__(self, answer: str = "Resposta de teste.") -> None:
        self.answer = answer
        self.calls: list[tuple[str, str]] = []

    def generate(self, question: str, context: str) -> str:
        self.calls.append((question, context))
        return self.answer
