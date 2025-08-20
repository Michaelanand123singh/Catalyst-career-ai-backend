@echo off
echo 🚀 Catalyst Career AI - Production Deployment to GCP
echo ====================================================

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Google Cloud SDK is not installed or not in PATH
    echo Please install from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Check if docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not in PATH
    echo Please install from: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Set project and service details
set PROJECT_ID=prefab-manifest-469549542423
set SERVICE_NAME=catalyst-career-ai-backend
set REGION=asia-southeast1
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest

echo.
echo 📋 Deployment Configuration:
echo    Project ID: %PROJECT_ID%
echo    Service Name: %SERVICE_NAME%
echo    Region: %REGION%
echo    Image: %IMAGE_NAME%

echo.
echo 🔧 Setting up Google Cloud project...
gcloud config set project %PROJECT_ID%

echo.
echo 🐳 Building Docker image...
docker build -t %IMAGE_NAME% .

if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)

echo.
echo 📤 Pushing image to Google Container Registry...
docker push %IMAGE_NAME%

if %errorlevel% neq 0 (
    echo ❌ Docker push failed
    pause
    exit /b 1
)

echo.
echo 🚀 Deploying to Cloud Run with environment variables...
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME% ^
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
    --set-env-vars "ENVIRONMENT=production,GOOGLE_API_KEY=AIzaSyBGnWrL0Bvr8MjIq5Z1b2QNBPA4pUT2Dac,MONGODB_URI=mongodb+srv://catalystedugrow:o6QuVNakrpP2pNnG@cluster0.15uz2y8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0,ADMIN_API_TOKEN=niferidngiuwenriungiuwnijnfewiundskjvndiunfeinwir,ADMIN_EMAILS=theanandsingh76@gmail.com,FRONTEND_URL=https://catalystcareers.in,CLOUDINARY_CLOUD_NAME=dxckwabqo,CLOUDINARY_API_KEY=227141174969319,CLOUDINARY_API_SECRET=rQHSVnSkHSgS_D75cnYbX6FO-t0"

if %errorlevel% neq 0 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

echo.
echo ✅ Deployment completed successfully!
echo.
echo 🔍 Testing the deployment...
echo Waiting 30 seconds for service to stabilize...
timeout /t 30 /nobreak >nul

echo.
echo 🧪 Running health check...
python test-backend-health.py

echo.
echo 🎉 Production deployment completed!
echo Your backend should now be working correctly.
echo.
pause
