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

```

## 🌐 Web Application (Recommended)

### Start the Web Server

```bash
python web_app/app.py
```

Then open your browser to: **http://localhost:5000**

### Features

- 🎯 **Drag & Drop** - Simply drag your FUB CSV file into the browser
- ✅ **Visual Column Mapping** - Check/uncheck columns with a friendly UI
- 📊 **Live Conversion Log** - Watch the conversion happen in real-time
- 📦 **Automatic Chunking** - Files >5,000 rows split automatically for Sierra
- ⬇️ **Instant Downloads** - Download converted files directly from the browser
- 🚨 **Error Handling** - Clear error messages if something goes wrong

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
- **Error Handling** - Clear error messages if something goes wrong

**Access:** http://127.0.0.1:5001 (or http://localhost:5001)
