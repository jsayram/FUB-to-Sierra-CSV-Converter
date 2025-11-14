# FUB to Sierra CSV Converter

A professional web application that converts **Follow Up Boss (FUB)** CSV exports into **Sierra CRM**-compatible format with an intuitive drag-and-drop interface.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0.0-green)

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

## 💻 Command Line Tool

For automated workflows, use the CLI version:

```
FUB-to-Sierra-CSV-Converter/
├── .env/                 # Python virtual environment (created by you)
├── csv_input/            # Place your FUB CSV exports here
├── csv_output/           # Sierra-ready CSVs appear here
├── src/
│   └── fub_to_sierra.py  # Main conversion script
├── .gitignore
└── README.md
```

## 🚀 Setup Instructions

### 1. Create Python Virtual Environment

**Mac/Linux:**
```bash
python3 -m venv .env
```

**Windows:**
```cmd
python -m venv .env
```

### 2. Activate Virtual Environment

**Mac/Linux:**
```bash
source .env/bin/activate
```

**Windows:**
```cmd
.\.env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask and other required packages for the web application.

### 4. Configure Payment Link (Web App Only)

To monetize your web application:

```bash
cp web_app/.env.example web_app/.env
```

Then edit `web_app/.env` and add your Stripe payment link:

1. Create a payment link at https://dashboard.stripe.com/payment-links
2. Set product name: "FUB to Sierra CSV Conversion"
3. Set price: $9.99 (or your preferred amount)
4. Copy the payment link URL
5. Paste it into `web_app/.env`:
   ```
   PAYMENT_LINK=https://buy.stripe.com/test_xxxxxxxxxxxxx
   SECRET_KEY=your-generated-secret-key
   ```

See `STRIPE_SETUP.md` for detailed instructions.

```

### Web Application

1. Configure payment link (see STRIPE_SETUP.md):
```bash
cp web_app/.env.example web_app/.env
# Add your Stripe payment link to web_app/.env
```

2. Start the Flask server:
```bash
python web_app/app.py
```

3. Open your browser to `http://127.0.0.1:5001`

4. **Features:**
   - 🎯 Drag-and-drop file upload
   - 📋 Interactive column mapping
   - 📟 Real-time conversion logs
   - 💳 **Payment link integration** - Monetize with Stripe ($9.99 per conversion)
   - ⬇️ Automatic download of converted files
   - 📦 Handles large files with automatic chunking (5,000 rows max per file)

### How the Payment System Works

When users attempt to convert a file:

1. A payment notice appears with your Stripe payment link
2. Users click the link and complete payment on Stripe's secure checkout
3. After payment, users return and can upload/convert their file
4. No credit card data touches your server - Stripe handles everything

**Note:** You can skip payment setup for free conversions. Just don't configure the payment link.

### How to Use the Web App

1. Start the server with `python web_app/app.py`
2. Open http://localhost:5000 in your browser
3. Drag and drop (or click to browse) your FUB CSV file
4. Review detected columns and adjust mappings if needed
5. Click "Convert to Sierra Format"
6. Watch the conversion progress in the console
7. Download your converted file(s)

---

## 💻 Command Line Tool

For automated/scripted workflows, use the command-line version.

## ⚙️ Configuration (IMPORTANT!)

Before running the script, you **must update the `FUB_COLS` mapping** in `src/fub_to_sierra.py` to match your actual Follow Up Boss export headers.

Open `src/fub_to_sierra.py` and find this section:

```python
FUB_COLS = {
    'first_name': 'First Name',        # ← Update these strings
    'last_name': 'Last Name',          # ← to match your actual
    'email': 'Email',                  # ← FUB CSV headers
    'secondary_email': 'Secondary Email',
    'phone': 'Phone',
    'secondary_phone': 'Secondary Phone',
    'source': 'Source',
    'assigned_to': 'Assigned To',
    'street': 'Street',
    'city': 'City',
    'state': 'State',
    'zip': 'Zip',
    'tags': 'Tags',
    'notes': 'Notes',
    'search_criteria': 'Search Criteria',
}
```

**Example:** If your FUB export uses `"Primary Phone"` instead of `"Phone"`, change:

