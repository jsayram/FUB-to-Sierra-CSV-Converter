#!/usr/bin/env python3
"""
Flask Web Application for FUB to Sierra CSV Converter
Provides a browser-based UI for converting Follow Up Boss exports to Sierra CRM format.
Includes Stripe payment integration.
"""

import os
import csv
import re
import uuid
import zipfile
import io
import time
from pathlib import Path
from textwrap import shorten
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['DOWNLOAD_FOLDER'] = Path(__file__).parent / 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 31  # 31 days in seconds

# Payment link configuration
PAYMENT_LINK = os.getenv('PAYMENT_LINK')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Ensure folders exist
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['DOWNLOAD_FOLDER'].mkdir(exist_ok=True)

# Sierra CRM output columns (fixed format)
SIERRA_COLS = [
    'First Name',
    'Last Name',
    'Full Name',
    'Email',
    'Secondary Email',
    'Phone',
    'Secondary Phone',
    'Lead Source',
    'Assigned Agent',
    'Street Address',
    'City',
    'State',
    'Zip Code',
    'Tags',
    'Short Summary',
    'Add to Import Note',
]

# Default FUB column mapping
DEFAULT_FUB_COLS = {
    'first_name': 'First Name',
    'last_name': 'Last Name',
    'email': 'Email',
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

SIERRA_MAX_ROWS = 5000


def normalize_phone(phone_str):
    """Extract digits from phone string and format as (XXX) XXX-XXXX."""
    if not phone_str:
        return ''
    
    digits = re.sub(r'\D', '', str(phone_str))
    
    if len(digits) == 10:
        return f'({digits[0:3]}) {digits[3:6]}-{digits[6:10]}'
    elif len(digits) == 11 and digits[0] == '1':
        return f'({digits[1:4]}) {digits[4:7]}-{digits[7:11]}'
    else:
        return phone_str.strip()


def normalize_tags(tags_str):
    """Split tags by common delimiters, deduplicate, and join with semicolons."""
    if not tags_str:
        return ''
    
    tags = re.split(r'[;,|]', str(tags_str))
    
    seen = set()
    unique = []
    for tag in tags:
        tag = tag.strip()
        if tag and tag not in seen:
            seen.add(tag)
            unique.append(tag)
    
    return '; '.join(unique)


def build_short_summary(row, fub_cols):
    """Create a ≤128 character summary from lead source and location."""
    source = row.get(fub_cols.get('source', ''), '').strip()
    city = row.get(fub_cols.get('city', ''), '').strip()
    state = row.get(fub_cols.get('state', ''), '').strip()
    
    parts = []
    if source:
        parts.append(f"Source: {source}")
    if city or state:
        loc = ', '.join(filter(None, [city, state]))
        parts.append(f"Location: {loc}")
    
    summary = ' | '.join(parts)
    return shorten(summary, width=128, placeholder='...')


def build_import_note(row, fub_cols):
    """Combine search criteria and notes into import note field."""
    criteria = row.get(fub_cols.get('search_criteria', ''), '').strip()
    notes = row.get(fub_cols.get('notes', ''), '').strip()
    
    parts = []
    if criteria:
        parts.append(f"Search Criteria: {criteria}")
    if notes:
        parts.append(f"Notes: {notes}")
    
    return '\n\n'.join(parts)


def convert_row(fub_row, fub_cols):
    """Convert a single FUB row dict to Sierra format dict."""
    first = fub_row.get(fub_cols.get('first_name', ''), '').strip()
    last = fub_row.get(fub_cols.get('last_name', ''), '').strip()
    
    full_name = ' '.join(filter(None, [first, last]))
    
    return {
        'First Name': first,
        'Last Name': last,
        'Full Name': full_name,
        'Email': fub_row.get(fub_cols.get('email', ''), '').strip(),
        'Secondary Email': fub_row.get(fub_cols.get('secondary_email', ''), '').strip(),
        'Phone': normalize_phone(fub_row.get(fub_cols.get('phone', ''), '')),
        'Secondary Phone': normalize_phone(fub_row.get(fub_cols.get('secondary_phone', ''), '')),
        'Lead Source': fub_row.get(fub_cols.get('source', ''), '').strip(),
        'Assigned Agent': fub_row.get(fub_cols.get('assigned_to', ''), '').strip(),
        'Street Address': fub_row.get(fub_cols.get('street', ''), '').strip(),
        'City': fub_row.get(fub_cols.get('city', ''), '').strip(),
        'State': fub_row.get(fub_cols.get('state', ''), '').strip(),
        'Zip Code': fub_row.get(fub_cols.get('zip', ''), '').strip(),
        'Tags': normalize_tags(fub_row.get(fub_cols.get('tags', ''), '')),
        'Short Summary': build_short_summary(fub_row, fub_cols),
        'Add to Import Note': build_import_note(fub_row, fub_cols),
    }


def convert_csv(input_path, fub_cols, log_callback=None):
    """Convert FUB CSV to Sierra format with logging."""
    sierra_rows = []
    
    with open(input_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        
        for row_num, fub_row in enumerate(reader, 1):
            sierra_row = convert_row(fub_row, fub_cols)
            sierra_rows.append(sierra_row)
            
            if log_callback:
                name = sierra_row['Full Name'] or '(No Name)'
                email = sierra_row['Email'] or '(No Email)'
                log_callback(f"Row {row_num}: {name} - {email}")
    
    return sierra_rows


def write_sierra_csv(output_path, sierra_rows):
    """Write Sierra rows to CSV file."""
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=SIERRA_COLS)
        writer.writeheader()
        writer.writerows(sierra_rows)


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', 
                         default_fub_cols=DEFAULT_FUB_COLS,
                         sierra_cols=SIERRA_COLS,
                         payment_link=PAYMENT_LINK)


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and conversion."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be a CSV'})
        
        # Get column mapping from request
        column_mapping = request.form.get('column_mapping', '{}')
        import json
        fub_cols = json.loads(column_mapping)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        session_id = str(uuid.uuid4())
        upload_path = app.config['UPLOAD_FOLDER'] / f"{session_id}_{filename}"
        file.save(upload_path)
        
        # Convert the CSV
        logs = []
        def log_message(msg):
            logs.append(msg)
        
        logs.append(f"Processing: {filename}")
        logs.append("=" * 60)
        
        sierra_rows = convert_csv(upload_path, fub_cols, log_message)
        total_rows = len(sierra_rows)
        
        logs.append("=" * 60)
        logs.append(f"Total rows processed: {total_rows}")
        
        # Generate preview (first 10 rows to show format)
        preview_rows = sierra_rows[:10] if len(sierra_rows) > 10 else sierra_rows
        preview_data = preview_rows  # Show full data to demonstrate format
        
        # Split into chunks if needed
        num_chunks = (total_rows + SIERRA_MAX_ROWS - 1) // SIERRA_MAX_ROWS
        output_files = []
        
        base_name = Path(filename).stem
        
        if num_chunks == 1:
            output_filename = f"{base_name}-sierra.csv"
            output_path = app.config['DOWNLOAD_FOLDER'] / f"{session_id}_{output_filename}"
            write_sierra_csv(output_path, sierra_rows)
            output_files.append({
                'filename': output_filename,
                'path': f"{session_id}_{output_filename}",
                'rows': total_rows
            })
            logs.append(f"Created: {output_filename} ({total_rows} rows)")
        else:
            logs.append(f"Splitting into {num_chunks} chunks (Sierra max: {SIERRA_MAX_ROWS} rows/file)")
            for chunk_num in range(num_chunks):
                start_idx = chunk_num * SIERRA_MAX_ROWS
                end_idx = min(start_idx + SIERRA_MAX_ROWS, total_rows)
                chunk_rows = sierra_rows[start_idx:end_idx]
                
                output_filename = f"{base_name}-sierra-chunk{chunk_num + 1}.csv"
                output_path = app.config['DOWNLOAD_FOLDER'] / f"{session_id}_{output_filename}"
                write_sierra_csv(output_path, chunk_rows)
                output_files.append({
                    'filename': output_filename,
                    'path': f"{session_id}_{output_filename}",
                    'rows': len(chunk_rows)
                })
                logs.append(f"Created: {output_filename} ({len(chunk_rows)} rows)")
        
        logs.append("=" * 60)
        logs.append("✓ Conversion complete!")
        
        # Clean up upload file
        upload_path.unlink()
        
        # Store conversion data in session for persistent download access
        session['conversion_id'] = session_id
        session['conversion_files'] = output_files
        session['conversion_timestamp'] = int(time.time())
        session['payment_completed'] = False  # Will be set to True after payment
        session.permanent = True  # Make session last 31 days
        
        return jsonify({
            'success': True,
            'logs': logs,
            'files': output_files,
            'total_rows': total_rows,
            'preview': preview_data,
            'preview_note': f'Showing first {len(preview_data)} of {total_rows} rows - Preview demonstrates format only',
            'session_id': session_id  # Send back for client-side tracking
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details,
            'logs': logs if 'logs' in locals() else []
        })


