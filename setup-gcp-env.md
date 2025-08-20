# GCP Cloud Run Environment Variables Setup

## Quick Fix: Set Environment Variables in GCP Console

### 1. Go to Google Cloud Console
- Navigate to: https://console.cloud.google.com/run
- Select your project: `prefab-manifest-469511-j9`
- Click on your service: `catalyst-career-ai-backend`

### 2. Edit the Service
- Click "Edit & Deploy New Revision"
- Go to the "Variables & Secrets" tab
- Add the following environment variables:

## Required Environment Variables

### Essential Variables (MUST HAVE):
```
ENVIRONMENT=production
GOOGLE_API_KEY=your_actual_google_api_key_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/catalyst_career_ai
ADMIN_API_TOKEN=your_secure_random_token_here
ADMIN_EMAILS=admin@catalystcareers.in
```

### Optional Variables:
```
CLOUDINARY_CLOUD_NAME=dxckwabqo
CLOUDINARY_API_KEY=227141174969319
CLOUDINARY_API_SECRET=rQHSVnSkHSgS_D75cnYbX6FO-t0
FRONTEND_URL=https://catalystcareers.in
```

## Alternative: Use gcloud CLI

```bash
gcloud run services update catalyst-career-ai-backend \
    --region asia-southeast1 \
    --set-env-vars "ENVIRONMENT=production,GOOGLE_API_KEY=your_key,MONGODB_URI=your_mongodb_uri,ADMIN_API_TOKEN=your_token,ADMIN_EMAILS=admin@catalystcareers.in"
```

## Test After Configuration

After setting the environment variables, test the endpoints:

```bash
# Test health endpoint
curl https://catalyst-career-ai-backend-147549542423.asia-southeast1.run.app/api/health

# Test blog posts endpoint
curl https://catalyst-career-ai-backend-147549542423.asia-southeast1.run.app/api/blog-posts

# Test system status
curl https://catalyst-career-ai-backend-147549542423.asia-southeast1.run.app/api/status
```

## Expected Results

After proper configuration, you should see:
- Health endpoint returns: `{"status":"healthy","message":"All services operational"}`
- Blog posts endpoint returns: `[]` (empty array if no posts) or actual blog posts
- No more timeout errors in your frontend
