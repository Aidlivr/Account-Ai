#!/bin/bash
# Accountrix Deploy Script
# Run this on the server to pull latest code and rebuild
# Usage: bash deploy.sh

set -e

echo "🚀 Deploying Accountrix..."

# Pull latest from GitHub
echo "📥 Pulling latest code..."
cd /var/www/accountrix
git pull origin main

# Restart backend
echo "🔄 Restarting backend..."
systemctl restart accountrix
sleep 3

# Check backend is running
if curl -s http://127.0.0.1:8001/api/health | grep -q "healthy"; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend health check failed — check logs with: journalctl -u accountrix -n 20"
fi

# Rebuild frontend
echo "🏗️  Building frontend..."
cd /var/www/accountrix/frontend
npm run build

# Reload nginx
echo "🔄 Reloading nginx..."
systemctl reload nginx

echo ""
echo "✅ Deployment complete!"
echo "🌐 Live at: https://accountrix.norabot.ai"
