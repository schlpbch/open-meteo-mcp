# GCP Deployment Status

## ✅ Staging Deployment - SUCCESS

**Service URL**: <https://open-meteo-mcp-480649180894.europe-west6.run.app>

### Current Status

- ✅ Project: `open-meteo-mcp`
- ✅ Project ID: `open-meteo-mcp`
- ✅ Project Number: `480649180894`
- ✅ Billing: Enabled (SBB MCP PoC - `015715-49F79A-6A40CC`)
- ✅ Deployment: Active on Cloud Run
- ✅ MCP Endpoint: Functional
- ✅ Health Check: UP (using in-memory session storage)

### Deployment Configuration

| Parameter | Value |
|-----------|-------|
| **Region** | europe-west6 |
| **Memory** | 512Mi |
| **CPU** | 1 |
| **Min Instances** | 0 |
| **Max Instances** | 10 |
| **Spring Profile** | prod |
| **Image** | gcr.io/open-meteo-mcp/open-meteo-mcp:latest |

## Quick Deployment

### Prerequisites

1. Ensure billing is enabled:

   ```bash
   gcloud billing projects describe open-meteo-mcp
   ```

2. Build locally first (to populate Maven cache):

   ```bash
   mvn clean install -DskipTests
   ```

### Deploy to Staging

```bash
# Build and push container image
mvn compile jib:build "-Djib.to.image=gcr.io/open-meteo-mcp/open-meteo-mcp:latest" -DskipTests -B

# Deploy to Cloud Run
gcloud run deploy open-meteo-mcp \
  --image=gcr.io/open-meteo-mcp/open-meteo-mcp:latest \
  --region=europe-west6 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --max-instances=10 \
  --min-instances=0 \
  --port=8080 \
  --timeout=60s \
  --set-env-vars=SPRING_PROFILES_ACTIVE=prod \
  --project=open-meteo-mcp
```

Or use the deployment script:

```bash
bash deploy.sh open-meteo-mcp
```

## Testing the Deployment

### Test MCP Endpoint

```bash
curl -X POST https://open-meteo-mcp-480649180894.europe-west6.run.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Test with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "open-meteo": {
      "url": "https://open-meteo-mcp-480649180894.europe-west6.run.app/mcp"
    }
  }
}
```

## Billing Account History

### Available Billing Accounts

1. **015715-49F79A-6A40CC** (SBB MCP PoC) - ✅ ACTIVE
   - Status: OPEN ✅
   - Currently linked to `open-meteo-mcp` project
   - Used for staging deployment

2. **01644F-ACF684-B5273C** (My Maps-Rechnungskonto)
   - Status: OPEN ✅
   - Issue: Cloud billing quota exceeded - Cannot link new projects

3. **00567A-EB2F12-F11043** (Mein Rechnungskonto)
   - Status: CLOSED ❌
   - Cannot be used for new projects

## Known Issues

### Test Failures (Java 25 Compatibility)

- **Issue**: Unit tests fail when run with Java 25 due to Mockito/ByteBuddy compatibility
- **Error**: `Java 25 (69) is not supported by the current version of Byte Buddy`
- **Impact**: None - Application compiles and runs correctly with Java 21
- **Workaround**: Ensure `JAVA_HOME` points to JDK 21 when running tests

## Next Steps

1. **Integration Testing**: Test with Claude Desktop or other MCP clients
2. **Monitoring**: Set up Cloud Monitoring alerts
3. **Production Deployment**: Deploy to production environment when ready