@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook for payment confirmation."""
    import stripe
    
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        if STRIPE_WEBHOOK_SECRET:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            # No webhook secret configured, parse JSON directly
            import json
            event = json.loads(payload)
        
        # Handle successful payment
        if event['type'] == 'checkout.session.completed':
            checkout_session = event['data']['object']
            session_id = checkout_session.get('id')
            customer_email = checkout_session.get('customer_details', {}).get('email', 'Unknown')
            amount = checkout_session.get('amount_total', 0) / 100
            
            print(f"✅ Payment successful!")
            print(f"   Session ID: {session_id}")
            print(f"   Customer: {customer_email}")
            print(f"   Amount: ${amount:.2f}")
            
            # Here you could:
            # - Store payment record in database
            # - Send confirmation email
            # - Mark files as paid for download
        
        return jsonify({'success': True}), 200
    
    except stripe.error.SignatureVerificationError as e:
        print(f"⚠️ Webhook signature verification failed: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/download/<path:filename>')
def download_file(filename):
    """Download a converted file."""
    try:
        file_path = app.config['DOWNLOAD_FOLDER'] / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Get original filename (without session ID prefix)
        original_name = '_'.join(filename.split('_')[1:])
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=original_name,
            mimetype='text/csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download_zip')
def download_zip():
    """Download all converted files as a ZIP archive."""
    try:
        # Check if user has completed payment
        if not session.get('payment_completed', False):
            return jsonify({'error': 'Payment required'}), 403
        
        # Get files from session
        conversion_files = session.get('conversion_files', [])
        session_id = session.get('conversion_id')
        
        if not conversion_files:
            return jsonify({'error': 'No files to download'}), 404
        
        # Create ZIP file in memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_info in conversion_files:
                file_path = app.config['DOWNLOAD_FOLDER'] / file_info['path']
                if file_path.exists():
                    # Add file to ZIP with clean name (no session ID)
                    zf.write(file_path, file_info['filename'])
        
        memory_file.seek(0)
        
        # Generate ZIP filename
        zip_name = f"sierra_converted_{session_id}.zip"
        
        return send_file(
            memory_file,
            as_attachment=True,
            download_name=zip_name,
            mimetype='application/zip'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/verify_payment')
def verify_payment():
    """Check if payment has been completed for this session."""
    payment_completed = session.get('payment_completed', False)
    conversion_files = session.get('conversion_files', [])
    
    return jsonify({
        'payment_completed': payment_completed,
        'has_files': len(conversion_files) > 0,
        'files': conversion_files if payment_completed else []
    })


@app.route('/mark_payment_complete')
def mark_payment_complete():
    """Mark payment as complete (called when user returns from Stripe)."""
    # In production, you'd verify this via webhook
    # For now, we trust the URL parameter from Stripe redirect
    if request.args.get('payment_success') == 'true':
        session['payment_completed'] = True
        return jsonify({'success': True})
    return jsonify({'success': False})


@app.route('/detect_columns', methods=['POST'])
def detect_columns():
    """Detect columns in uploaded CSV file."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        
        # Read just the header
        file.seek(0)
        content = file.read().decode('utf-8-sig')
        file.seek(0)
        
        reader = csv.DictReader(content.splitlines())
        detected_columns = list(reader.fieldnames)
        
        return jsonify({
            'success': True,
            'columns': detected_columns
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
