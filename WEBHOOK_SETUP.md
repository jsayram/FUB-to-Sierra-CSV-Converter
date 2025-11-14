# Stripe Webhook Setup Guide

Complete guide for setting up Stripe webhooks for both local development and production.

---

## 🎯 Overview

Webhooks allow Stripe to notify your app when payment events occur (e.g., successful payment, failed payment).

You need **two separate webhooks**:
1. **Local webhook** - for testing on your computer (localhost)
2. **Production webhook** - for your live Railway app

---

## 🏠 Part 1: Local Development Webhook

### Step 1: Install Stripe CLI

**Mac:**
```bash
brew install stripe/stripe-cli/stripe
```

**Windows:**
```bash
# Download from: https://github.com/stripe/stripe-cli/releases/latest
# Run the installer
```

**Linux:**
```bash
# Download and extract
wget https://github.com/stripe/stripe-cli/releases/latest/download/stripe_linux_x86_64.tar.gz
tar -xvf stripe_linux_x86_64.tar.gz
sudo mv stripe /usr/local/bin
```

---

### Step 2: Login to Stripe CLI

```bash
stripe login
```

This opens your browser to authenticate with your Stripe account.

---

### Step 3: Forward Webhooks to Localhost

```bash
# Start webhook forwarding
stripe listen --forward-to localhost:5001/stripe-webhook
```

**Output will look like:**
```
> Ready! Your webhook signing secret is whsec_abc123xyz... (^C to quit)
```

**Copy the webhook secret** (starts with `whsec_`).

---

### Step 4: Update Local .env File

Open `web_app/.env` and update:

```bash
# Replace with the secret from Step 3
STRIPE_WEBHOOK_SECRET=whsec_abc123xyz...
```

---

### Step 5: Test Local Webhook

**Terminal 1 - Run Stripe listener:**
```bash
stripe listen --forward-to localhost:5001/stripe-webhook
```

**Terminal 2 - Run your app:**
```bash
python3 web_app/app.py
```

**Terminal 3 - Trigger test event:**
```bash
# Test a successful payment
stripe trigger payment_intent.succeeded
```

You should see the webhook event in Terminal 1 and your app logs in Terminal 2.

---

### Step 6: Test with Real Payment Flow

1. Visit http://localhost:5001
2. Upload a CSV and convert
3. Click "Pay to Download"
4. Use Stripe test card: `4242 4242 4242 4242`
5. Any future expiry date (e.g., 12/34)
6. Any 3-digit CVC (e.g., 123)
7. Complete payment

Check Terminal 1 - you should see the webhook event.

---

## 💳 Part 2: Create Stripe Payment Link

Before setting up webhooks, you need a payment link that customers will use.

### Step 1: Go to Stripe Payment Links

