#!/bin/bash

# Quick Access Script for AI Course Builder

echo "🚀 AI Course Builder - Quick Access"
echo "===================================="
echo ""
echo "Choose an access method:"
echo ""
echo "  1) Local Proxy (access at http://localhost:8080)"
echo "  2) Open in browser with authentication"
echo "  3) Get authenticated access URL"
echo "  4) View service status"
echo "  5) View logs"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
  1)
    echo ""
    echo "🌐 Starting local proxy..."
    echo "Access your app at: http://localhost:8080"
    echo "Press Ctrl+C to stop"
    echo ""
    gcloud run services proxy ai-course-builder --region=us-central1 --project=warm-scion-ritm0062859
    ;;
  2)
    echo ""
    echo "🌐 Opening in browser..."
    open "https://ai-course-builder-r25i2edvga-uc.a.run.app"
    echo ""
    echo "Note: You'll need to sign in with your Google account"
    ;;
  3)
    echo ""
    echo "🔐 Generating authenticated access..."
    TOKEN=$(gcloud auth print-identity-token)
    echo ""
    echo "✅ Use this curl command to access the service:"
    echo ""
    echo "curl -H \"Authorization: Bearer $TOKEN\" https://ai-course-builder-r25i2edvga-uc.a.run.app"
    echo ""
    echo "Or use this token in your browser extension:"
    echo "$TOKEN"
    echo ""
    ;;
  4)
    echo ""
    echo "📊 Service Status:"
    echo ""
    gcloud run services describe ai-course-builder --region=us-central1 --project=warm-scion-ritm0062859
    ;;
  5)
    echo ""
    echo "📋 Recent Logs:"
    echo ""
    gcloud run services logs read ai-course-builder --region=us-central1 --project=warm-scion-ritm0062859 --limit=50
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

