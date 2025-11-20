# 🚀 Deployment Guide: AI Course Builder to Google Cloud Platform

This guide will help you deploy your AI Course Builder application to Google Cloud Platform and make it publicly available.

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
   - Sign up at: https://cloud.google.com/
   - Enable billing: https://console.cloud.google.com/billing

2. **gcloud CLI installed**
   - Download: https://cloud.google.com/sdk/docs/install
   - Or use Cloud Shell in GCP Console

3. **Project Setup**
   - Create a new project or use existing one
   - Note your PROJECT_ID

---

## 🎯 Method 1: Deploy to Cloud Run (RECOMMENDED)

Cloud Run is the easiest and most cost-effective way to deploy containerized applications.

### Step 1: Authenticate and Configure

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 2: Deploy Using the Script

```bash
# Make the script executable (if not already)
chmod +x deploy-to-cloudrun.sh

# Deploy (replace YOUR_PROJECT_ID with your actual project ID)
./deploy-to-cloudrun.sh YOUR_PROJECT_ID us-central1
```

### Step 3: Access Your Application

After deployment completes, you'll see a URL like:
```
https://ai-course-builder-XXXXXXXX-uc.a.run.app
```

This URL is **publicly accessible** immediately!

---

## 🔧 Manual Deployment to Cloud Run

If you prefer to deploy manually:

```bash
# Set variables
PROJECT_ID="your-project-id"
SERVICE_NAME="ai-course-builder"
REGION="us-central1"
API_KEY="AIzaSyBuXH09VMsrPkBv3LmFRSKXnhEC0q1_X34"

# Deploy
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "GOOGLE_API_KEY=$API_KEY,GEMINI_MODEL=gemini-2.0-flash-exp,PORT=8080" \
  --max-instances 10 \
  --min-instances 0
```

---

## 💰 Cost Estimation

### Cloud Run Pricing (as of 2024)

**Free Tier:**
- 2 million requests/month
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds

**Beyond Free Tier:**
- Memory: ~$0.0000025 per GB-second
- CPU: ~$0.000024 per vCPU-second
- Requests: ~$0.40 per million

**Estimated Monthly Cost:**
- Low usage (< 10k requests): FREE
- Medium usage (~100k requests): $5-15
- High usage (1M requests): $50-100

---

## 🌐 Custom Domain Setup (Optional)

### Step 1: Verify Domain Ownership
```bash
gcloud domains verify YOUR_DOMAIN.com
```

### Step 2: Map Domain to Cloud Run
```bash
gcloud run services add-iam-policy-binding ai-course-builder \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"

gcloud run domain-mappings create \
  --service=ai-course-builder \
  --domain=YOUR_DOMAIN.com \
  --region=us-central1
```

### Step 3: Update DNS Records
Add the DNS records shown in the output to your domain registrar.

---

## 🔒 Security Best Practices

### 1. Use Secret Manager for API Keys

```bash
# Create secret
echo -n "AIzaSyBuXH09VMsrPkBv3LmFRSKXnhEC0q1_X34" | \
  gcloud secrets create google-api-key --data-file=-

# Deploy with secret
gcloud run deploy ai-course-builder \
  --source . \
  --region us-central1 \
  --update-secrets GOOGLE_API_KEY=google-api-key:latest
```

### 2. Enable Authentication (if needed)

```bash
# Require authentication
gcloud run services update ai-course-builder \
  --region=us-central1 \
  --no-allow-unauthenticated
```

### 3. Set Up VPC Connector (for private resources)

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create ai-course-connector \
  --region=us-central1 \
  --range=10.8.0.0/28

# Update service
gcloud run services update ai-course-builder \
  --vpc-connector=ai-course-connector \
  --region=us-central1
```

---

## 📊 Monitoring and Logs

### View Logs
```bash
# Real-time logs
gcloud run services logs tail ai-course-builder --region=us-central1

# Recent logs
gcloud run services logs read ai-course-builder --region=us-central1 --limit=50
```

### View Metrics
```bash
# Service details
gcloud run services describe ai-course-builder --region=us-central1

# Or visit Cloud Console
# https://console.cloud.google.com/run
```

---

## 🔄 Update Deployment

### Update Code
```bash
# After making changes, simply redeploy
./deploy-to-cloudrun.sh YOUR_PROJECT_ID us-central1
```

### Update Environment Variables
```bash
gcloud run services update ai-course-builder \
  --region=us-central1 \
  --update-env-vars GEMINI_MODEL=gemini-2.5-pro
```

### Scale Configuration
```bash
gcloud run services update ai-course-builder \
  --region=us-central1 \
  --max-instances=20 \
  --min-instances=1 \
  --memory=4Gi \
  --cpu=4
```

---

## 🐛 Troubleshooting

### Issue: Deployment Fails
```bash
# Check build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log BUILD_ID
```

### Issue: Application Errors
```bash
# Check application logs
gcloud run services logs read ai-course-builder --region=us-central1 --limit=100
```

### Issue: Out of Memory
```bash
# Increase memory allocation
gcloud run services update ai-course-builder \
  --region=us-central1 \
  --memory=4Gi
```

### Issue: Timeout
```bash
# Increase timeout (max 3600 seconds)
gcloud run services update ai-course-builder \
  --region=us-central1 \
  --timeout=3600
```

---

## 🎯 Alternative: Deploy to Google Kubernetes Engine (GKE)

For more complex deployments:

```bash
# Create GKE cluster
gcloud container clusters create ai-course-cluster \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --region=us-central1

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-course-builder

# Deploy to GKE
kubectl create deployment ai-course-builder \
  --image=gcr.io/YOUR_PROJECT_ID/ai-course-builder

kubectl expose deployment ai-course-builder \
  --type=LoadBalancer \
  --port=80 \
  --target-port=8080
```

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)

---

## ✅ Quick Start Checklist

- [ ] Google Cloud account with billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] Project created and selected
- [ ] Required APIs enabled
- [ ] Deployment script executed
- [ ] Application URL accessible
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up

---

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Cloud Run logs
3. Check GCP Status Dashboard: https://status.cloud.google.com/
4. Visit GCP Console: https://console.cloud.google.com/

---

**Ready to deploy?** Run: `./deploy-to-cloudrun.sh YOUR_PROJECT_ID`

