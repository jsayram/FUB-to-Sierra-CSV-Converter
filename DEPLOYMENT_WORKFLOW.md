# Deployment Workflow Guide

Quick guide for deploying changes to your Railway app.

---

## 🚀 Standard Deployment Workflow

Every time you make changes to your code, follow these 3 simple steps:

### Step 1: Save and Test Locally

```bash
# Run your app locally to test changes
python web_app/app.py
```

Visit http://localhost:5001 to verify everything works.

Press `Ctrl+C` to stop the local server.

---

### Step 2: Commit Changes to Git

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Update index.html with new feature"

# View what will be pushed (optional)
git log --oneline -3
```

---

### Step 3: Push to GitHub

```bash
# Push to main branch
git push origin main
```

**That's it!** Railway automatically deploys your changes.

---

## 📊 Monitor Deployment

### Option 1: Watch in Terminal

```bash
# View live deployment logs
railway logs --follow
```

Press `Ctrl+C` to stop watching logs.

### Option 2: Check in Browser

```bash
# Open Railway dashboard
railway open
```

Then:
1. Click **"Deployments"** tab
2. See the latest deployment status
3. Click on deployment to view build logs

---

## ⏱️ Deployment Timeline

| Step | Time | What Happens |
|------|------|--------------|
| Push to GitHub | ~2 sec | Code uploaded to GitHub |
| Railway detects push | ~5 sec | Webhook triggers build |
| Build starts | ~30 sec | Installs dependencies |
| Deploy | ~10 sec | Starts your app |
| **Total** | **~1 min** | Your changes are live! |

---

## ✅ Verify Deployment

### Check if deployment succeeded:

```bash
# Get your app URL
railway domain
```

Visit the URL in your browser to see your changes live.

### Or check status:

```bash
railway status
```

---

## 🔄 Complete Example Workflow

Let's say you updated `index.html`:

```bash
# 1. Test locally
python web_app/app.py
# Visit http://localhost:5001, verify changes
# Press Ctrl+C

# 2. Commit changes
git add web_app/templates/index.html
git commit -m "feat: Update homepage layout"

# 3. Push to GitHub
git push origin main

# 4. Watch deployment (optional)
railway logs --follow
# Or open dashboard: railway open

# 5. Verify live app
railway domain
# Visit the URL to see your changes
```

**Done!** Your changes are live in production. 🎉

---

## 🛠️ Advanced Workflows

### Quick Fix Workflow

For small fixes without running locally:

```bash
git add .
git commit -m "fix: Typo in homepage"
git push origin main
```

Railway deploys automatically.

---

### Feature Branch Workflow

For larger features, use branches:

```bash
# Create feature branch
git checkout -b feature/new-homepage

# Make changes and commit
git add .
git commit -m "feat: Redesign homepage"

# Push branch to GitHub
git push origin feature/new-homepage

# Create Pull Request on GitHub
# After review, merge to main
# Railway auto-deploys when merged
```

---

### Rollback to Previous Version

If something breaks:

```bash
# View recent commits
git log --oneline -10

# Revert to previous commit
git revert HEAD

# Push the revert
git push origin main
```

Railway deploys the reverted version.

**Or rollback via Railway dashboard:**
1. Open Railway dashboard
2. Go to **"Deployments"** tab
3. Find previous working deployment
4. Click **"Redeploy"**

---

## 🚨 Common Issues

### Issue: Changes not appearing

**Solution:**
```bash
# Force refresh browser
# Press Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

# Or clear Railway cache
railway up --force
```

---

### Issue: Build fails

**Solution:**
```bash
# Check logs
railway logs

# Common fixes:
# - Fix syntax errors in your code
# - Ensure requirements.txt is up to date
# - Check environment variables are set
```

---

### Issue: App not starting

**Solution:**
```bash
# Check if environment variables are set
railway variables

# Restart the app
railway restart
```

---

## 📝 Best Practices

### ✅ Do:
- **Test locally** before pushing
- **Use descriptive commit messages** (feat, fix, docs, etc.)
- **Push frequently** - small, incremental changes
- **Check logs** after deployment
- **Keep requirements.txt** updated

### ❌ Don't:
- **Don't commit secrets** to git (use Railway variables)
- **Don't push broken code** to main
- **Don't skip local testing**
- **Don't commit `.env` file**

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Test locally | `python web_app/app.py` |
| Stage changes | `git add .` |
| Commit | `git commit -m "message"` |
| Deploy | `git push origin main` |
| View logs | `railway logs` |
| Check status | `railway status` |
| Get URL | `railway domain` |
| Open dashboard | `railway open` |
| Restart app | `railway restart` |

---

## 🔗 Your Deployment Setup

**Current Configuration:**
- ✅ Repository: `jsayram/FUB-to-Sierra-CSV-Converter`
- ✅ Branch: `main` (auto-deploys)
- ✅ Railway Project: `FUBConverterApp`
- ✅ Deploy trigger: Push to `main`
- ✅ Build time: ~1 minute

**Every push to main = automatic deployment** 🚀

---

## 📞 Need Help?

- **Railway Docs**: https://docs.railway.app/
- **Railway Discord**: https://discord.gg/railway
- **Check logs**: `railway logs`
- **Check status**: `railway status`

---

**Remember:** The workflow is always the same - **test → commit → push → deploy** ✨
