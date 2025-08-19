# Catalyst Career AI Backend - GCP Deployment Guide

## Project Information
- **Project ID**: `prefab-manifest-469511-j9`
- **Service Name**: `catalyst-career-ai-backend`
- **Region**: `us-central1`

## Prerequisites

### 1. Install Google Cloud SDK
```bash
# Download and install from: https://cloud.google.com/sdk/docs/install
# Or use the installer for your OS
```

### 2. Install Docker
```bash
# Download and install from: https://docs.docker.com/get-docker/
```

### 3. Authenticate with Google Cloud
```bash
gcloud auth login
gcloud auth configure-docker
```

## Deployment Methods

### Method 1: Quick Deployment (Recommended)

#### For Windows:
```cmd
cd backend
deploy-gcp.bat
```

#### For Linux/Mac:
```bash
cd backend
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

### Method 2: Manual Deployment

#### Step 1: Set up your project
```bash
gcloud config set project prefab-manifest-469511-j9
```

#### Step 2: Enable required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

#### Step 3: Build and push Docker image
```bash
cd backend

# Build the image
docker build -t gcr.io/prefab-manifest-469511-j9/catalyst-career-ai-backend:latest .

# Push to Container Registry
docker push gcr.io/prefab-manifest-469511-j9/catalyst-career-ai-backend:latest
```

#### Step 4: Deploy to Cloud Run
```bash
gcloud run deploy catalyst-career-ai-backend \
    --image gcr.io/prefab-manifest-469511-j9/catalyst-career-ai-backend:latest \
    --region us-central1 \
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
```

### Method 3: Using Cloud Build (CI/CD)

#### Step 1: Set up Cloud Build trigger
1. Go to [Cloud Build Console](https://console.cloud.google.com/cloud-build/triggers)
2. Create a new trigger
3. Connect your repository
4. Use the provided `cloudbuild.yaml` file

#### Step 2: Push code to trigger deployment
```bash
git add .
git commit -m "Deploy to GCP"
git push origin main
```

## Environment Variables Setup

### 1. Copy the environment template
```bash
cp env.production.template .env
```

### 2. Fill in your actual values in `.env`

### 3. Set environment variables in Cloud Run
You can set environment variables through:

#### Option A: Google Cloud Console
1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Select your service
3. Click "Edit & Deploy New Revision"
4. Go to "Variables & Secrets" tab
5. Add your environment variables

#### Option B: Using gcloud CLI
```bash
gcloud run services update catalyst-career-ai-backend \
    --region us-central1 \
    --set-env-vars "GOOGLE_API_KEY=your_actual_key,MONGODB_URI=your_mongodb_uri"
```

## Required Environment Variables

### Essential Variables:
- `GOOGLE_API_KEY`: Your Google AI API key
- `MONGODB_URI`: Your MongoDB connection string
- `ADMIN_API_TOKEN`: Secure token for admin access
- `ADMIN_EMAILS`: Comma-separated admin emails

### Optional Variables:
- `CLOUDINARY_CLOUD_NAME`: For image uploads
- `CLOUDINARY_API_KEY`: For image uploads  
- `CLOUDINARY_API_SECRET`: For image uploads
- `FRONTEND_URL`: Your frontend domain for CORS

## Post-Deployment Steps

### 1. Test your deployment
```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe catalyst-career-ai-backend --region=us-central1 --format="value(status.url)")

# Test health endpoint
curl $SERVICE_URL/ping

# Test API status
curl $SERVICE_URL/api/status
```

### 2. Set up custom domain (optional)
```bash
gcloud run domain-mappings create \
    --service catalyst-career-ai-backend \
    --domain your-api-domain.com \
    --region us-central1
```

### 3. Configure monitoring
1. Go to [Cloud Monitoring](https://console.cloud.google.com/monitoring)
2. Set up alerts for your service
3. Monitor logs in [Cloud Logging](https://console.cloud.google.com/logs)

### 4. Set up SSL certificate (if using custom domain)
```bash
gcloud compute ssl-certificates create catalyst-ssl-cert \
    --domains your-api-domain.com
```

## Monitoring and Maintenance

### View logs
```bash
gcloud logs tail --follow --project=prefab-manifest-469511-j9
```

### Update deployment
```bash
# Build new image
docker build -t gcr.io/prefab-manifest-469511-j9/catalyst-career-ai-backend:latest .
docker push gcr.io/prefab-manifest-469511-j9/catalyst-career-ai-backend:latest

# Deploy new revision
gcloud run deploy catalyst-career-ai-backend \
    --image gcr.io/prefab-manifest-469511-j9/catalyst-career-ai-backend:latest \
    --region us-central1
```

### Scale service
```bash
gcloud run services update catalyst-career-ai-backend \
    --region us-central1 \
    --min-instances 1 \
    --max-instances 20
```

## Troubleshooting

### Common Issues:

1. **Build fails**: Check Docker is running and you have permissions
2. **Deployment fails**: Verify project ID and region are correct
3. **Service not responding**: Check environment variables and logs
4. **CORS errors**: Update allowed origins in your backend code

### Debug commands:
```bash
# Check service status
gcloud run services describe catalyst-career-ai-backend --region us-central1

# View recent logs
gcloud logs read --project=prefab-manifest-469511-j9 --limit=50

# Check resource usage
gcloud run services describe catalyst-career-ai-backend --region us-central1 --format="value(status.conditions)"
```

## Cost Optimization

1. **Set appropriate min/max instances**
2. **Use appropriate memory/CPU allocation**
3. **Monitor usage in Cloud Console**
4. **Set up billing alerts**

## Security Best Practices

1. **Use environment variables for secrets**
2. **Enable VPC connector if needed**
3. **Set up IAM roles properly**
4. **Use Cloud Secret Manager for sensitive data**
5. **Regular security updates**

## Support

- **GCP Console**: https://console.cloud.google.com/run/detail/us-central1/catalyst-career-ai-backend/metrics?project=prefab-manifest-469511-j9
- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Logs**: https://console.cloud.google.com/logs/query?project=prefab-manifest-469511-j9
