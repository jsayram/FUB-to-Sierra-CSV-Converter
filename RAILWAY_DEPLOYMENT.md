# Railway Deployment Guide

Complete guide to deploy your FUB to Sierra CSV Converter on Railway.app

---

## Why Railway?

✅ **$5 free credit/month** - Enough for your app  
✅ **Custom domains** with free SSL  
✅ **No sleep** - Always-on, no cold starts  
✅ **Auto-deploy** from GitHub  
✅ **Simple setup** - Deploy in 5 minutes  
✅ **Perfect for Flask apps** - Native Python support  

---

## Quick Deploy (5 Minutes)

### Step 1: Install Railway CLI

**Mac/Linux:**
```bash
npm i -g @railway/cli
```

**Or use Homebrew:**
```bash
brew install railway
```

**Windows:**
```bash
npm i -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

This opens your browser to authenticate.

### Step 3: Initialize Project

```bash
# Make sure you're in the project root
cd /Users/jramirez/Git/PyhtonNichePrograms/FUB-to-Sierra-CSV-Converter

# Initialize Railway project
railway init
```

Choose:
- **Create new project**: Yes
- **Project name**: fub-sierra-converter (or your choice)

### Step 4: Link to GitHub (Optional but Recommended)

```bash
# Push to GitHub if you haven't already
git add .
git commit -m "Add Railway deployment files"
git push origin main

# Link Railway to GitHub repo
railway link
```

Or create from Railway dashboard:
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository

### Step 5: Set Environment Variables

```bash
# Set SECRET_KEY
railway variables set SECRET_KEY=4b503fd1304b7dd31ae5e94b23657b08c2df550e3be8c71780db125fd940fed0

# Set Stripe payment link
railway variables set PAYMENT_LINK=https://buy.stripe.com/test_cNi3cxfeTbvk4Ru23F1VK00

# Set Stripe webhook secret
railway variables set STRIPE_WEBHOOK_SECRET=whsec_95bcYJmQllp83suQ1TGqD36x2VESrPuo

# Set debug mode to false
railway variables set FLASK_DEBUG=false

# Set PORT (Railway requires this)
railway variables set PORT=5001
```

**Or set via Dashboard:**
1. Open https://railway.app/dashboard
2. Select your project
3. Click "Variables" tab
4. Add each variable

### Step 6: Deploy!

```bash
railway up
```

This will:
- Build your app
- Install dependencies
- Start gunicorn server
- Deploy to Railway

### Step 7: Open Your App

```bash
railway open
```

Or get the URL:
```bash
railway domain
```

---

## Custom Domain Setup

### Add Your Domain

**Via CLI:**
```bash
railway domain
# Follow prompts to add custom domain
```

**Via Dashboard:**
1. Open https://railway.app/dashboard
2. Select your project
3. Click "Settings" → "Domains"
4. Click "Custom Domain"
5. Enter: `yourdomain.com`
6. Railway provides DNS records

### Configure DNS

Railway will show you DNS records to add. Example:

**For root domain (yourdomain.com):**
- Type: `CNAME` or `ALIAS`
- Name: `@`
- Value: `your-app.up.railway.app`

**For www subdomain:**
- Type: `CNAME`
- Name: `www`
- Value: `your-app.up.railway.app`

### DNS Provider Examples:

**Cloudflare:**
1. DNS → Add Record
2. Type: `CNAME`
3. Name: `@` (or `www`)
4. Target: `your-app.up.railway.app`
5. Proxy status: DNS only (gray cloud)

**GoDaddy:**
1. DNS Management → Add Record
2. Type: `CNAME`
3. Host: `@` (or `www`)
4. Points to: `your-app.up.railway.app`

**Namecheap:**
1. Advanced DNS → Add Record
2. Type: `CNAME Record`
3. Host: `@` (or `www`)
4. Value: `your-app.up.railway.app`

### SSL Certificate

Railway **automatically provisions SSL** certificates for custom domains via Let's Encrypt. No configuration needed!

- Wait 5-10 minutes after adding domain
- Certificate auto-renews every 90 days
- Access via `https://yourdomain.com`

---

## Monitoring & Management

### View Logs

```bash
# Live logs
railway logs

# Or via dashboard
railway open
# Click "Deployments" → "Logs"
```

### Check Deployment Status

```bash
railway status
```

### Environment Variables

```bash
# List all variables
railway variables

# Set a variable
railway variables set KEY=value

# Delete a variable
railway variables delete KEY
```

### Restart App

```bash
railway restart
```

### View Metrics

Dashboard shows:
- CPU usage
- Memory usage
- Network traffic
- Request count

---

## Update & Redeploy

### From CLI:

```bash
# Make code changes
git add .
git commit -m "Update feature"
git push origin main

# Deploy
railway up
```

