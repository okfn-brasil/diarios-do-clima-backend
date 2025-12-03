# Deploy em Produção com Docker Compose

Este guia explica como fazer deploy da aplicação em produção usando as imagens publicadas no GitHub Container Registry.

## Pré-requisitos

1. Docker e Docker Compose instalados
2. Rede externa do Traefik criada:
   ```bash
   docker network create frontend
   ```

## Configuração

1. Copie o arquivo de exemplo e configure as variáveis:
   ```bash
   cp .example.env .env
   ```

2. Edite o arquivo `.env` com as configurações de produção:
   ```bash
   # Domínio do backend
   BACKEND_DOMAIN=api.diariosdoclima.org.br
   
   # Versão da imagem Docker (tag ou branch)
   IMAGE_TAG=main
   # ou use uma versão específica:
   # IMAGE_TAG=v1.0.0
   
   # ... outras variáveis ...
   ```

## Deploy

### Deploy inicial:

```bash
# 1. Baixar as imagens do registry
docker compose -f compose.yml -f compose.prod.yml pull

# 2. Iniciar os serviços (sem build)
docker compose -f compose.yml -f compose.prod.yml up -d --no-build
```

### Atualizar para nova versão:

```bash
# 1. Atualizar IMAGE_TAG no .env (se necessário)
# 2. Baixar a nova imagem
docker compose -f compose.yml -f compose.prod.yml pull

# 3. Recriar os containers
docker compose -f compose.yml -f compose.prod.yml up -d --no-build
```

### Verificar status:

```bash
docker compose -f compose.yml -f compose.prod.yml ps
docker compose -f compose.yml -f compose.prod.yml logs -f
```

### Parar os serviços:

```bash
docker compose -f compose.yml -f compose.prod.yml down
```

## Arquivo unificado (opcional)

Se preferir trabalhar com um único arquivo compose, você pode gerar a versão unificada:

```bash
# Gerar arquivo unificado
docker compose -f compose.yml -f compose.prod.yml config > compose.unified.yml

# Usar o arquivo unificado
docker compose -f compose.unified.yml pull
docker compose -f compose.unified.yml up -d --no-build
```

**Nota:** O arquivo unificado conterá tanto a diretiva `build` quanto `image`. Isso é normal - o Docker Compose usará a imagem do registry quando você usar `--no-build` ou `pull`.

## Arquitetura de Redes

- **frontend**: Rede externa onde o Traefik está conectado
  - `diarios-do-clima-backend-server`: exposto via Traefik
  
- **backend**: Rede interna para comunicação entre serviços
  - `diarios-do-clima-backend-server`
  - `diarios-do-clima-backend-celery-beat`
  - `diarios-do-clima-backend-celery-worker`
  - `diarios-do-clima-redis`

## Troubleshooting

### Imagem não encontrada:

```bash
# Verificar se a imagem existe no registry
docker pull ghcr.io/okfn-brasil/diarios-do-clima-backend:main

# Verificar tags disponíveis em:
# https://github.com/okfn-brasil/diarios-do-clima-backend/pkgs/container/diarios-do-clima-backend
```

### Container não inicia:

```bash
# Ver logs detalhados
docker compose -f compose.yml -f compose.prod.yml logs <service-name>

# Verificar configuração
docker compose -f compose.yml -f compose.prod.yml config
```

### Traefik não roteia:

```bash
# Verificar se o container está na rede frontend
docker network inspect frontend

# Verificar labels do Traefik
docker inspect diarios-do-clima-backend-diarios-do-clima-backend-server-1 | grep -A 20 Labels
```