1. Go to [Stripe Dashboard → Payment Links](https://dashboard.stripe.com/payment-links)
2. Click **"+ New"** (or **"Create payment link"**)

---

### Step 2: Configure Payment Details

**Product Information:**
- **Name**: `FUB to Sierra CSV Conversion`
- **Description**: `Convert your Follow Up Boss contacts to Sierra CSV format`
- **Price**: `$5.00` USD (or your chosen price)
- **Billing**: One-time payment

**Advanced Options:**
- ✅ Check **"Collect customer email addresses"** (optional but recommended)
- ✅ Check **"Allow promotion codes"** (optional)

---

### Step 3: Configure After Payment

**After payment:**
- **Redirect customers to**: Choose one:
  - **Option A**: Stripe-hosted success page (default)
  - **Option B**: Custom URL (e.g., `https://your-railway-app.up.railway.app/success`)

**Note**: If using custom URL, add this route to your app:
```python
@app.route('/success')
def payment_success():
    return render_template('success.html')
```

---

### Step 4: Save and Copy Payment Link

1. Click **"Create link"**
2. Copy the payment link URL
   - Test mode: `https://buy.stripe.com/test_xxxxx`
   - Live mode: `https://buy.stripe.com/live_xxxxx`

---

### Step 5: Add Payment Link to Your App

**For Local Development:**

Update `web_app/.env`:
```bash
PAYMENT_LINK=https://buy.stripe.com/test_xxxxx
```

**For Production (Railway):**
```bash
railway variables --set "PAYMENT_LINK=https://buy.stripe.com/test_xxxxx"
```

---

## 🚀 Part 3: Production Webhook (Railway)

### Step 1: Get Your Production URL

```bash
# Get your Railway app URL
railway domain
```

Example output: `fubconverterapp-production.up.railway.app`

---

### Step 2: Create Production Webhook in Stripe

1. Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click **"Add endpoint"**
3. Enter endpoint URL:
   ```
   https://your-railway-url.up.railway.app/stripe-webhook
   ```
   Example: `https://fubconverterapp-production.up.railway.app/stripe-webhook`

4. Click **"Select events"**
5. **Important**: Select these specific events:
   - ✅ `checkout.session.completed` - Triggered when payment link checkout completes
   - ✅ `payment_intent.succeeded` - Triggered when payment successfully processes
   - ✅ `payment_intent.payment_failed` - Triggered when payment fails

   **Why these events?**
   - `checkout.session.completed` - Your payment link uses Checkout, so this event fires when the customer completes the checkout form
   - `payment_intent.succeeded` - Confirms the actual payment went through successfully
   - Both are needed to handle the complete payment flow

6. Click **"Add endpoint"**

---

### Step 3: Get Production Webhook Secret

After creating the endpoint:

1. Click on the webhook you just created
2. Click **"Reveal"** next to "Signing secret"
3. Copy the secret (starts with `whsec_`)

---

### Step 4: Add to Railway Environment Variables

**Option A - Via CLI:**
```bash
railway variables --set "STRIPE_WEBHOOK_SECRET=whsec_production_secret_here"
```

**Option B - Via Dashboard:**
1. Open Railway dashboard: `railway open`
2. Click **"Variables"** tab
3. Find `STRIPE_WEBHOOK_SECRET`
4. Update with the new production secret
5. Click **"Save"**

The app will automatically redeploy with the new secret.

---

### Step 5: Test Production Webhook

1. Visit your Railway URL: `https://your-app.up.railway.app`
2. Upload a CSV and convert
3. Click "Pay to Download"
4. Use test card: `4242 4242 4242 4242`
5. Complete payment
6. Download should start automatically

**Verify webhook received:**
1. Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click on your production webhook
3. Check **"Events"** tab - you should see recent events

---

## 🔄 Workflow Summary

### Local Development
```bash
# Terminal 1: Start Stripe listener
stripe listen --forward-to localhost:5001/stripe-webhook

# Terminal 2: Run app
python3 web_app/app.py

# Test with stripe CLI
stripe trigger payment_intent.succeeded
```

### Production (Railway)
- Webhook URL: `https://your-app.up.railway.app/stripe-webhook`
- Set `STRIPE_WEBHOOK_SECRET` in Railway variables
- Webhooks work automatically on every payment

---

## 📊 Webhook Event Flow

### What happens when payment completes:

1. **Customer pays** on Stripe Checkout
2. **Stripe sends webhook** to your endpoint
3. **Your app verifies** webhook signature
4. **Your app processes** payment confirmation
5. **Download link** becomes available

---

## 🔐 Security Notes

### Webhook Signature Verification

Your app already verifies webhooks using this code (in `app.py`):

```python
@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        # Process verified event
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
```

This prevents fake webhook requests.

---

## 🛠️ Troubleshooting

### Issue: Webhook not received locally

**Solution:**
```bash
# Ensure Stripe CLI is running
stripe listen --forward-to localhost:5001/stripe-webhook

# Ensure your app is running
python3 web_app/app.py

# Check if port matches (both use 5001)
```

---

### Issue: Webhook signature verification fails

**Solution:**
```bash
# Ensure STRIPE_WEBHOOK_SECRET matches the current webhook
# For local: Copy from stripe listen output
# For production: Copy from Stripe Dashboard

# Update .env (local)
STRIPE_WEBHOOK_SECRET=whsec_correct_secret

# Or update Railway (production)
railway variables --set "STRIPE_WEBHOOK_SECRET=whsec_correct_secret"
```

---

### Issue: Production webhook not working

**Check these:**

1. **Correct URL?**
   ```bash
   # Get your Railway URL
   railway domain
   # Webhook should be: https://that-url/stripe-webhook
   ```

2. **Correct events selected?**
   - ✅ `checkout.session.completed`
   - ✅ `payment_intent.succeeded`

3. **Secret set in Railway?**
   ```bash
   railway variables
   # Should show STRIPE_WEBHOOK_SECRET
   ```

4. **Check Stripe logs:**
   - Go to Stripe Dashboard → Webhooks
   - Click your endpoint
   - Check "Events" tab for errors

---

## 📝 Environment Variable Reference

### Local (.env file)
```bash
STRIPE_WEBHOOK_SECRET=whsec_local_secret_from_stripe_listen
PAYMENT_LINK=https://buy.stripe.com/test_...
```

### Production (Railway Variables)
```bash
STRIPE_WEBHOOK_SECRET=whsec_production_secret_from_dashboard
PAYMENT_LINK=https://buy.stripe.com/live_...  # When ready for production
```

---

## 🎯 Quick Setup Checklist

### Create Payment Link First
- [ ] Go to Stripe Dashboard → Payment Links
- [ ] Create new payment link ($5 for CSV conversion)
- [ ] Copy payment link URL
- [ ] Add to `.env` (local) or Railway variables (production)
- [ ] Test payment link opens correctly

### Local Development
- [ ] Install Stripe CLI
- [ ] Run `stripe login`
- [ ] Run `stripe listen --forward-to localhost:5001/stripe-webhook`
- [ ] Copy webhook secret to `.env`
- [ ] Test with `stripe trigger payment_intent.succeeded`
- [ ] Test full payment flow with payment link

### Production
- [ ] Get Railway URL with `railway domain`
- [ ] Create webhook in Stripe Dashboard
- [ ] Add endpoint: `https://your-url/stripe-webhook`
- [ ] Select events: `checkout.session.completed`, `payment_intent.succeeded`, `payment_intent.payment_failed`
- [ ] Copy production webhook secret
- [ ] Add to Railway variables: `STRIPE_WEBHOOK_SECRET`
- [ ] Test with real payment using test card `4242 4242 4242 4242`
- [ ] Verify download works after payment

---

## 🔗 Useful Links

- **Stripe CLI Docs**: https://stripe.com/docs/stripe-cli
- **Webhook Events**: https://stripe.com/docs/api/events/types
- **Test Cards**: https://stripe.com/docs/testing
- **Stripe Dashboard**: https://dashboard.stripe.com/webhooks

---

## 💡 Pro Tips

### Tip 1: Keep Stripe CLI Running

Add to your development workflow:
```bash
# Create a script: dev.sh
#!/bin/bash
stripe listen --forward-to localhost:5001/stripe-webhook &
python3 web_app/app.py
```

### Tip 2: Test Multiple Event Types

```bash
# Successful payment
stripe trigger payment_intent.succeeded

# Failed payment
stripe trigger payment_intent.payment_failed

# Checkout completed
stripe trigger checkout.session.completed
```

### Tip 3: View Webhook Logs

```bash
# Local: Check Stripe CLI output
# Production: Check Railway logs
railway logs --follow
```

---

**Your webhook setup is ready!** 🎉

- **Local**: Use Stripe CLI for testing
- **Production**: Use Stripe Dashboard webhook for live payments
