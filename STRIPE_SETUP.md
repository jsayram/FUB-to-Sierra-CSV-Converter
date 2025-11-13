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

## 💰 Pricing Configuration

To change the price displayed to users:

1. Edit your Stripe Payment Link at https://dashboard.stripe.com/payment-links
2. Change the product price
3. Update the text in `web_app/templates/index.html` if needed (line showing "$9.99")

## 🧪 Testing Payments

Use Stripe test mode to test the payment flow:

1. Create a payment link in **Test mode**
2. Users can complete test payments without real charges
3. View test payments in: https://dashboard.stripe.com/test/payments

## 🚀 Going Live

When ready for production:

1. Toggle **Test mode** off in your Stripe dashboard
2. Create a new payment link in **Live mode**
3. Update `web_app/.env` with your live payment link URL
4. Test the live payment link before announcing to users

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
