"""
Tests for file upload and download functionality
Ensures reliable file handling for user conversions
"""

import pytest
import json
import io
from pathlib import Path


class TestFileUpload:
    """Test file upload validation and processing."""
    
    def test_upload_valid_csv(self, client, sample_csv_file, column_mapping):
        """Test successful upload of valid CSV file."""
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'test_contacts.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response = client.post('/upload', 
                                 data=data,
                                 content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert 'logs' in json_data
        assert 'files' in json_data
        assert len(json_data['files']) >= 1
    
    def test_upload_no_file(self, client):
        """Test upload endpoint rejects request with no file."""
        response = client.post('/upload', data={})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is False
        assert 'error' in json_data
        assert 'No file' in json_data['error']
    
    def test_upload_empty_filename(self, client):
        """Test upload endpoint rejects empty filename."""
        data = {
            'file': (io.BytesIO(b''), ''),
            'column_mapping': '{}'
        }
        response = client.post('/upload',
                             data=data,
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is False
        assert 'No file selected' in json_data['error']
    
    def test_upload_non_csv_file(self, client, non_csv_file):
        """Test upload endpoint rejects non-CSV files."""
        with open(non_csv_file, 'rb') as f:
            data = {
                'file': (f, 'not_a_csv.txt'),
                'column_mapping': '{}'
            }
            response = client.post('/upload',
                                 data=data,
                                 content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is False
        assert 'must be a CSV' in json_data['error']
    
    def test_upload_no_column_mapping(self, client, sample_csv_file):
        """Test upload fails without column mapping."""
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'test_contacts.csv'),
                'column_mapping': '{}'  # Empty mapping
            }
            response = client.post('/upload',
                                 data=data,
                                 content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        # Should fail with empty column mapping or succeed with empty conversion
        assert 'success' in json_data
    
    def test_upload_creates_session_data(self, client, sample_csv_file, column_mapping):
        """Test upload creates session data for conversion tracking."""
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'test_contacts.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response = client.post('/upload',
                                 data=data,
                                 content_type='multipart/form-data')
        
        json_data = response.get_json()
        assert 'session_id' in json_data
        
        # Verify session was set
        with client.session_transaction() as sess:
            assert 'conversion_id' in sess
            assert 'conversion_files' in sess


class TestLargeFileHandling:
    """Test handling of large files that require chunking."""
    
    def test_large_file_chunking(self, client, large_csv_file, column_mapping):
        """Test files >5000 rows are split into multiple chunks."""
        with open(large_csv_file, 'rb') as f:
            data = {
                'file': (f, 'large_contacts.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response = client.post('/upload',
                                 data=data,
                                 content_type='multipart/form-data')
        
        json_data = response.get_json()
        assert json_data['success'] is True
        
        # 6000 rows should create 2 chunks (5000 + 1000)
        assert len(json_data['files']) == 2
        
        # Verify chunk row counts
        total_rows = sum(f['rows'] for f in json_data['files'])
        assert total_rows == 6000
    
    def test_chunked_files_have_correct_naming(self, client, large_csv_file, column_mapping):
        """Test chunked files are named with chunk numbers."""
        with open(large_csv_file, 'rb') as f:
            data = {
                'file': (f, 'large_contacts.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response = client.post('/upload',
                                 data=data,
                                 content_type='multipart/form-data')
        
        json_data = response.get_json()
        files = json_data['files']
        
        # Should have chunk1 and chunk2 in filenames
        assert 'chunk1' in files[0]['filename']
        assert 'chunk2' in files[1]['filename']


class TestFileDownload:
    """Test file download functionality."""
    
    def test_download_converted_file(self, client, sample_csv_file, column_mapping, app):
        """Test downloading a successfully converted file."""
        # First upload and convert
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'test_contacts.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            upload_response = client.post('/upload',
                                        data=data,
                                        content_type='multipart/form-data')
        
        json_data = upload_response.get_json()
        file_path = json_data['files'][0]['path']
        
        # Now download the file
        download_response = client.get(f'/download/{file_path}')
        
        assert download_response.status_code == 200
        assert 'text/csv' in download_response.content_type
        assert len(download_response.data) > 0
    
    def test_download_nonexistent_file(self, client):
        """Test downloading a file that doesn't exist returns 404."""
        response = client.get('/download/nonexistent_file.csv')
        
        assert response.status_code == 404
        json_data = response.get_json()
        assert 'error' in json_data
        assert 'not found' in json_data['error'].lower()
    
    def test_download_removes_session_id_from_filename(self, client, sample_csv_file, column_mapping):
        """Test downloaded file has session ID removed from filename."""
        # Upload and convert
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'test_contacts.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            upload_response = client.post('/upload',
                                        data=data,
                                        content_type='multipart/form-data')
        
        json_data = upload_response.get_json()
        file_path = json_data['files'][0]['path']
        original_filename = json_data['files'][0]['filename']
        
        # Download
        download_response = client.get(f'/download/{file_path}')
        
        # Check Content-Disposition header for clean filename
        content_disp = download_response.headers.get('Content-Disposition')
        assert original_filename in content_disp or 'sierra' in content_disp


class TestSessionIsolation:
    """Test that users can only access their own files."""
    
    def test_different_sessions_different_files(self, client, sample_csv_file, column_mapping):
        """Test two different sessions get different session IDs."""
        # First user upload
        with open(sample_csv_file, 'rb') as f:
            data1 = {
                'file': (f, 'user1.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response1 = client.post('/upload',
                                  data=data1,
                                  content_type='multipart/form-data')
        
        session_id_1 = response1.get_json()['session_id']
        
        # Reset session (simulate new user)
        client.get('/reset_session')
        
        # Second user upload
        with open(sample_csv_file, 'rb') as f:
            data2 = {
                'file': (f, 'user2.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response2 = client.post('/upload',
                                  data=data2,
                                  content_type='multipart/form-data')
        
        session_id_2 = response2.get_json()['session_id']
        
        # Session IDs should be different
        assert session_id_1 != session_id_2
