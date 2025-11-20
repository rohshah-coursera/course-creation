# 🚀 Deploy Your AI Course Builder NOW

## ✅ Step 1: Install gcloud CLI (COMPLETED)
gcloud CLI is now installed on your system!

---

## 🔐 Step 2: Authenticate with Google Cloud (MANUAL STEP REQUIRED)

**Open your terminal** and run:

```bash
gcloud auth login
```

This will:
1. Open your browser automatically
2. Ask you to sign in with your Google account
3. Grant permissions to gcloud CLI

**Alternative (if browser doesn't open):**
```bash
gcloud auth login --no-launch-browser
```
Then visit the URL shown and enter the verification code.

---

## 📁 Step 3: Create a New Project

After authentication, run these commands:

```bash
# Generate a unique project ID (or use your own)
PROJECT_ID="ai-course-builder-$(date +%s)"

# Create the project
gcloud projects create $PROJECT_ID --name="AI Course Builder"

# Set as default project
gcloud config set project $PROJECT_ID

# Link billing account (REQUIRED - you'll need to do this in Console)
echo "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
echo "Enable billing for your project to continue"
```

**Important:** You MUST enable billing for your project. Visit the Cloud Console and link a billing account.

---

## 🔧 Step 4: Enable Required APIs

```bash
cd /Users/rohanshah/Desktop/AI-Spark-04

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

---

## 🚀 Step 5: Deploy to Cloud Run

```bash
cd /Users/rohanshah/Desktop/AI-Spark-04

# Set your API key as environment variable
export GOOGLE_API_KEY="AIzaSyBuXH09VMsrPkBv3LmFRSKXnhEC0q1_X34"

# Deploy
gcloud run deploy ai-course-builder \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "GOOGLE_API_KEY=$GOOGLE_API_KEY,GEMINI_MODEL=gemini-2.0-flash-exp,PORT=8080" \
  --max-instances 10 \
  --min-instances 0
```

---

## ✅ Step 6: Get Your Public URL

After deployment completes, you'll see:

```
Service [ai-course-builder] revision [ai-course-builder-00001-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://ai-course-builder-xxxxxxxxxx-uc.a.run.app
```

**Your app is now LIVE and publicly accessible!** 🎉

---

## 🎯 QUICK START (All Commands in One)

Copy and paste this entire block:

```bash
# 1. Authenticate
gcloud auth login

# 2. Create project
PROJECT_ID="ai-course-builder-$(date +%s)"
gcloud projects create $PROJECT_ID --name="AI Course Builder"
gcloud config set project $PROJECT_ID

# 3. MANUAL: Enable billing at:
echo "⚠️  ENABLE BILLING: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
read -p "Press Enter after enabling billing..."

# 4. Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com

# 5. Deploy
cd /Users/rohanshah/Desktop/AI-Spark-04
gcloud run deploy ai-course-builder \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "GOOGLE_API_KEY=AIzaSyBuXH09VMsrPkBv3LmFRSKXnhEC0q1_X34,GEMINI_MODEL=gemini-2.0-flash-exp,PORT=8080" \
  --max-instances 10
```

---

## 📊 View Your Deployment

```bash
# Get service URL
gcloud run services describe ai-course-builder --region us-central1 --format 'value(status.url)'

# View logs
gcloud run services logs read ai-course-builder --region us-central1

# View in console
echo "View at: https://console.cloud.google.com/run"
```

---

## 💡 Troubleshooting

### "Billing must be enabled"
- Visit: https://console.cloud.google.com/billing
- Link a billing account to your project
- Free tier includes $300 credit for new users

### "API not enabled"
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### "Permission denied"
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## 🎉 That's It!

Your AI Course Builder will be:
- ✅ Deployed to Google Cloud Run
- ✅ Publicly accessible via HTTPS
- ✅ Auto-scaling (0-10 instances)
- ✅ Running on Google's infrastructure

**Total time:** ~10-15 minutes

**Cost:** FREE for low usage (under 2M requests/month)

---

## 🔄 Update Your Deployment

After making code changes:

```bash
cd /Users/rohanshah/Desktop/AI-Spark-04
gcloud run deploy ai-course-builder --source . --region us-central1
```

That's it! Cloud Run handles everything else.

