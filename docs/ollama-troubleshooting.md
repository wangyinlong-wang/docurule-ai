# Ollama Troubleshooting

This guide helps diagnose Docker-to-Ollama connectivity issues when DocuRule uses Ollama running on the host machine.

> **Security:** Ollama does not need to be exposed to the public internet. The setup below is intended for local Docker-to-host communication.

## Quick checks

Run these commands from the DocuRule project directory.

### 1. Check Ollama

Check that Ollama is running and that the expected model is installed:

```bash
curl http://127.0.0.1:11434/api/tags
```

If Ollama is managed by systemd:

```bash
sudo systemctl status ollama
ss -ltnp | grep 11434
```

On Linux, Ollama must listen on an address reachable from the Docker container. If needed, configure the systemd drop-in:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Then restart Ollama:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### 2. Check DocuRule provider status

```bash
curl http://localhost:8080/api/v1/provider
```

A healthy response should report the Ollama provider, configured model, and:

```text
"available": true
```

### 3. Check the configured base URL and model

DocuRule's Compose configuration uses:

```text
DOCURULE_AI_PROVIDER=ollama
DOCURULE_AI_BASE_URL=http://host.docker.internal:11434
DOCURULE_AI_MODEL=gemma4:latest
```

Check the resolved Compose configuration:

```bash
docker compose config
```

### 4. Test Ollama from the DocuRule container

```bash
docker compose exec docurule sh
```

Then run:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://host.docker.internal:11434/api/tags', timeout=5).read().decode())"
```

If the command returns the Ollama model list, Docker-to-Ollama connectivity is working.

## Docker host addressing

### Docker Desktop

Docker Desktop provides `host.docker.internal` for containers to reach services running on the host.

DocuRule uses:

```text
http://host.docker.internal:11434
```

### Linux Docker Compose

On Linux, DocuRule's Compose configuration provides the host mapping:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

This allows the container to resolve `host.docker.internal` to the Docker host.


### Connection refused

**Symptoms:**

- `/api/v1/provider` reports Ollama as unavailable.
- The container connectivity check returns `Connection refused`.

Check Ollama:

```bash
curl http://127.0.0.1:11434/api/tags
ss -ltnp | grep 11434
```

Make sure Ollama is running and listening on an address reachable from Docker. Do not expose Ollama to the public internet.

### Model not found

Check installed models:

```bash
curl http://127.0.0.1:11434/api/tags
```

Make sure `DOCURULE_AI_MODEL` exactly matches an installed model, for example:

```text
gemma4:latest
```

### Model timeout

If connectivity works but model requests time out, inspect both DocuRule and Ollama logs:

```bash
docker compose logs --tail=100 docurule
```

```bash
sudo journalctl -u ollama --no-pager -n 100
```

Large models may take longer to load, especially on systems with limited resources. Confirm that Ollama is running normally before changing networking configuration.

## Container logs

View recent DocuRule logs:

```bash
docker compose logs --tail=100 docurule
```

Follow the logs while reproducing a problem:

```bash
docker compose logs -f docurule
```

## Verify Docker Compose

Check that the Compose configuration is valid:

```bash
docker compose config --quiet
```

## Issue report checklist

Copy and complete this checklist when reporting an issue:

```text
### Environment
- OS:
- Docker version:
- Docker Compose version:
- Ollama version:
- DocuRule version/commit:

### Configuration
- AI provider: ollama
- AI base URL: http://host.docker.internal:11434
- AI model:
- Ollama running on: host

### Commands and results
- curl http://127.0.0.1:11434/api/tags:
- curl http://localhost:8080/api/v1/provider:
- docker compose config --quiet:
- Container Ollama connectivity check:
- docker compose logs --tail=100 docurule:

### Problem
- Error message:
- When it occurs:
- Problem type: connection refused / model not found / timeout / other:
```

Do not include API keys, credentials, tokens, or document contents in issue reports.