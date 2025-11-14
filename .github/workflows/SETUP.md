# GitHub Actions CI/CD Setup Guide

This guide will help you set up automatic deployment to Railway using GitHub Actions.

## Overview

The CI/CD pipeline automatically:
1. ✅ Runs all 62 tests on every push to `main`
2. ✅ Deploys to Railway if tests pass
3. ✅ Provides deployment notifications

---

## Setup Steps

### Step 1: Create Railway Project

1. Go to [railway.app/new](https://railway.app/new)
2. Click **"Deploy from GitHub repo"**
3. Select `jsayram/FUB-to-Sierra-CSV-Converter`
4. Railway will create your project

### Step 2: Add Environment Variables in Railway

In your Railway project dashboard:

1. Click **"Variables"** tab
2. Add these variables:

```
SECRET_KEY=6f1bceacbeb0865ac391d29ca0bdcb56f73c633f59c7c0a4c9e72c326d15d458
STRIPE_WEBHOOK_SECRET=whsec_RB0QZFn2IR1hqR4LMqKRQx6w1RyRjq8w
PAYMENT_LINK=https://buy.stripe.com/test_cNi3cxfeTbvk4Ru23F1VK00
FLASK_DEBUG=false
PORT=5001
```

### Step 3: Get Railway Token

1. In Railway dashboard, click your profile (top right)
2. Click **"Account Settings"**
3. Click **"Tokens"** tab
4. Click **"Create Token"**
5. Copy the token (starts with `railway_...`)

### Step 4: Get Railway Service ID

In your Railway project:

1. Click **"Settings"** tab
2. Scroll to **"Service ID"**
3. Copy the service ID (UUID format)

### Step 5: Add GitHub Secrets

1. Go to your GitHub repo: [github.com/jsayram/FUB-to-Sierra-CSV-Converter](https://github.com/jsayram/FUB-to-Sierra-CSV-Converter)
2. Click **"Settings"** tab
3. Click **"Secrets and variables"** → **"Actions"**
4. Click **"New repository secret"**
5. Add these secrets:

**Secret 1:**
- Name: `RAILWAY_TOKEN`
- Value: Your Railway token (from Step 3)

**Secret 2:**
- Name: `RAILWAY_SERVICE_ID`
- Value: Your Railway service ID (from Step 4)

### Step 6: Test the Workflow

Commit and push to trigger deployment:

```bash
git add .github/workflows/
git commit -m "Add CI/CD pipeline for Railway deployment"
git push origin main
```

Watch the workflow run:
1. Go to **"Actions"** tab in your GitHub repo
2. You'll see the workflow running
3. Tests run first, then deployment

---

## How It Works

### Workflow Triggers

- **On push to `main`**: Automatically runs tests and deploys
- **Manual trigger**: Click "Run workflow" in Actions tab

### Pipeline Steps

1. **Checkout**: Clones your code
2. **Setup Python**: Installs Python 3.10
3. **Install dependencies**: Installs from `requirements.txt`
4. **Run tests**: Executes all 62 tests with coverage
5. **Deploy**: If tests pass, deploys to Railway

### What Happens on Failure

- **Tests fail**: Deployment is cancelled, you get notified
- **Deployment fails**: Workflow fails, previous deployment remains active

---

## Monitoring

### View Workflow Runs

GitHub repo → **Actions** tab → Click on any workflow run

### View Deployment Logs

Railway dashboard → **Deployments** tab → Click on deployment → **Logs**

### Check App Status

Railway dashboard → Your app URL (e.g., `your-app.up.railway.app`)

---

## Customization

### Run Tests Only (No Deploy)

Temporarily disable deployment:

1. Go to `.github/workflows/deploy.yml`
2. Comment out the `deploy` job
3. Push to main

### Change Deployment Branch

Edit `.github/workflows/deploy.yml`:

```yaml
on:
  push:
    branches:
      - production  # Change from 'main' to 'production'
```

### Add Slack Notifications

Add to the end of `deploy` job:

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "🚀 Deployment successful!"
      }
```

---

## Troubleshooting

### Workflow Fails at Test Step

**Cause**: Tests are failing

**Fix**:
```bash
# Run tests locally first
pytest tests/ -v

# Fix failing tests, then push
git add .
git commit -m "Fix tests"
git push origin main
```

### Workflow Fails at Deploy Step

**Cause**: Railway token or service ID incorrect

**Fix**:
1. Verify Railway token in GitHub Secrets
2. Verify Railway service ID in GitHub Secrets
3. Check Railway project is active

### No Deployment Happening

**Cause**: Workflow file not detected

**Fix**:
```bash
# Ensure workflow file is committed
git add .github/workflows/deploy.yml
git commit -m "Add workflow file"
git push origin main
```

---

## Manual Deployment

If you need to deploy without pushing:

1. Go to **Actions** tab in GitHub
2. Click **"Deploy to Railway"** workflow
3. Click **"Run workflow"**
4. Select `main` branch
5. Click **"Run workflow"** button

---

## Security Notes

✅ **Never commit secrets to git**
✅ **Use GitHub Secrets for sensitive data**
✅ **Rotate Railway token if compromised**
✅ **Railway environment variables are encrypted**

---

## Next Steps

After setup:

1. ✅ Push code to `main` branch
2. ✅ Watch workflow run in Actions tab
3. ✅ Check deployment in Railway dashboard
4. ✅ Visit your app URL to test
5. ✅ Add custom domain in Railway (optional)

---

## Support

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Railway Docs**: https://docs.railway.app/
- **Railway Discord**: https://discord.gg/railway

---

**Your CI/CD pipeline is ready! 🚀**

Every push to `main` will now automatically test and deploy your app.
