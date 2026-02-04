# Deployment Guide - Open Meteo Python MCP

This guide covers deployment and operational procedures for the Open Meteo Python MCP server.

## Table of Contents

- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Environment Configuration](#environment-configuration)
- [Health Checks](#health-checks)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Local Development

```bash
# Install dependencies
uv pip install -e .

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the server
python -m uvicorn open_meteo_mcp.api.main:create_app --host 0.0.0.0 --port 8000

# Access the API
# REST API: http://localhost:8000/api/docs
# Health Check: http://localhost:8000/api/health
# Chat API: http://localhost:8000/api/chat/health
```

### Docker Deployment

#### Build the Image

```bash
# Build production image
docker build -t open-meteo-mcp:latest .

# Build with specific version tag
docker build -t open-meteo-mcp:4.0.0 .
```

#### Run the Container

```bash
# Basic run
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key_here \
  open-meteo-mcp:latest

# With environment file
docker run -p 8000:8000 \
  --env-file .env \
  open-meteo-mcp:latest

# With resource limits
docker run -p 8000:8000 \
  -m 512m \
  --cpus="1" \
  -e ANTHROPIC_API_KEY=your_key_here \
  open-meteo-mcp:latest

# With logging
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key_here \
  -e LOG_LEVEL=INFO \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  open-meteo-mcp:latest
```

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key for chat functionality | `sk-ant-...` |

### Recommended Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `development` |
| `API_PORT` | Port for REST API | `8000` |
| `CHAT_MODEL` | Claude model version | `claude-3-5-sonnet-20241022` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |
| `SESSION_TIMEOUT_MINUTES` | Chat session timeout | `30` |

## Health Checks

### REST API Health

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "version": "4.0.0",
  "timestamp": "2026-02-04T10:00:00Z"
}
```

### Chat API Health

```bash
curl http://localhost:8000/api/chat/health
```

### Readiness Check

```bash
curl http://localhost:8000/
```

## Performance Tuning

### Python Configuration

```bash
# Enable optimization
export PYTHONOPTIMIZE=2

# Increase file descriptors for high concurrency
ulimit -n 65536

# Use environment variables for tuning
export PYTHONHASHSEED=0
```

### API Configuration

```env
# Increase concurrent connections
WORKERS=4
WORKER_CONNECTIONS=1000

# Increase request timeouts for large operations
TIMEOUT_SECONDS=30

# Cache configuration
OPENMETEO_CACHE_ENABLED=true
OPENMETEO_CACHE_TTL_SECONDS=600
```

### Resource Limits

For Docker deployments:

```bash
# Recommended for production
docker run \
  -m 1g \
  --cpus="2" \
  -p 8000:8000 \
  open-meteo-mcp:latest
```

## Troubleshooting

### API Not Responding

1. **Check health endpoint:**
   ```bash
   curl -v http://localhost:8000/api/health
   ```

2. **Check logs:**
   ```bash
   docker logs <container_id>
   ```

3. **Verify port binding:**
   ```bash
   netstat -an | grep 8000
   ```

### Chat API Errors

**Issue: "Anthropic API key not found"**

Solution:
```bash
# Verify environment variable is set
echo $ANTHROPIC_API_KEY

# Set the key
export ANTHROPIC_API_KEY=your_key_here

# Restart the application
```

**Issue: "Tool calling failed"**

Solution:
- Check that the AI model has tool use capability
- Verify service layer is properly initialized
- Check application logs for detailed error

### Performance Issues

**Slow response times:**

1. Check API response time:
   ```bash
   time curl http://localhost:8000/api/tools/weather?latitude=47.3769&longitude=8.5417
   ```

2. Increase resource allocation:
   ```bash
   docker update --memory 2g <container_id>
   ```

3. Enable caching:
   ```env
   OPENMETEO_CACHE_ENABLED=true
   OPENMETEO_CACHE_TTL_SECONDS=600
   ```

### Connection Issues

**Issue: "Connection refused"**

Check if the server is running:
```bash
docker ps | grep open-meteo-mcp
```

Restart the container:
```bash
docker restart <container_id>
```

## Monitoring

### Logging Configuration

```env
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_OUTPUT=stdout
```

### Metrics Collection

Monitor key endpoints:
- `/api/health` - Overall application health
- `/api/tools/weather` - Weather service latency
- `/api/chat/health` - Chat service status

### Docker Stats

```bash
# Monitor container resources
docker stats <container_id>

# Watch logs in real-time
docker logs -f <container_id>
```

## Security Considerations

1. **Never commit .env files** - Use .env.example for templates
2. **Use secrets management** - Consider Docker Secrets or external secret stores
3. **Enable HTTPS in production** - Use reverse proxy (nginx, Traefik)
4. **Rate limiting** - Implement at reverse proxy level
5. **API authentication** - Consider adding API keys for REST endpoints

## Scaling

### Horizontal Scaling

For Docker Compose or Kubernetes, run multiple instances behind a load balancer:

```yaml
# Docker Compose example
services:
  api-1:
    image: open-meteo-mcp:latest
    ports: ["8001:8000"]
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

  api-2:
    image: open-meteo-mcp:latest
    ports: ["8002:8000"]
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

  nginx:
    image: nginx:latest
    ports: ["8000:80"]
    # Load balance between api-1 and api-2
```

### Vertical Scaling

Increase resources per instance:

```bash
docker run \
  -m 2g \
  --cpus="4" \
  open-meteo-mcp:latest
```

## Version Management

### Checking Version

```bash
curl http://localhost:8000/ | jq .version
```

### Updating Version

1. Update application code
2. Rebuild Docker image with new tag
3. Test in staging environment
4. Deploy with rolling update

## Support

For issues or questions:
- Check application logs: `docker logs <container_id>`
- Review API documentation: http://localhost:8000/api/docs
- Check health endpoints: `/api/health`, `/api/chat/health`
