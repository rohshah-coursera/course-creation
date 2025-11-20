#!/bin/bash

# Complete End-to-End Deployment Script for AI Course Builder
# This script guides you through the entire deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     AI Course Builder - Complete GCP Deployment Script      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
GOOGLE_API_KEY="AIzaSyBuXH09VMsrPkBv3LmFRSKXnhEC0q1_X34"
SERVICE_NAME="ai-course-builder"
REGION="us-central1"

# Step 1: Check gcloud installation
echo -e "${YELLOW}[Step 1/6] Checking gcloud installation...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed!${NC}"
    echo "Please install it first using: brew install --cask google-cloud-sdk"
    exit 1
fi
echo -e "${GREEN}✅ gcloud CLI is installed ($(gcloud --version | head -1))${NC}"
echo ""

# Step 2: Authenticate
echo -e "${YELLOW}[Step 2/6] Authenticating with Google Cloud...${NC}"
echo "This will open your browser for authentication."
read -p "Press Enter to continue..."

if gcloud auth login; then
    echo -e "${GREEN}✅ Authentication successful!${NC}"
else
    echo -e "${RED}❌ Authentication failed. Please try again.${NC}"
    exit 1
fi
echo ""

# Step 3: Create or select project
echo -e "${YELLOW}[Step 3/6] Setting up GCP Project...${NC}"
echo ""
echo "Choose an option:"
echo "  1) Create a new project"
echo "  2) Use an existing project"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    # Generate unique project ID
    PROJECT_ID="ai-course-builder-$(date +%s)"
    echo ""
    echo "Creating project: $PROJECT_ID"
    
    if gcloud projects create $PROJECT_ID --name="AI Course Builder"; then
        echo -e "${GREEN}✅ Project created successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to create project. Try using an existing project instead.${NC}"
        exit 1
    fi
else
    # List existing projects
    echo ""
    echo "Your existing projects:"
    gcloud projects list
    echo ""
    read -p "Enter Project ID to use: " PROJECT_ID
fi

# Set the project
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ Project set to: $PROJECT_ID${NC}"
echo ""

# Step 4: Enable billing (manual check)
echo -e "${YELLOW}[Step 4/6] Checking billing...${NC}"
echo ""
echo "⚠️  IMPORTANT: Billing MUST be enabled for Cloud Run deployment"
echo ""
echo "Please visit this URL and ensure billing is enabled:"
echo -e "${BLUE}https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID${NC}"
echo ""
read -p "Press Enter after confirming billing is enabled..."

# Verify billing is enabled
if gcloud beta billing projects describe $PROJECT_ID &> /dev/null; then
    echo -e "${GREEN}✅ Billing appears to be configured${NC}"
else
    echo -e "${YELLOW}⚠️  Could not verify billing status. Continuing anyway...${NC}"
fi
echo ""

# Step 5: Enable required APIs
echo -e "${YELLOW}[Step 5/6] Enabling required APIs...${NC}"
echo "This may take a few minutes..."

apis=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "containerregistry.googleapis.com"
    "artifactregistry.googleapis.com"
)

for api in "${apis[@]}"; do
    echo "  Enabling $api..."
    if gcloud services enable $api --project=$PROJECT_ID; then
        echo -e "${GREEN}  ✅ $api enabled${NC}"
    else
        echo -e "${RED}  ❌ Failed to enable $api${NC}"
    fi
done
echo ""

# Step 6: Deploy to Cloud Run
echo -e "${YELLOW}[Step 6/6] Deploying to Cloud Run...${NC}"
echo "This will build your Docker container and deploy it."
echo "⏱️  Expected time: 5-10 minutes for first deployment"
echo ""
read -p "Press Enter to start deployment..."

cd "$(dirname "$0")"

echo ""
echo "🏗️  Starting deployment..."
echo ""

if gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "GOOGLE_API_KEY=$GOOGLE_API_KEY,GEMINI_MODEL=gemini-2.0-flash-exp,GEMINI_TEMPERATURE=0.7,PORT=8080" \
  --max-instances 10 \
  --min-instances 0 \
  --project=$PROJECT_ID; then
    
    echo ""
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              🎉 DEPLOYMENT SUCCESSFUL! 🎉                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' --project=$PROJECT_ID)
    
    echo ""
    echo -e "${GREEN}✅ Your AI Course Builder is now live!${NC}"
    echo ""
    echo -e "${BLUE}📱 Access your application at:${NC}"
    echo -e "${GREEN}   $SERVICE_URL${NC}"
    echo ""
    echo "📋 Useful Commands:"
    echo ""
    echo "   View logs:"
    echo "   gcloud run services logs read $SERVICE_NAME --region $REGION --project=$PROJECT_ID"
    echo ""
    echo "   View in console:"
    echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics?project=$PROJECT_ID"
    echo ""
    echo "   Update deployment:"
    echo "   cd $(pwd) && gcloud run deploy $SERVICE_NAME --source . --region $REGION --project=$PROJECT_ID"
    echo ""
    echo -e "${YELLOW}💰 Cost: FREE for up to 2M requests/month${NC}"
    echo ""
    
else
    echo ""
    echo -e "${RED}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              ❌ DEPLOYMENT FAILED                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Common issues and solutions:"
    echo "1. Billing not enabled: Visit https://console.cloud.google.com/billing"
    echo "2. APIs not enabled: Run the script again"
    echo "3. Permissions issue: Run: gcloud auth login"
    echo ""
    echo "For detailed logs, run:"
    echo "gcloud builds list --limit=1 --project=$PROJECT_ID"
    echo ""
    exit 1
fi

