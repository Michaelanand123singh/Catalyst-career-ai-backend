#!/bin/bash

# Catalyst Career AI Backend - GCP Deployment Script
# Project ID: prefab-manifest-469511-j9

set -e

PROJECT_ID="prefab-manifest-469511-j9"
SERVICE_NAME="catalyst-career-ai-backend"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying Catalyst Career AI Backend to Google Cloud Platform"
echo "Project ID: $PROJECT_ID"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo "----------------------------------------"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: Not authenticated with gcloud. Please run 'gcloud auth login'"
    exit 1
fi

# Set the project
echo "📝 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push the Docker image
echo "🏗️  Building Docker image..."
docker build -t $IMAGE_NAME:latest .

echo "📤 Pushing image to Container Registry..."
docker push $IMAGE_NAME:latest

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 0 \
    --concurrency 100 \
    --timeout 900 \
    --set-env-vars "ENVIRONMENT=production,PORT=8000,HOST=0.0.0.0"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 Monitor logs: gcloud logs tail --follow --project=$PROJECT_ID"
echo "🔍 View in Console: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics?project=$PROJECT_ID"

# Test the deployment
echo "🧪 Testing deployment..."
if curl -f -s "$SERVICE_URL/ping" > /dev/null; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed. Check the logs for issues."
fi

echo "----------------------------------------"
echo "🎉 Deployment process completed!"
echo "📋 Next steps:"
echo "   1. Set up your environment variables in Cloud Run console"
echo "   2. Configure your domain (if needed)"
echo "   3. Set up monitoring and alerting"
echo "   4. Update your frontend to use the new backend URL"
