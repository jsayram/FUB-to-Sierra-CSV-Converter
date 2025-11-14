# FUB to Sierra CSV Converter

A Python tool that converts **Follow Up Boss** CSV exports into **Sierra CRM**-compatible CSV format. Available as both a **command-line tool** and a **web-based application**.

## 📋 What This Tool Does

This converter transforms Follow Up Boss contact exports into the exact format required by Sierra CRM, including:

- ✅ Normalizes phone numbers to `(XXX) XXX-XXXX` format
- ✅ Deduplicates and formats tags with semicolon separators
- ✅ Creates a concise "Short Summary" field (≤128 characters)
- ✅ Merges notes and search criteria into "Add to Import Note"
- ✅ Maps all standard FUB fields to Sierra's expected headers
- ✅ Processes multiple CSV files in batch

## 📂 Project Structure

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

**Access:** http://127.0.0.1:5001 (or http://localhost:5001)

**Payment:** Configure a Stripe payment link in `web_app/.env` to charge $9.99 per conversion (see `STRIPE_SETUP.md`)
# Last updated: Fri Nov 14 01:06:34 EST 2025