```python
'phone': 'Primary Phone',
```

## 📥 Usage

### 1. Place Input Files

Copy your Follow Up Boss CSV export(s) into the `csv_input/` directory.

### 2. Run the Converter

```bash
python src/fub_to_sierra.py
```

### 3. Retrieve Output Files

The script will create Sierra-formatted CSV files in `csv_output/` with the naming pattern:

```
original_filename-sierra.csv
```

### Example Output

```
Found 1 CSV file(s) to process...

✓ Processed 25280 rows from 'fub_export.csv' into 'fub_export-sierra.csv'

Output files saved to: /path/to/csv_output
```

## 📊 Sierra CSV Output Format

The tool generates CSV files with these exact columns:

```
First Name
Last Name
Full Name
Email
Secondary Email
Phone
Secondary Phone
Lead Source
Assigned Agent
Street Address
City
State
Zip Code
Tags
Short Summary
Add to Import Note
```

---

## 🚀 Production Deployment

Ready to deploy your app to production? Follow this guide:

### Prerequisites

1. ✅ `.env` file configured with:
   - `SECRET_KEY` - Random 64-character hex string
   - `PAYMENT_LINK` - Your Stripe payment link (optional)
   - `FLASK_DEBUG=false` - Production mode

2. ✅ Test app locally first:
   ```bash
   python web_app/app.py
   # Visit http://localhost:5001
   # Upload a test CSV and verify conversion works
   ```

### Deploy to Railway.app (Recommended)

**Why Railway?**
- ✅ $5 free credit/month (enough for low traffic)
- ✅ Custom domain with free SSL
- ✅ No sleep/cold starts
- ✅ Auto-deploy from GitHub
- ✅ Deploy in 5 minutes

**Step 1: Install Railway CLI**
```bash
npm i -g @railway/cli
```

**Step 2: Login**
```bash
railway login
```

**Step 3: Initialize Project**
```bash
railway init
# Choose: Create new project
# Name: fub-sierra-converter (or your choice)
```

**Step 4: Set Environment Variables**
```bash
# Copy your SECRET_KEY from web_app/.env
railway variables set SECRET_KEY=your-secret-key-here

# Add Stripe payment link (if using)
railway variables set PAYMENT_LINK=your-stripe-link

# Set production mode
railway variables set FLASK_DEBUG=false
```

**Step 5: Deploy**
```bash
railway up
```

**Step 6: Open Your App**
```bash
railway open
```

**Step 7: Add Custom Domain (Optional)**
```bash
railway domain
# Follow prompts to add yourdomain.com
# Then add CNAME record at your DNS provider
```

**Complete Guide:** See `RAILWAY_DEPLOYMENT.md` for detailed instructions, troubleshooting, and custom domain setup.

### Alternative Platforms

**Fly.io (Free Tier):**
- See `HEROKU_DEPLOYMENT.md` for Fly.io setup
- Truly free tier with 256MB RAM
- Great for testing

**Render.com (Free with Sleep):**
- Easy deployment from GitHub
- Free tier sleeps after 15 min inactivity
- Good for low-traffic sites

**Cost Comparison:**

| Platform | Free Tier | Always-On | Custom Domain |
|----------|-----------|-----------|---------------|
| Railway | $5 credit/mo | ✅ Yes | ✅ Free SSL |
| Fly.io | ✅ 256MB RAM | ✅ Yes | ✅ Free SSL |
| Render | ✅ 750hrs/mo | ❌ Sleeps | ✅ Free SSL |

### Post-Deployment Checklist

After deploying:

1. ✅ **Test conversion** - Upload a CSV and verify it works
2. ✅ **Test payment flow** - Click payment link, verify redirect works
3. ✅ **Check file cleanup** - Upload file, click "Convert Another File", verify files deleted
4. ✅ **Monitor logs** - Check for errors (`railway logs` or platform dashboard)
5. ✅ **Add custom domain** - If you have one
6. ✅ **Update Stripe** - Switch from test mode to live mode when ready
7. ✅ **Set up monitoring** - Check usage/costs weekly

### Production Features

