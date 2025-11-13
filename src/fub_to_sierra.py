#!/usr/bin/env python3
"""
FUB to Sierra CSV Converter
Converts Follow Up Boss CSV exports to Sierra CRM-compatible format.
"""

import csv
import re
from pathlib import Path
from textwrap import shorten

# ========== CONFIGURATION ==========

# Map actual FUB column names to our internal keys
# UPDATE THESE to match your actual FUB export headers
FUB_COLS = {
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

# Input/output paths
INPUT_DIR = Path(__file__).parent.parent / 'csv_input'
OUTPUT_DIR = Path(__file__).parent.parent / 'csv_output'

# Sierra import limit
SIERRA_MAX_ROWS = 5000

# ========== HELPER FUNCTIONS ==========

def normalize_phone(phone_str):
    """
    Extract digits from phone string and format as (XXX) XXX-XXXX.
    Returns empty string if insufficient digits.
    """
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
    """
    Split tags by common delimiters, deduplicate, and join with semicolons.
    """
    if not tags_str:
        return ''
    
    # Split on semicolon, comma, or pipe
    tags = re.split(r'[;,|]', str(tags_str))
    
    # Clean, deduplicate, preserve order
    seen = set()
    unique = []
    for tag in tags:
        tag = tag.strip()
        if tag and tag not in seen:
            seen.add(tag)
            unique.append(tag)
    
    return '; '.join(unique)


def build_short_summary(row):
    """
    Create a ≤128 character summary from lead source and location.
    """
    source = row.get(FUB_COLS['source'], '').strip()
    city = row.get(FUB_COLS['city'], '').strip()
    state = row.get(FUB_COLS['state'], '').strip()
    
    parts = []
    if source:
        parts.append(f"Source: {source}")
    if city or state:
        loc = ', '.join(filter(None, [city, state]))
        parts.append(f"Location: {loc}")
    
    summary = ' | '.join(parts)
    return shorten(summary, width=128, placeholder='...')


def build_import_note(row):
    """
    Combine search criteria and notes into import note field.
    """
    criteria = row.get(FUB_COLS['search_criteria'], '').strip()
    notes = row.get(FUB_COLS['notes'], '').strip()
    
    parts = []
    if criteria:
        parts.append(f"Search Criteria: {criteria}")
    if notes:
        parts.append(f"Notes: {notes}")
    
    return '\n\n'.join(parts)


def convert_row(fub_row):
    """
    Convert a single FUB row dict to Sierra format dict.
    """
    first = fub_row.get(FUB_COLS['first_name'], '').strip()
    last = fub_row.get(FUB_COLS['last_name'], '').strip()
    
    # Build full name
    full_name = ' '.join(filter(None, [first, last]))
    
    return {
        'First Name': first,
        'Last Name': last,
        'Full Name': full_name,
        'Email': fub_row.get(FUB_COLS['email'], '').strip(),
        'Secondary Email': fub_row.get(FUB_COLS['secondary_email'], '').strip(),
        'Phone': normalize_phone(fub_row.get(FUB_COLS['phone'], '')),
        'Secondary Phone': normalize_phone(fub_row.get(FUB_COLS['secondary_phone'], '')),
        'Lead Source': fub_row.get(FUB_COLS['source'], '').strip(),
        'Assigned Agent': fub_row.get(FUB_COLS['assigned_to'], '').strip(),
        'Street Address': fub_row.get(FUB_COLS['street'], '').strip(),
        'City': fub_row.get(FUB_COLS['city'], '').strip(),
        'State': fub_row.get(FUB_COLS['state'], '').strip(),
        'Zip Code': fub_row.get(FUB_COLS['zip'], '').strip(),
        'Tags': normalize_tags(fub_row.get(FUB_COLS['tags'], '')),
        'Short Summary': build_short_summary(fub_row),
        'Add to Import Note': build_import_note(fub_row),
    }


# ========== MAIN CONVERSION ==========

def convert_fub_to_sierra(input_path, output_path):
    """
    Read FUB CSV, convert all rows, write Sierra CSV.
    Returns list of sierra rows for potential chunking.
    """
    with open(input_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        
        sierra_rows = []
        row_num = 0
        for fub_row in reader:
            row_num += 1
            sierra_row = convert_row(fub_row)
            sierra_rows.append(sierra_row)
            
            # Log progress every row
            name = sierra_row['Full Name'] or '(No Name)'
            email = sierra_row['Email'] or '(No Email)'
            print(f"  Row {row_num}: {name} - {email}")
    
    return sierra_rows


def write_sierra_csv(output_path, sierra_rows):
    """Write Sierra rows to CSV file."""
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=SIERRA_COLS)
        writer.writeheader()
        writer.writerows(sierra_rows)


def process_file_with_chunks(input_path):
    """
    Process a FUB CSV file and split into 5,000-row chunks for Sierra import.
    Returns list of (output_filename, row_count) tuples.
    """
    # Convert all rows
    sierra_rows = convert_fub_to_sierra(input_path, None)
    total_rows = len(sierra_rows)
    
    # Calculate number of chunks needed
    num_chunks = (total_rows + SIERRA_MAX_ROWS - 1) // SIERRA_MAX_ROWS  # Ceiling division
    
    output_files = []
    
    if num_chunks == 1:
        # Single file, no chunking needed
        output_filename = f"{input_path.stem}-sierra.csv"
        output_path = OUTPUT_DIR / output_filename
        write_sierra_csv(output_path, sierra_rows)
        output_files.append((output_filename, total_rows))
    else:
        # Multiple chunks needed
        for chunk_num in range(num_chunks):
            start_idx = chunk_num * SIERRA_MAX_ROWS
            end_idx = min(start_idx + SIERRA_MAX_ROWS, total_rows)
            chunk_rows = sierra_rows[start_idx:end_idx]
            
            output_filename = f"{input_path.stem}-sierra-chunk{chunk_num + 1}.csv"
            output_path = OUTPUT_DIR / output_filename
            write_sierra_csv(output_path, chunk_rows)
            output_files.append((output_filename, len(chunk_rows)))
    
    return output_files, total_rows


def main():
    """
    Process all CSV files in csv_input/ and create Sierra-formatted versions.
    Automatically splits files into 5,000-row chunks for Sierra import limits.
    """
    # Ensure directories exist
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all CSV files
    csv_files = list(INPUT_DIR.glob('*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in {INPUT_DIR}")
        print("Please add Follow Up Boss CSV exports to the csv_input/ folder.")
        return
    
    print(f"Found {len(csv_files)} CSV file(s) to process...\n")
    
    # Process each file
    for input_path in csv_files:
        try:
            print(f"\n{'='*60}")
            print(f"Processing: {input_path.name}")
            print(f"{'='*60}")
            
            output_files, total_rows = process_file_with_chunks(input_path)
            
            if len(output_files) == 1:
                # Single file output
                filename, count = output_files[0]
                print(f"\n✓ Processed {total_rows} rows from '{input_path.name}' into '{filename}'")
            else:
                # Multiple chunks
                print(f"\n✓ Processed {total_rows} rows from '{input_path.name}' into {len(output_files)} chunks:")
                for filename, count in output_files:
                    print(f"  - {filename}: {count} rows")
        except Exception as e:
            print(f"✗ Error processing '{input_path.name}': {e}")
    
    print(f"\nOutput files saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
