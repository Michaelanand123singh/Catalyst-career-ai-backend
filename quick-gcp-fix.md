# 🚀 Quick GCP Fix - Set Environment Variables

## ⚡ **IMMEDIATE ACTION REQUIRED**

Your backend is failing because environment variables are missing in GCP Cloud Run. Here's how to fix it in 5 minutes:

### **Step 1: Go to Google Cloud Console**
1. Navigate to: https://console.cloud.google.com/run
2. Select project: `prefab-manifest-469549542423`
3. Click on service: `catalyst-career-ai-backend`

### **Step 2: Edit the Service**
1. Click **"Edit & Deploy New Revision"**
2. Go to **"Variables & Secrets"** tab
3. Click **"Add Variable"** for each of these:

### **Step 3: Add These Environment Variables**

#### **Essential Variables (Copy & Paste):**

| Variable Name | Value |
|---------------|-------|
| `ENVIRONMENT` | `production` |
| `GOOGLE_API_KEY` | `AIzaSyBGnWrL0Bvr8MjIq5Z1b2QNBPA4pUT2Dac` |
| `MONGODB_URI` | `mongodb+srv://catalystedugrow:o6QuVNakrpP2pNnG@cluster0.15uz2y8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0` |
| `ADMIN_API_TOKEN` | `niferidngiuwenriungiuwnijnfewiundskjvndiunfeinwir` |
| `ADMIN_EMAILS` | `theanandsingh76@gmail.com` |

#### **Optional Variables (Copy & Paste):**

| Variable Name | Value |
|---------------|-------|
| `FRONTEND_URL` | `https://catalystcareers.in` |
| `CLOUDINARY_CLOUD_NAME` | `dxckwabqo` |
| `CLOUDINARY_API_KEY` | `227141174969319` |
| `CLOUDINARY_API_SECRET` | `rQHSVnSkHSgS_D75cnYbX6FO-t0` |

### **Step 4: Deploy**
1. Click **"Deploy"**
2. Wait for deployment to complete (2-3 minutes)
3. Your backend will be fixed!

## 🔍 **After Deployment - Test It**

Run this command to verify everything is working:

```bash
cd backend
python test-backend-health.py
```

**Expected Results:**
- ✅ All endpoints return 200 status
- ✅ `/api/health` shows "healthy" status
- ✅ `/api/blog-posts` returns `[]` or actual posts
- ✅ No more timeout errors in your frontend

## 🎯 **What This Fixes**

- ❌ **Before**: Blog posts endpoint returns 500 error
- ❌ **Before**: Chat service fails to initialize
- ❌ **Before**: Frontend gets timeout errors
- ✅ **After**: All endpoints work correctly
- ✅ **After**: Blog posts load properly
- ✅ **After**: Chat functionality available
- ✅ **After**: Frontend works without errors

## 🚨 **If You Still Have Issues**

1. **Check deployment logs** in GCP Console
2. **Verify environment variables** are set correctly
3. **Wait 5 minutes** for changes to propagate
4. **Run health check** again

---

**Time to Fix:** ⏱️ **5 minutes**
**Difficulty:** 🟢 **Easy**
**Result:** 🎉 **Fully functional backend**
