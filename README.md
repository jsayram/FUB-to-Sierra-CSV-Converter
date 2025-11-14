# FUB to Sierra CSV Converter

A professional web application that converts **Follow Up Boss (FUB)** CSV exports into **Sierra CRM**-compatible format with an intuitive drag-and-drop interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0.0-green)

---

## ✨ Features

### 🎨 Professional UI
- **Dark/Light Mode** - Toggle between themes with persistent preference
- **Drag & Drop Upload** - Intuitive file upload with visual feedback
- **Real-time Preview** - See your converted data before downloading
- **Responsive Design** - Works seamlessly on desktop and mobile
- **Interactive Tables** - Resizable columns, zoom controls, fullscreen view

### 🔒 Privacy & Security
- **No Data Storage** - Files processed in-memory and deleted after 1 hour
- **Automatic Cleanup** - Server-side cleanup on page reload and session reset
- **Session-based** - Each user's data is isolated and secure
- **HTTPS Ready** - SSL/TLS support for production deployment

### 🚀 Smart Conversion
- **Auto-Detection** - Automatically detects FUB column names
- **Smart Mapping** - Pre-configured mappings for all Sierra fields
- **Phone Formatting** - Auto-formats phone numbers to (XXX) XXX-XXXX
- **Tag Deduplication** - Removes duplicate tags and formats properly
- **Chunking Support** - Handles large files (50k+ rows) by splitting into 5k row chunks
- **ZIP Downloads** - Automatically packages multiple files into a ZIP

### 💳 Payment Integration
- **Stripe Checkout** - Secure payment processing via Stripe Payment Links
- **Webhook Verification** - Server-side payment verification for security
- **Session Persistence** - Files remain available after payment completion
- **Pay-per-use** - Simple one-time payment model

### 🛡️ User Experience
- **Download Protection** - Explicit warnings before page reload/navigation
- **Toast Notifications** - Clear feedback for all actions
- **Progress Indicators** - Visual feedback during conversion
- **Error Handling** - Graceful error messages with helpful details
- **Console Logs** - Real-time conversion progress in UI

---

## 📋 What This Tool Does

This converter transforms Follow Up Boss contact exports into the exact format required by Sierra CRM, including:

- ✅ Normalizes phone numbers to `(XXX) XXX-XXXX` format
- ✅ Deduplicates and formats tags with semicolon separators
- ✅ Creates a concise "Short Summary" field (≤128 characters)
- ✅ Merges notes and search criteria into "Add to Import Note"
- ✅ Maps all standard FUB fields to Sierra's expected headers
- ✅ Processes multiple CSV files in batch

---

## 🚀 Quick Start - Web Application (Recommended)

The easiest way to use this tool is through the professional web interface:

### Local Development

**1. Clone and setup:**
```bash
git clone https://github.com/jsayram/FUB-to-Sierra-CSV-Converter.git
cd FUB-to-Sierra-CSV-Converter
python3 -m venv .env
source .env/bin/activate  # Windows: .env\Scripts\activate
pip install -r requirements.txt
```

**2. Configure environment:**
```bash
# Create .env file
cat > web_app/.env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
PAYMENT_LINK=your_stripe_payment_link_here
STRIPE_WEBHOOK_SECRET=your_webhook_secret_here
FLASK_DEBUG=true
EOF
```

**3. Run the application:**
```bash
python3 web_app/app.py
```

**4. Open browser:**
```
http://localhost:5001
```

### Web App Features:
- 🎯 **Drag & Drop Upload** - No file picker needed
- ✅ **Visual Column Mapping** - Check/uncheck columns with friendly UI
- 📊 **Live Conversion Log** - Dark-themed console showing progress
- ⬇️ **Instant Downloads** - Download converted files or ZIP
- 💳 **Stripe Integration** - Optional payment links for monetization
- 🔄 **Automatic Chunking** - Files >5,000 rows split automatically
- 🛡️ **Download Protection** - Warns before page reload
- 🎨 **Dark/Light Mode** - Professional UI with theme toggle

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=web_app --cov-report=html

# Specific test file
pytest tests/test_converter.py -v
```

### Test Coverage

- **62 comprehensive tests** covering all critical functionality
- **65% code coverage** focused on user-facing features

**Test Categories:**
- ✅ Phone normalization (11 formats) - `test_converter.py`
- ✅ Tag deduplication (9 scenarios) - `test_converter.py`
- ✅ File upload/download workflows - `test_upload_download.py`
- ✅ Large file chunking (6000+ rows) - `test_upload_download.py`
- ✅ Session isolation - `test_cleanup.py`
- ✅ Cleanup on reload/reset - `test_cleanup.py`
- ✅ End-to-end workflows - `test_integration.py`

---

## 🌐 Production Deployment

### Deploy to Railway (Recommended)

Railway offers $5 free credit/month - perfect for this app!

**Quick Deploy:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and initialize
railway login
railway init

# Set environment variables
railway variables set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
railway variables set PAYMENT_LINK=your_stripe_payment_link
railway variables set STRIPE_WEBHOOK_SECRET=your_webhook_secret
railway variables set FLASK_DEBUG=false

# Deploy
railway up

# Get URL
railway domain
```

