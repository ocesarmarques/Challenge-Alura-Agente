# Deploy do ImobIA no OCI Compute

## Arquitetura

```text
Internet
  ↓ TCP 8501
OCI Compute Ubuntu
  ↓
Docker
  ↓
ImobIA / Streamlit
  ↓
Instance Principal
  ↓
OCI Generative AI
```

## Autenticação segura

Na VM, use:

```dotenv
OCI_AUTH_MODE=instance_principal
```

Assim, a aplicação usa a identidade da própria instância e não precisa armazenar `~/.oci/config` nem chave privada PEM.

## Dynamic Group

Nome sugerido:

```text
ImobIACompute
```

Regra simples para um compartimento dedicado ao projeto:

```text
instance.compartment.id = '<COMPARTMENT_OCID>'
```

Se houver outras VMs no mesmo compartimento, prefira restringir pela instância específica.

## Políticas

```text
Allow dynamic-group ImobIACompute to use generative-ai-chat in compartment <NOME_DO_COMPARTIMENTO>
Allow dynamic-group ImobIACompute to use generative-ai-text-embedding in compartment <NOME_DO_COMPARTIMENTO>
```

## VM sugerida

Para demonstração com baixo custo:

```text
Ubuntu 24.04
VM.Standard.A1.Flex
1 OCPU
6 GB RAM
Subnet pública
IPv4 público
```

## Rede

Ingress recomendado para o Challenge:

```text
TCP 22   → preferencialmente restrito ao seu IP
TCP 8501 → 0.0.0.0/0 para acesso dos avaliadores
```

## Deploy automatizado

O repositório contém:

```text
deploy/cloud-init.yml
deploy/bootstrap_ubuntu.sh
deploy/docker-compose.oci.yml
scripts/generate_oci_runtime_env.sh
```

O bootstrap instala Docker, clona o repositório, detecta região/compartment via IMDSv2 e inicia o container.

## URL esperada

```text
http://<PUBLIC_IP>:8501
```

## Diagnóstico

```bash
sudo tail -f /var/log/imobia-bootstrap.log
cd /opt/imobia
sudo docker compose -f deploy/docker-compose.oci.yml ps
sudo docker logs --tail 200 imobia
```

## Segurança

Nunca copie para a VM:

```text
~/.oci/config
oci_api_key.pem
.env local
```
