#!/bin/bash

# Deploy AI Course Builder to Google Cloud Run
# Usage: ./deploy-to-cloudrun.sh [PROJECT_ID] [REGION]

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="ai-course-builder"
GOOGLE_API_KEY="AIzaSyBuXH09VMsrPkBv3LmFRSKXnhEC0q1_X34"

echo "🚀 Deploying AI Course Builder to Google Cloud Run"
echo "=================================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo ""

# Set the project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and deploy to Cloud Run
echo "🏗️  Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
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
  --min-instances 0

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Your application is now live at:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
echo ""
echo "🔗 To view your service details:"
echo "   gcloud run services describe $SERVICE_NAME --region $REGION"
echo ""
echo "📊 To view logs:"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION"

