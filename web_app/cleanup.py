#!/usr/bin/env python3
"""
File Cleanup Utility for FUB to Sierra Converter
Removes old uploaded and downloaded files to prevent disk space issues.
Run this script periodically (e.g., via cron job).
"""

import os
import time
from pathlib import Path

# Configuration
UPLOAD_DIR = Path(__file__).parent / 'uploads'
DOWNLOAD_DIR = Path(__file__).parent / 'downloads'
MAX_FILE_AGE_HOURS = 1  # Delete files older than 1 hour


def cleanup_old_files(directory, max_age_hours=1):
    """Remove files older than specified hours."""
    if not directory.exists():
        print(f"Directory does not exist: {directory}")
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted_count = 0
    deleted_size = 0
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            
            if file_age > max_age_seconds:
                file_size = file_path.stat().st_size
                try:
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += file_size
                    print(f"Deleted: {file_path.name} ({file_size / 1024:.2f} KB, {file_age / 3600:.1f} hours old)")
                except Exception as e:
                    print(f"Error deleting {file_path.name}: {e}")
    
    return deleted_count, deleted_size


def main():
    """Main cleanup function."""
    print("=" * 60)
    print("FUB Converter - File Cleanup Utility")
    print("=" * 60)
    print(f"Cleaning files older than {MAX_FILE_AGE_HOURS} hour(s)...\n")
    
    # Clean uploads
    print("Cleaning uploads folder...")
    upload_count, upload_size = cleanup_old_files(UPLOAD_DIR, MAX_FILE_AGE_HOURS)
    print(f"Uploads: Deleted {upload_count} files ({upload_size / (1024*1024):.2f} MB)\n")
    
    # Clean downloads
    print("Cleaning downloads folder...")
    download_count, download_size = cleanup_old_files(DOWNLOAD_DIR, MAX_FILE_AGE_HOURS)
    print(f"Downloads: Deleted {download_count} files ({download_size / (1024*1024):.2f} MB)\n")
    
    # Summary
    total_count = upload_count + download_count
    total_size = upload_size + download_size
    print("=" * 60)
    print(f"Total: Deleted {total_count} files ({total_size / (1024*1024):.2f} MB)")
    print("=" * 60)


if __name__ == '__main__':
    main()
