# Políticas OCI — ImobIA

## Desenvolvimento local

Permissões mínimas de inferência:

```text
Allow group <NOME_DO_GRUPO> to use generative-ai-chat in compartment <NOME_DO_COMPARTMENT>
Allow group <NOME_DO_GRUPO> to use generative-ai-text-embedding in compartment <NOME_DO_COMPARTMENT>
```

## Segurança

Não usar uma policy ampla `manage generative-ai-family` quando o projeto só
precisa de Chat e EmbedText, a menos que seja um ambiente sandbox e haja motivo
administrativo explícito.

## Deploy futuro

Quando o ImobIA for implantado em uma Compute Instance, a estratégia planejada
é trocar credenciais de usuário por **Instance Principal + Dynamic Group**,
evitando armazenar a chave privada do usuário na VM.

Essa mudança será implementada na fase de deploy.