Your app includes:

- ✅ **Automatic file cleanup** - Files deleted after 1 hour or on session reset
- ✅ **Session security** - Cryptographically signed with SECRET_KEY
- ✅ **Payment integration** - Stripe payment links (optional)
- ✅ **Error logging** - Rotating logs in `logs/` directory
- ✅ **Health endpoint** - `/health` for monitoring
- ✅ **No data retention** - Privacy-focused, session-only storage
- ✅ **Large file support** - Handles 50k+ rows with chunking
- ✅ **Concurrent users** - 4-8 users simultaneously (free tier)

### Scaling Guide

**As traffic grows:**

```bash
# Railway: Scale workers
railway variables set WORKERS=6

# Or upgrade memory
# Settings → Resources → Increase RAM
```

**For 100+ concurrent users:**
- See queuing system setup in conversation history
- Requires Celery + Redis
- Cost: ~$10-15/month

### Security Notes

🔒 **Your app is production-ready with:**
- Environment-based configuration
- Secure session handling
- No database (privacy-focused)
- Automatic file cleanup
- HTTPS enforced (on Railway/Fly/Render)

⚠️ **Remember to:**
- Never commit `.env` to git
- Rotate `SECRET_KEY` every 6-12 months
- Use Stripe live mode only when ready
- Monitor usage to avoid unexpected costs

---

## 🔧 Features Explained

### Phone Normalization

- Extracts digits from any phone format
- Converts to `(555) 123-4567` format
- Handles 10-digit and 11-digit (with leading 1) numbers

### Tag Deduplication

- Splits tags by semicolon, comma, or pipe
- Removes duplicates while preserving order
- Outputs as semicolon-separated list

### Short Summary (≤128 chars)

Automatically generated from:
- Lead source
- City/State location

Example: `Source: Zillow | Location: Austin, TX`

### Add to Import Note

Combines:
- **Search Criteria** from FUB
- **Notes** from FUB

Separated by double line breaks for readability.

## 🐛 Troubleshooting

### "No CSV files found in csv_input"

- Make sure you've placed `.csv` files in the `csv_input/` folder
- Check that files have the `.csv` extension (not `.CSV` or `.txt`)

### Missing Data in Output

- Verify `FUB_COLS` mapping matches your actual FUB headers exactly
- Column names are **case-sensitive**
- Open your FUB export in a text editor to see the exact header row

### Encoding Issues

- The script uses `utf-8-sig` encoding to handle BOM characters
- If you see garbled characters, check your FUB export encoding

## 📝 Notes

- The virtual environment (`.env/`) is excluded from git via `.gitignore`
- You can process multiple FUB exports in one run
- Original files in `csv_input/` are never modified
- Output files will overwrite existing files with the same name

## 🔄 Workflow Summary

1. Export contacts from Follow Up Boss as CSV
2. Place CSV in `csv_input/`
3. Update `FUB_COLS` if needed (first time only)
4. Run `python src/fub_to_sierra.py`
5. Import the output CSV from `csv_output/` into Sierra CRM

---

**Ready to convert!** Place your FUB exports in `csv_input/` and run the script.

---

## 🌐 Quick Start - Web Application

The easiest way to use this tool is through the web interface:

1. **Start the server:**
   ```bash
   python web_app/app.py
   ```

2. **Open your browser to:**
   ```
   http://127.0.0.1:5001
   ```

3. **Use the app:**
   - 🎯 Drag and drop your FUB CSV file
   - ✅ Review and adjust column mappings
   - 🔄 Click "Convert to Sierra Format"
   - 📊 Watch real-time conversion progress
   - ⬇️ Download your converted file(s)

### Web App Features:
- **Drag & Drop Interface** - No file picker needed, just drag your CSV
- **Visual Column Mapping** - Check/uncheck columns with friendly UI
- **Live Conversion Log** - Dark-themed console showing each row
- **Automatic Chunking** - Files >5,000 rows split automatically
- **Instant Downloads** - Download all chunks directly from browser
- **💳 Stripe Payment Integration** - Monetize conversions with payment links
- **Error Handling** - Clear error messages if something goes wrong

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