**Auto-Deploy from GitHub:**
1. Go to [railway.app/new](https://railway.app/new)
2. Click "Deploy from GitHub repo"
3. Select `jsayram/FUB-to-Sierra-CSV-Converter`
4. Add environment variables in Railway dashboard
5. Railway auto-deploys on every push to `main`! 🚀

**📖 Full Guides:**
- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Complete deployment guide
- [DEPLOYMENT_WORKFLOW.md](DEPLOYMENT_WORKFLOW.md) - Auto-deploy workflow
- [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md) - Stripe webhook configuration

---

## 💳 Stripe Setup

### Payment Link Configuration

1. Go to [Stripe Dashboard → Payment Links](https://dashboard.stripe.com/payment-links)
2. Create new link:
   - **Product**: FUB to Sierra CSV Conversion
   - **Price**: $5.00 USD
   - **Billing**: One-time payment
3. Copy payment link URL
4. Add to `.env` or Railway variables

### Webhook Setup

**Local Development:**
```bash
stripe login
stripe listen --forward-to localhost:5001/webhook
# Copy webhook secret to .env
```

**Production:**
1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Add endpoint: `https://your-app.up.railway.app/webhook`
3. Select events: `checkout.session.completed`, `payment_intent.succeeded`
4. Copy secret to Railway variables

See [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md) for detailed instructions.

---

## 📊 Supported Fields

### Contact Information
First Name, Last Name, Email, Secondary Email, Phone, Secondary Phone, Source, Assigned To, Stage, Status

### Location
Street, City, State, ZIP, County, Country

### Dates
Created Date, Modified Date, Last Activity, Birthday, Anniversary

### Professional
Company, Title, Website, Spouse Name, Occupation, Employer

### Social Media
Facebook, LinkedIn, Twitter, Instagram

### Property Details
Home Price, Price Range (Min/Max), Beds/Baths (Min/Max), Property Type, Square Feet, Lot Size, Year Built

### MLS & Notes
Listing ID, MLS Number, Tags (auto-deduplicated), Notes, Search Criteria

### Custom Fields
Custom Field 1, 2, 3

---

## 📂 Project Structure

```
FUB-to-Sierra-CSV-Converter/
├── src/                           # Core conversion logic
│   └── fub_to_sierra.py          # CSV transformation engine
├── web_app/                       # Flask web application
│   ├── app.py                    # Main Flask app
│   ├── static/
│   │   ├── css/styles.css        # Professional UI
│   │   └── js/app.js             # Frontend logic
│   └── templates/
│       ├── index.html            # Main app page
│       ├── privacy.html          # Privacy policy
│       ├── terms.html            # Terms of service
│       └── refund-policy.html    # Refund policy
├── tests/                         # Test suite (62 tests)
│   ├── test_converter.py         # Core conversion
│   ├── test_upload_download.py  # File handling
│   ├── test_cleanup.py           # Session cleanup
│   └── test_integration.py       # End-to-end
├── railway.toml                   # Railway config
├── Procfile                       # Process definition
├── RAILWAY_DEPLOYMENT.md          # Deployment guide
├── DEPLOYMENT_WORKFLOW.md         # Auto-deploy guide
└── WEBHOOK_SETUP.md               # Webhook setup
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask session secret | Yes |
| `PAYMENT_LINK` | Stripe payment link | Yes |
| `STRIPE_WEBHOOK_SECRET` | Webhook secret | Yes |
| `FLASK_DEBUG` | Debug mode | No |

### File Limits

- **Max Upload**: 50 MB
- **Max Rows per File**: 5,000 (auto-chunks larger)
- **Retention**: 1 hour (auto-cleanup)
- **Session Timeout**: 31 days

---

## 🐛 Troubleshooting

**Files not showing after payment?**
- Payment links open in new tab to preserve session

**Files deleted on reload?**
- Intentional for privacy! Download before reloading

**Large file fails?**
- Files >50MB rejected. Split CSV before upload

**Railway deployment fails?**
- Check environment variables with `railway variables`

**Webhook verification fails?**
- Ensure `STRIPE_WEBHOOK_SECRET` matches Stripe dashboard

---

## 💻 Command Line Tool (Advanced)

For automated workflows and scripting, use the CLI version:

### Setup

```bash
# Place FUB CSV files in csv_input/
# Run conversion
python src/fub_to_sierra.py
# Retrieve converted files from csv_output/
```

### Configuration

Update `FUB_COLS` mapping in `src/fub_to_sierra.py` to match your FUB export headers:

```python
FUB_COLS = {
    'first_name': 'First Name',
    'last_name': 'Last Name',
    'email': 'Email',
    # ... customize to match your FUB headers
}
```

### Output Format

```
First Name, Last Name, Full Name, Email, Secondary Email,
Phone, Secondary Phone, Lead Source, Assigned Agent,
Street Address, City, State, Zip Code, Tags,
Short Summary, Add to Import Note
```

---

## 📄 License

MIT License

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure tests pass (`pytest tests/ -v`)
5. Commit changes (`git commit -m 'feat: Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

---

## 📈 Stats

- **62 Tests** - Comprehensive coverage
- **65% Coverage** - Critical user flows
- **<1 min** - Conversion time for 50k rows
- **$5/month** - Railway hosting cost
- **0 MB** - Server storage (privacy-focused)

---

**Last updated: November 14, 2025**
