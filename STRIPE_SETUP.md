# FUB to Sierra Converter - Stripe Payment Link Setup

## 🔗 Creating a Stripe Payment Link

1. **Create a Stripe Account** (if you don't have one)
   - Go to https://stripe.com
   - Sign up for a free account

2. **Create a Payment Link**
   - Log in to https://dashboard.stripe.com
   - Click "Payment links" in the left sidebar
   - Click "+ New" to create a new payment link
   - Fill in the details:
     - **Product name:** FUB to Sierra CSV Conversion
     - **Price:** $9.99 (or your desired amount)
     - **Quantity:** 1
   - Click "Create link"

3. **Copy Your Payment Link**
   - After creation, you'll see a URL like: `https://buy.stripe.com/test_xxxxxxxxxxxxx`
   - Copy this entire URL

4. **Create Environment File**
   ```bash
   cp web_app/.env.example web_app/.env
   ```

5. **Add Your Payment Link to `web_app/.env`**
   ```bash
   PAYMENT_LINK=https://buy.stripe.com/test_xxxxxxxxxxxxx
   
   # Generate a random secret key for Flask sessions
   SECRET_KEY=your-random-secret-key-here
   ```

6. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🔗 Webhook Setup (Optional - For Payment Verification)

Webhooks allow your server to receive notifications when payments complete. This is optional but recommended for production.

### For Local Testing:

**Option 1: Stripe CLI (Recommended)**

1. Install Stripe CLI:
   ```bash
   brew install stripe/stripe-cli/stripe
   ```

2. Login to Stripe:
   ```bash
   stripe login
   ```

3. Forward webhooks to your local server:
   ```bash
   stripe listen --forward-to localhost:5001/webhook
   ```

4. Copy the webhook signing secret from the output:
   ```
   > Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxx
   ```

5. Add to `web_app/.env`:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

**Option 2: ngrok**

1. Install ngrok:
   ```bash
   brew install ngrok
   ```

2. Start ngrok tunnel:
   ```bash
   ngrok http 5001
   ```

3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

4. In Stripe Dashboard → Webhooks → Add endpoint:
   - Endpoint URL: `https://abc123.ngrok.io/webhook`
   - Events to send: `checkout.session.completed`

5. Copy the signing secret to `web_app/.env`

### For Production:

1. Go to https://dashboard.stripe.com/webhooks
2. Click "+ Add endpoint"
3. Configure:
   - **Endpoint URL:** `https://your-domain.com/webhook`
   - **Events to send:** Select `checkout.session.completed`
   - **Description:** "FUB to Sierra payment notifications"
4. Click "Add endpoint"
5. Click "Reveal" next to "Signing secret"
6. Copy the secret (starts with `whsec_`)
7. Add to your production `.env`:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

**Note:** Webhooks are optional. The app works without them using URL parameter verification. Webhooks add extra security and reliability for production use.

## 💰 Pricing Configuration

To change the price displayed to users:

1. Edit your Stripe Payment Link at https://dashboard.stripe.com/payment-links
2. Change the product price
3. Update the text in `web_app/templates/index.html` if needed (line showing "$9.99")

## 🧪 Testing Payments

### Test Payment Link Flow:

1. Make sure your Flask app is running:
   ```bash
   python web_app/app.py
   ```

2. **(Optional) Start Stripe webhook forwarding:**
   ```bash
   stripe listen --forward-to localhost:5001/webhook
   ```
   Keep this running in a separate terminal window.

3. Open your app: http://127.0.0.1:5001

4. Upload a CSV file and convert it

5. Click the payment link - use Stripe test mode

6. Use test card details:
   - **Card:** `4242 4242 4242 4242`
   - **Expiry:** Any future date (e.g., `12/25`)
   - **CVC:** Any 3 digits (e.g., `123`)
   - **ZIP:** Any 5 digits (e.g., `12345`)

7. Complete payment and get redirected back

8. Download your converted files

### Webhook Testing:

If you're running `stripe listen`, you'll see webhook events in the terminal:
```
✔ Received event checkout.session.completed
→ POST http://localhost:5001/webhook [200]
```

This confirms your webhook endpoint is receiving payment notifications!

## 🚀 Going Live

When ready for production:

### 1. Create Live Payment Link

1. Toggle **Test mode OFF** in Stripe dashboard (top right)
2. Go to https://dashboard.stripe.com/payment-links
3. Click "+ New" to create a new payment link
4. Configure:
   - **Product name:** FUB to Sierra CSV Conversion
   - **Price:** $9.99 (or your desired amount)
   - **After payment:** Success page
   - **Success URL:** `https://your-domain.com/?payment_success=true`
5. Click "Create link"
6. Copy the live payment link URL

### 2. Set Up Production Webhook

1. Go to https://dashboard.stripe.com/webhooks (with test mode OFF)
2. Click "+ Add endpoint"
3. Set **Endpoint URL:** `https://your-domain.com/webhook`
4. Select event: `checkout.session.completed`
5. Click "Add endpoint"
6. Copy the signing secret

### 3. Update Production Environment

Update your production `.env` file:
```env
PAYMENT_LINK=https://buy.stripe.com/live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
SECRET_KEY=your-secure-random-key
```

### 4. Deploy Your App

Deploy to your hosting platform (Render, Railway, Heroku, etc.) with the updated environment variables.

### 5. Test Live Payment

1. Visit your production site
2. Upload a test CSV
3. Complete payment with a real card
4. Verify download works
5. Check Stripe dashboard for the payment

### 6. Monitor Payments

View all live payments:
- https://dashboard.stripe.com/payments

**Important:** Make sure to change Flask debug mode to `False` in production!

## 🔒 Security Notes

- Payment links are hosted by Stripe (secure by default)
- Users complete payment on Stripe's secure checkout page
- No credit card data ever touches your server
- Keep `.env` file secure (it's in `.gitignore`)

## 📊 Monitoring Payments

View all payments in your Stripe dashboard:
- https://dashboard.stripe.com/payments

## 🆓 Free Tier Option

To offer free conversions:

1. Remove the payment notice from the UI
2. Edit `web_app/templates/index.html` - remove the payment notice display logic
3. Or create a separate free version without payment integration
