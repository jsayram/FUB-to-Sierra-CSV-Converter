"""
End-to-end integration tests
Tests complete user workflows to ensure reliability
"""

import pytest
import json


class TestCompleteWorkflow:
    """Test complete user workflow from upload to download to cleanup."""
    
    def test_full_conversion_workflow(self, client, sample_csv_file, column_mapping):
        """Test complete workflow: upload → convert → download → reset."""
        # Step 1: Upload and convert
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'contacts.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            upload_response = client.post('/upload',
                                        data=data,
                                        content_type='multipart/form-data')
        
        assert upload_response.status_code == 200
        upload_data = upload_response.get_json()
        assert upload_data['success'] is True
        assert len(upload_data['files']) > 0
        
        # Step 2: Download converted file
        file_path = upload_data['files'][0]['path']
        download_response = client.get(f'/download/{file_path}')
        
        assert download_response.status_code == 200
        assert len(download_response.data) > 0
        
        # Verify downloaded content is valid CSV
        csv_content = download_response.data.decode('utf-8')
        assert 'First Name' in csv_content  # Header present
        assert 'Last Name' in csv_content
        assert 'Full Name' in csv_content
        
        # Step 3: Reset session
        reset_response = client.get('/reset_session')
        
        assert reset_response.status_code == 200
        reset_data = reset_response.get_json()
        assert reset_data['success'] is True
        
        # Step 4: Verify session cleared
        with client.session_transaction() as sess:
            assert 'conversion_id' not in sess
    
    def test_workflow_data_accuracy(self, client, sample_csv_file, column_mapping):
        """Test converted data maintains accuracy throughout workflow."""
        # Upload and convert
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'contacts.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            upload_response = client.post('/upload',
                                        data=data,
                                        content_type='multipart/form-data')
        
        # Check preview data for accuracy
        upload_data = upload_response.get_json()
        preview = upload_data.get('preview', [])
        
        if preview:
            # Verify phone normalization
            for row in preview:
                if row.get('Phone'):
                    # Should be formatted as (XXX) XXX-XXXX
                    phone = row['Phone']
                    assert '(' in phone or phone == ''
            
            # Verify full name generation
            for row in preview:
                first = row.get('First Name', '')
                last = row.get('Last Name', '')
                full = row.get('Full Name', '')
                if first or last:
                    assert full == f"{first} {last}".strip()


class TestMultipleUsers:
    """Test concurrent user sessions don't interfere."""
    
    def test_concurrent_user_sessions(self, client, sample_csv_file, column_mapping):
        """Test multiple users can use app simultaneously without interference."""
        # User 1: Upload
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'user1.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response1 = client.post('/upload',
                                  data=data,
                                  content_type='multipart/form-data')
        
        user1_session = response1.get_json()['session_id']
        user1_files = response1.get_json()['files']
        
        # Simulate User 2 (reset session)
        client.get('/reset_session')
        
        # User 2: Upload
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'user2.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response2 = client.post('/upload',
                                  data=data,
                                  content_type='multipart/form-data')
        
        user2_session = response2.get_json()['session_id']
        user2_files = response2.get_json()['files']
        
        # Verify different sessions
        assert user1_session != user2_session
        
        # Verify different files
        assert user1_files[0]['path'] != user2_files[0]['path']


class TestHealthEndpoint:
    """Test health check endpoint for monitoring."""
    
    def test_health_check_returns_healthy(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get('/health')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'healthy'
        assert 'timestamp' in json_data
        assert 'service' in json_data
    
    def test_health_check_timestamp(self, client):
        """Test health endpoint includes current timestamp."""
        response = client.get('/health')
        json_data = response.get_json()
        
        import time
        current_time = time.time()
        health_time = json_data['timestamp']
        
        # Timestamp should be recent (within 5 seconds)
        assert abs(current_time - health_time) < 5


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_upload_handles_malformed_csv(self, client, tmp_path, column_mapping):
        """Test upload handles malformed CSV gracefully."""
        # Create malformed CSV
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("This is not,a valid\nCSV file with mismatched,columns,and,more")
        
        with open(bad_csv, 'rb') as f:
            data = {
                'file': (f, 'bad.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response = client.post('/upload',
                                 data=data,
                                 content_type='multipart/form-data')
        
        # Should handle gracefully (may succeed or fail, but shouldn't crash)
        assert response.status_code == 200
        json_data = response.get_json()
        # Either succeeds or has error message
        assert 'success' in json_data
    
    def test_routes_exist(self, client):
        """Test all critical routes are accessible."""
        routes = [
            ('/', 200),
            ('/health', 200),
            ('/terms', 200),
            ('/privacy', 200),
            ('/refund-policy', 200),
            ('/reset_session', 200),
        ]
        
        for route, expected_status in routes:
            response = client.get(route)
            assert response.status_code == expected_status, f"Route {route} failed"
