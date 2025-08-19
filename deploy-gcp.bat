@echo off
REM Catalyst Career AI Backend - GCP Deployment Script (Windows)
REM Project ID: prefab-manifest-469511-j9

setlocal enabledelayedexpansion

set PROJECT_ID=prefab-manifest-469511-j9
set SERVICE_NAME=catalyst-career-ai-backend
set REGION=us-central1
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%

echo 🚀 Deploying Catalyst Career AI Backend to Google Cloud Platform
echo Project ID: %PROJECT_ID%
echo Service Name: %SERVICE_NAME%
echo Region: %REGION%
echo ----------------------------------------

REM Check if gcloud is installed
gcloud version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: gcloud CLI is not installed. Please install it first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    exit /b 1
)

REM Set the project
echo 📝 Setting project...
gcloud config set project %PROJECT_ID%

REM Enable required APIs
echo 🔧 Enabling required APIs...
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

REM Build and push the Docker image
echo 🏗️  Building Docker image...
docker build -t %IMAGE_NAME%:latest .

echo 📤 Pushing image to Container Registry...
docker push %IMAGE_NAME%:latest

REM Deploy to Cloud Run
echo 🚀 Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME%:latest ^
    --region %REGION% ^
    --platform managed ^
    --allow-unauthenticated ^
    --port 8000 ^
    --memory 2Gi ^
    --cpu 2 ^
    --max-instances 10 ^
    --min-instances 0 ^
    --concurrency 100 ^
    --timeout 900 ^
    --set-env-vars "ENVIRONMENT=production,PORT=8000,HOST=0.0.0.0"

REM Get the service URL
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)"') do set SERVICE_URL=%%i

echo ✅ Deployment completed successfully!
echo 🌐 Service URL: %SERVICE_URL%
echo 📊 Monitor logs: gcloud logs tail --follow --project=%PROJECT_ID%
echo 🔍 View in Console: https://console.cloud.google.com/run/detail/%REGION%/%SERVICE_NAME%/metrics?project=%PROJECT_ID%

echo ----------------------------------------
echo 🎉 Deployment process completed!
echo 📋 Next steps:
echo    1. Set up your environment variables in Cloud Run console
echo    2. Configure your domain (if needed)
echo    3. Set up monitoring and alerting
echo    4. Update your frontend to use the new backend URL

pause
