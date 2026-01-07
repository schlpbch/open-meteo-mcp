# Deploy open-meteo-mcp to Google Cloud Platform
# Usage: .\deploy.ps1 [PROJECT_ID]

param(
    [string]$ProjectId = "journey-service-mcp"
)

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Write-Success "🚀 Open-Meteo MCP Deployment Script"
Write-Host "======================================"

Write-Info "📋 Project ID: $ProjectId"

# Set project
Write-Host "Setting GCP project..."
gcloud config set project $ProjectId

# Enable required APIs
Write-Info "`n🔧 Enabling required GCP APIs..."
gcloud services enable `
    cloudbuild.googleapis.com `
    run.googleapis.com `
    containerregistry.googleapis.com `
    --project=$ProjectId

# Build and push with Jib (using Artifact Registry compatible settings)
Write-Info "`n🏗️  Building container image with Jib..."
mvn compile jib:build `
    "-Djib.to.image=gcr.io/$ProjectId/open-meteo-mcp:latest" `
    "-Djib.from.auth.username=_json_key" `
    "-Djib.from.auth.password=$(gcloud auth print-access-token)" `
    "-Djib.allowInsecureRegistries=false" `
    -DskipTests `
    -B

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Build failed"
    exit 1
}

# Deploy to Cloud Run
Write-Info "`n☁️  Deploying to Cloud Run..."
gcloud run deploy open-meteo-mcp `
    --image=gcr.io/$ProjectId/open-meteo-mcp:latest `
    --region=europe-west6 `
    --platform=managed `
    --allow-unauthenticated `
    --memory=512Mi `
    --cpu=1 `
    --max-instances=10 `
    --min-instances=0 `
    --port=8080 `
    --timeout=60s `
    --set-env-vars=SPRING_PROFILES_ACTIVE=prod `
    --project=$ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Deployment failed"
    exit 1
}

# Get service URL
$ServiceUrl = gcloud run services describe open-meteo-mcp `
    --region=europe-west6 `
    --format='value(status.url)' `
    --project=$ProjectId

# Test deployment
Write-Info "`n🧪 Testing deployment..."
Write-Host "Service URL: $ServiceUrl"

# Test health endpoint
try {
    $response = Invoke-WebRequest -Uri "$ServiceUrl/health" -UseBasicParsing -ErrorAction Stop
    Write-Success "✅ Health check passed!"
} catch {
    Write-Error "❌ Health check failed: $_"
    exit 1
}

# Success message
Write-Success "`n✅ Deployment successful!"
Write-Host "======================================"
Write-Success "Service URL: $ServiceUrl"
Write-Host ""
Write-Host "Available endpoints:"
Write-Host "  - Health: $ServiceUrl/health"
Write-Host "  - MCP: $ServiceUrl/mcp"
Write-Host ""
Write-Host "Test with Claude Desktop by adding to config:"
Write-Host '{'
Write-Host '  "mcpServers": {'
Write-Host '    "open-meteo": {'
Write-Host "      `"url`": `"$ServiceUrl/mcp`""
Write-Host '    }'
Write-Host '  }'
Write-Host '}'
