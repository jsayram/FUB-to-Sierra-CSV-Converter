# Railway GitHub Auto-Deploy Setup

This guide shows you how to enable automatic deployments from GitHub to Railway for any project.

---

## 🎯 Problem

When you push commits to GitHub, Railway doesn't automatically deploy the changes.

## ✅ Solution

Connect your Railway project to your GitHub repository to enable auto-deploy.

---

## 📋 Prerequisites

- ✅ Railway account created at [railway.app](https://railway.app)
- ✅ GitHub repository with your project code
- ✅ Railway CLI installed: `npm i -g @railway/cli`
- ✅ Code pushed to GitHub's `main` branch

---

## 🏗️ Initial Railway Setup (First Time)

If you haven't set up Railway yet, follow these steps:

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"** or **"Login with GitHub"**
3. Authorize Railway to access your GitHub account
4. Complete signup

### Step 2: Install Railway CLI

**macOS/Linux:**
```bash
npm i -g @railway/cli
```

**Windows:**
```bash
npm i -g @railway/cli
```

**Verify installation:**
```bash
railway --version
```

### Step 3: Login to Railway CLI

```bash
railway login
```

This opens a browser window to authenticate. Click **"Authorize"** to connect the CLI to your account.

### Step 4: Prepare Your Project

**Ensure your project has these files:**

**For Python/Flask projects:**
- `requirements.txt` - Python dependencies
- `Procfile` or `railway.toml` - How to run your app
- `.env.example` (optional) - Example environment variables

**For Node.js projects:**
- `package.json` - Node dependencies
- Start script defined in `package.json`

**Example `Procfile` for Flask:**
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

**Example `railway.toml` for Python:**
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn web_app.app:app --workers 4 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Step 5: Initialize Railway Project

**Option A: From existing GitHub repo (Recommended)**

1. Go to [railway.app/new](https://railway.app/new)
2. Click **"Deploy from GitHub repo"**
3. Select your repository from the list
4. Railway detects your framework and creates the project
5. Skip to **Step 7** (Set Environment Variables)

**Option B: From local code**

```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize Railway project
railway init
```

Follow the prompts:
- **Create a new project:** Yes
- **Project name:** my-awesome-app (or your choice)
- **Environment:** production

### Step 6: Link Local Project to Railway

If you used Option B, link your local directory:

```bash
railway link
```

Select the project you just created.

### Step 7: Set Environment Variables

**Via CLI:**
```bash
# Generate a secret key (for Flask/Django)
railway variables set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Add other variables
railway variables set PAYMENT_LINK=your-stripe-link
railway variables set STRIPE_WEBHOOK_SECRET=your-webhook-secret
railway variables set FLASK_DEBUG=false
```

**Via Dashboard:**
1. `railway open`
2. Click your service
3. Click **Variables** tab
4. Click **+ New Variable**
5. Add `KEY` and `VALUE`
6. Click **Add**

### Step 8: Initial Deployment

**If you used Option A (GitHub):** Railway auto-deploys immediately ✅

**If you used Option B (local):** Deploy manually first:
```bash
railway up
```

Wait for deployment to complete (usually 1-3 minutes).

### Step 9: Get Your App URL

```bash
railway domain
```

Or check in Dashboard → Settings → Domains

Your app is live at: `https://your-app.up.railway.app` 🎉

### Step 10: Enable GitHub Auto-Deploy

**This is the critical step!**

Now follow **Method 1** below to connect your GitHub repository for auto-deploy.

---

## 🚀 Method 1: Railway Dashboard (Recommended)

### Step 1: Open Railway Dashboard

```bash
railway open
```

Or visit: [railway.app/dashboard](https://railway.app/dashboard)

### Step 2: Select Your Project

Click on the project you want to configure (e.g., "FUBConverterApp")

### Step 3: Navigate to Service Settings

1. Click on your **service** (the box showing your app)
2. Click the **Settings** tab
3. Scroll to the **Source** section

### Step 4: Connect GitHub Repository

1. Click **Connect Repo** (or **Change Source** if already connected)
2. **First time only:** Authorize Railway to access your GitHub account
3. Select your repository from the list (e.g., `username/my-project`)
4. Select branch: `main` (or your default branch)
5. Click **Connect**

### Step 5: Verify Auto-Deploy is Enabled

In **Settings → Source**, you should see:
```
GitHub: username/repository-name (main)
✅ Auto-deploy enabled
```

### Step 6: Test It!

Make a small change to your code:
```bash
# Make a small edit (e.g., add a comment to README.md)
git add .
git commit -m "test: Verify Railway auto-deploy"
git push origin main
```

Watch Railway dashboard - you should see a new deployment start automatically! 🎉

---

## 🚀 Method 2: Deploy New Project from GitHub

If starting fresh, you can deploy directly from GitHub:

### Step 1: New Project from GitHub

1. Go to [railway.app/new](https://railway.app/new)
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. Railway automatically:
   - Detects your framework (Flask, Node.js, etc.)
   - Sets up auto-deploy
   - Creates a production environment

### Step 2: Configure Environment Variables

```bash
railway variables set SECRET_KEY=your-secret-key
railway variables set OTHER_VAR=value
```

Or add them in Dashboard → Variables tab

### Step 3: Deploy

Railway auto-deploys on first connection. Future pushes to `main` will auto-deploy! ✅

---

## 🔧 Method 3: Railway CLI (Advanced)

### Connect via CLI

```bash
# Login to Railway
railway login

# Link to existing project
railway link

# Deploy current code
railway up

# Check deployment status
railway status
```

**Note:** `railway link` + `railway up` doesn't enable GitHub auto-deploy. You must still connect the GitHub repo via Dashboard (Method 1).

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Settings → Source shows: `GitHub: username/repo (main)`
- [ ] Auto-deploy toggle is **ON**
- [ ] Make test commit and push to `main`
- [ ] Railway dashboard shows new deployment starting
- [ ] Check logs: `railway logs`
- [ ] Visit your app URL to confirm changes deployed

---

## 🐛 Troubleshooting

### Auto-deploy not triggering?

**Check GitHub connection:**
1. Dashboard → Settings → Source
2. Should show: `GitHub: username/repo`
3. If blank or shows "Empty Service", reconnect GitHub

**Check branch:**
- Ensure you're pushing to the correct branch (usually `main`)
- Railway only deploys from the connected branch

**Check Railway GitHub App permissions:**
1. Go to [github.com/settings/installations](https://github.com/settings/installations)
2. Find "Railway"
3. Ensure your repository is granted access
4. If not, click "Configure" → Select repositories → Save

### Deployments failing?

**Check build logs:**
```bash
railway logs --deployment
```

**Common issues:**
- Missing environment variables
- Build commands failing
- Port configuration (Railway uses `PORT` env var)
- Dependencies not installed

### Manual deploy as fallback:

```bash
railway up
```

This force-deploys current code, but doesn't fix auto-deploy.

---

## 📊 How Auto-Deploy Works

1. **You push to GitHub:**
   ```bash
   git push origin main
   ```

2. **GitHub webhook triggers Railway:**
   - GitHub sends notification to Railway
   - Railway detects new commits on connected branch

3. **Railway auto-builds:**
   - Pulls latest code from GitHub
   - Runs build process (installs dependencies, etc.)
   - Starts new container

4. **Railway deploys:**
   - Health checks pass
   - Switches traffic to new container
   - Old container shuts down

5. **You're live!** 🚀

**Timeline:** Usually 1-3 minutes from push to live deployment.

---

## 🎨 Best Practices

### 1. Use Environment Variables

Never commit secrets to GitHub:
```bash
railway variables set SECRET_KEY=...
railway variables set API_KEY=...
```

### 2. Test Locally First

```bash
# Test before pushing
python app.py  # or npm start, etc.
# Only push when working locally
```

### 3. Use Branch Deployments

For larger projects:
- `main` branch → Production environment
- `staging` branch → Staging environment
- Feature branches → Preview deployments

Set up in Railway: Settings → Deployments → Branch Deployments

### 4. Monitor Deployments

```bash
# Watch logs in real-time
railway logs --tail

# Check deployment history
railway deployments
```

### 5. Rollback if Needed

In Dashboard → Deployments → Click any previous deployment → "Redeploy"

---

## 🔗 Useful Commands

```bash
# Check current Railway connection
railway status

# View environment variables
railway variables

# Open Railway dashboard
railway open

# View recent logs
railway logs

# Force manual deploy
railway up

# List all deployments
railway deployments
```

---

## 📚 Additional Resources

- **Railway Docs:** [docs.railway.com](https://docs.railway.com)
- **Auto-Deploy Guide:** [docs.railway.com/guides/github-autodeploy](https://docs.railway.com/guides/github-autodeploy)
- **GitHub Integration:** [docs.railway.com/develop/integrations#github](https://docs.railway.com/develop/integrations#github)
- **Environment Variables:** [docs.railway.com/develop/variables](https://docs.railway.com/develop/variables)

---

## 📝 Quick Reference

| Action | Command |
|--------|---------|
| Open dashboard | `railway open` |
| Deploy manually | `railway up` |
| View logs | `railway logs` |
| Check status | `railway status` |
| Set variable | `railway variables set KEY=value` |
| List variables | `railway variables` |

---

**Last Updated:** November 14, 2025

**Pro Tip:** Once GitHub auto-deploy is set up, you never need to run `railway up` manually again. Just `git push` and Railway handles the rest! 🎉