### Auto-Deploy from GitHub:

If linked to GitHub, Railway auto-deploys on push to main branch!

```bash
git add .
git commit -m "Update feature"
git push origin main
# Railway automatically deploys! 🚀
```

---

## Scaling

### Increase Resources:

**Via Dashboard:**
1. Project → Settings
2. Scroll to "Resources"
3. Adjust:
   - vCPU allocation
   - Memory limit
   - Restart policy

**Cost:** Pay for what you use (~$5-20/month depending on traffic)

### Horizontal Scaling:

Railway supports multiple instances:
1. Settings → "Replicas"
2. Increase replica count
3. Load balancing automatic

---

## Costs & Usage

### Free Tier:
- **$5 credit/month**
- Enough for ~500 hours of light traffic
- Perfect for testing/small apps

### Typical Usage for Your App:
- **2-5 users/day**: ~$3-5/month (within free tier)
- **10-20 users/day**: ~$8-12/month
- **50+ users/day**: ~$15-25/month

### Monitor Usage:
```bash
# Check current usage
railway status

# Or via dashboard
# Project → Usage tab
```

---

## Troubleshooting

### App Won't Start

**Check logs:**
```bash
railway logs
```

**Common issues:**
- Missing environment variables → `railway variables`
- Port binding → Ensure `PORT` variable is set
- Dependencies → Check `requirements.txt`

### Domain Not Working

**Check DNS:**
```bash
dig yourdomain.com
nslookup yourdomain.com
```

**Common issues:**
- DNS propagation (wait 24-48 hours)
- CNAME not pointing to Railway domain
- Cloudflare proxy enabled (disable for Railway)

### 502 Bad Gateway

**Causes:**
- App crashed → Check logs
- Port mismatch → Verify `PORT` variable
- Startup timeout → Increase in `railway.toml`

**Fix:**
```bash
railway logs
railway restart
```

### High Memory Usage

**Optimize:**
```bash
# Reduce workers in Procfile
# Change from --workers=4 to --workers=2
```

Update `railway.toml`:
```toml
startCommand = "gunicorn --workers=2 --threads=2 --timeout=120 --bind=0.0.0.0:$PORT web_app.app:app"
```

---

## Security Best Practices

### Environment Variables

✅ **Never commit `.env` to git**
✅ **Use Railway variables for secrets**
✅ **Rotate SECRET_KEY periodically**
✅ **Use Stripe test mode until ready**

### HTTPS Only

Railway enforces HTTPS automatically on custom domains.

### Rate Limiting

Consider adding Flask-Limiter:

```bash
pip install Flask-Limiter
```

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per hour")
def upload_file():
    # ...
```

---

## File Cleanup on Railway

Your cleanup script works on Railway! Schedule it:

### Option 1: In-App Cleanup (Current)

Your app already runs cleanup on page load:
```python
@app.route('/')
def index():
    cleanup_old_files()  # Runs automatically
```

### Option 2: Railway Cron Job

Railway doesn't have built-in cron, but you can use:

**GitHub Actions** (Free):

Create `.github/workflows/cleanup.yml`:
```yaml
name: Cleanup Files
on:
  schedule:
    - cron: '0 * * * *'  # Every hour

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Cleanup
        run: |
          curl https://yourdomain.com/  # Triggers cleanup on page load
```

---

## Backup & Rollback

### Rollback to Previous Deployment:

**Via Dashboard:**
1. Deployments tab
2. Find previous deployment
3. Click "Redeploy"

**Via CLI:**
```bash
railway logs --deployment previous
railway rollback
```

### Database Backup:

You don't use a database, but if you add one later:
```bash
railway db backup
```

---

## Support & Resources

- **Railway Docs**: https://docs.railway.app/
- **Discord**: https://discord.gg/railway
- **Status**: https://status.railway.app/
- **Pricing**: https://railway.app/pricing

---

## Quick Reference Commands

```bash
# Deploy
railway up

# View logs
railway logs

# Open dashboard
railway open

# Check status
railway status

# Set variable
railway variables set KEY=value

# Restart
railway restart

# Link to GitHub
railway link

# Get domain
railway domain
```

---

## Next Steps After Deployment

1. ✅ Test your app at the Railway URL
2. ✅ Add custom domain (if you have one)
3. ✅ Update Stripe to production mode (when ready)
4. ✅ Monitor usage in first week
5. ✅ Set up GitHub auto-deploy
6. ✅ Add error monitoring (optional: Sentry)

---

## Summary

Railway is **perfect for your Flask app** because:
- Simple deployment (`railway up`)
- Auto-scaling based on usage
- $5/month free credit (enough for low traffic)
- Custom domain + SSL included
- No sleep/cold starts
- Great developer experience

**Deploy now with:** `railway up` 🚀
