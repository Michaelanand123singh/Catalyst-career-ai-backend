# Catalyst Career AI - Production Deployment Script
# This script will deploy your backend to GCP with all the correct environment variables

Write-Host "🚀 Catalyst Career AI - Production Deployment to GCP" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# Check if gcloud is installed
try {
    $gcloudVersion = gcloud --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Google Cloud SDK found" -ForegroundColor Green
    } else {
        throw "gcloud not found"
    }
} catch {
    Write-Host "❌ Google Cloud SDK is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if docker is installed
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker found" -ForegroundColor Green
    } else {
        throw "docker not found"
    }
} catch {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install from: https://docs.docker.com/get-docker/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Set project and service details
$PROJECT_ID = "prefab-manifest-469549542423"
$SERVICE_NAME = "catalyst-career-ai-backend"
$REGION = "asia-southeast1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest"

Write-Host ""
Write-Host "📋 Deployment Configuration:" -ForegroundColor Yellow
Write-Host "   Project ID: $PROJECT_ID" -ForegroundColor White
Write-Host "   Service Name: $SERVICE_NAME" -ForegroundColor White
Write-Host "   Region: $REGION" -ForegroundColor White
Write-Host "   Image: $IMAGE_NAME" -ForegroundColor White

Write-Host ""
Write-Host "🔧 Setting up Google Cloud project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set project" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🐳 Building Docker image..." -ForegroundColor Yellow
docker build -t $IMAGE_NAME .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "📤 Pushing image to Google Container Registry..." -ForegroundColor Yellow
docker push $IMAGE_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker push failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 Deploying to Cloud Run with environment variables..." -ForegroundColor Yellow

# Deploy with all environment variables
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --port 8000 `
    --memory 2Gi `
    --cpu 2 `
    --max-instances 10 `
    --min-instances 0 `
    --concurrency 100 `
    --timeout 900 `
    --set-env-vars "ENVIRONMENT=production,GOOGLE_API_KEY=AIzaSyBGnWrL0Bvr8MjIq5Z1b2QNBPA4pUT2Dac,MONGODB_URI=mongodb+srv://catalystedugrow:o6QuVNakrpP2pNnG@cluster0.15uz2y8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0,ADMIN_API_TOKEN=niferidngiuwenriungiuwnijnfewiundskjvndiunfeinwir,ADMIN_EMAILS=theanandsingh76@gmail.com,FRONTEND_URL=https://catalystcareers.in,CLOUDINARY_CLOUD_NAME=dxckwabqo,CLOUDINARY_API_KEY=227141174969319,CLOUDINARY_API_SECRET=rQHSVnSkHSgS_D75cnYbX6FO-t0"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green

Write-Host ""
Write-Host "🔍 Testing the deployment..." -ForegroundColor Yellow
Write-Host "Waiting 30 seconds for service to stabilize..." -ForegroundColor White
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "🧪 Running health check..." -ForegroundColor Yellow
python test-backend-health.py

Write-Host ""
Write-Host "🎉 Production deployment completed!" -ForegroundColor Green
Write-Host "Your backend should now be working correctly." -ForegroundColor White

Write-Host ""
Write-Host "🔗 Next steps:" -ForegroundColor Cyan
Write-Host "1. Test your frontend: https://catalystcareers.in" -ForegroundColor White
Write-Host "2. Test blog page: https://catalystcareers.in/blog" -ForegroundColor White
Write-Host "3. Check browser console for any remaining errors" -ForegroundColor White

Read-Host "Press Enter to exit"
