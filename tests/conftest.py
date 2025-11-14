"""
Pytest configuration and fixtures for test suite
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from web_app.app import app as flask_app


@pytest.fixture
def app():
    """Create Flask app configured for testing."""
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key-for-testing-only'
    
    # Use temporary directories for testing
    temp_upload = Path(tempfile.mkdtemp())
    temp_download = Path(tempfile.mkdtemp())
    
    flask_app.config['UPLOAD_FOLDER'] = temp_upload
    flask_app.config['DOWNLOAD_FOLDER'] = temp_download
    
    yield flask_app
    
    # Cleanup after tests
    shutil.rmtree(temp_upload, ignore_errors=True)
    shutil.rmtree(temp_download, ignore_errors=True)


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def sample_csv_content():
    """Sample FUB CSV content for testing."""
    return """First Name,Last Name,Email,Phone,City,State,Source,Tags,Notes
John,Doe,john@example.com,5551234567,Austin,TX,Zillow,buyer; investor,Looking for investment properties
Jane,Smith,jane@example.com,(555) 987-6543,Dallas,TX,Realtor.com,seller,Wants to sell home
Bob,Johnson,bob@example.com,555-111-2222,Houston,TX,Facebook,buyer; buyer; lead,First time home buyer"""


@pytest.fixture
def large_csv_content():
    """Generate large CSV content for chunking tests (6000 rows)."""
    header = "First Name,Last Name,Email,Phone,City,State,Source,Tags,Notes\n"
    rows = []
    for i in range(6000):
        rows.append(f"Person{i},LastName{i},person{i}@example.com,555{i:07d},City{i % 100},TX,Zillow,buyer,Note {i}")
    return header + "\n".join(rows)


@pytest.fixture
def sample_csv_file(tmp_path, sample_csv_content):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_contacts.csv"
    csv_file.write_text(sample_csv_content)
    return csv_file


@pytest.fixture
def large_csv_file(tmp_path, large_csv_content):
    """Create a large temporary CSV file for chunking tests."""
    csv_file = tmp_path / "large_contacts.csv"
    csv_file.write_text(large_csv_content)
    return csv_file


@pytest.fixture
def non_csv_file(tmp_path):
    """Create a non-CSV file for validation testing."""
    txt_file = tmp_path / "not_a_csv.txt"
    txt_file.write_text("This is not a CSV file")
    return txt_file


@pytest.fixture
def column_mapping():
    """Default column mapping for testing."""
    return {
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'email': 'Email',
        'phone': 'Phone',
        'city': 'City',
        'state': 'State',
        'source': 'Source',
        'tags': 'Tags',
        'notes': 'Notes'
    }
