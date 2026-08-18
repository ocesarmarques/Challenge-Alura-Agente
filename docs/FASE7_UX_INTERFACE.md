# Fase 7 — UX e interface do ImobIA

## Objetivo

Transformar a interface técnica da Fase 6 em uma experiência adequada para
demonstração e apresentação do Challenge Alura Agente.

## Melhorias implementadas

- interface conversacional com `st.chat_input`;
- mensagens em formato de chat com `st.chat_message`;
- histórico da conversa via Session State;
- quatro perguntas sugeridas;
- fontes recolhíveis por resposta;
- nomes amigáveis para os cinco PDFs;
- status visual do RAG;
- indicadores de PDFs, páginas e chunks;
- botão para iniciar nova conversa;
- estado vazio educativo;
- aviso explícito contra alucinação;
- tratamento visual de erros;
- cache do agente/FAISS/cliente OCI;
- layout mais limpo e adequado para screenshots.

## Comportamento fora da base

Quando o score não atinge o limiar, a interface informa que não há informação
suficiente e registra que o LLM não foi utilizado.

## Evidências recomendadas posteriormente

1. tela inicial;
2. pergunta respondida com fontes;
3. pergunta fora da base;
4. sidebar mostrando a base de conhecimento.
