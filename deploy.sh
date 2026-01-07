#!/bin/bash
# Deploy open-meteo-mcp to Google Cloud Platform
# Usage: ./deploy.sh [PROJECT_ID]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Open-Meteo MCP Deployment Script${NC}"
echo "======================================"

# Get project ID
if [ -z "$1" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ Error: No GCP project ID specified${NC}"
        echo "Usage: ./deploy.sh [PROJECT_ID]"
        echo "Or set default project: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
else
    PROJECT_ID=$1
fi

echo -e "${YELLOW}📋 Project ID: $PROJECT_ID${NC}"

# Set project
echo "Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "\n${YELLOW}🔧 Enabling required GCP APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    --project=$PROJECT_ID

# Build and push with Jib
echo -e "\n${YELLOW}🏗️  Building container image with Jib...${NC}"
mvn clean compile jib:build \
    -Djib.to.image=gcr.io/$PROJECT_ID/open-meteo-mcp:latest \
    -DskipTests \
    -B

# Deploy to Cloud Run
echo -e "\n${YELLOW}☁️  Deploying to Cloud Run...${NC}"
gcloud run deploy open-meteo-mcp \
    --image=gcr.io/$PROJECT_ID/open-meteo-mcp:latest \
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
    --project=$PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe open-meteo-mcp \
    --region=europe-west6 \
    --format='value(status.url)' \
    --project=$PROJECT_ID)

# Test deployment
echo -e "\n${YELLOW}🧪 Testing deployment...${NC}"
echo "Service URL: $SERVICE_URL"

# Test health endpoint
if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

# Test MCP endpoint
if curl -f -s "$SERVICE_URL/mcp" > /dev/null; then
    echo -e "${GREEN}✅ MCP endpoint accessible!${NC}"
else
    echo -e "${YELLOW}⚠️  MCP endpoint returned error (may require POST request)${NC}"
fi

# Success message
echo -e "\n${GREEN}✅ Deployment successful!${NC}"
echo "======================================"
echo -e "Service URL: ${GREEN}$SERVICE_URL${NC}"
echo ""
echo "Available endpoints:"
echo "  - Health: $SERVICE_URL/health"
echo "  - MCP: $SERVICE_URL/mcp"
echo ""
echo "Test with Claude Desktop by adding to config:"
echo '{'
echo '  "mcpServers": {'
echo '    "open-meteo": {'
echo '      "url": "'$SERVICE_URL'/mcp"'
echo '    }'
echo '  }'
echo '}'
