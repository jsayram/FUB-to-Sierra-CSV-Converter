"""
Tests for session and file cleanup functionality
Ensures user data is properly deleted for privacy and security
"""

import pytest
import json
import time
from pathlib import Path
from web_app.app import cleanup_session_files, cleanup_old_files


class TestSessionReset:
    """Test session reset clears user data."""
    
    def test_reset_session_clears_session_data(self, client, sample_csv_file, column_mapping):
        """Test session reset clears all session variables."""
        # Upload a file to create session data
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'test.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            client.post('/upload',
                       data=data,
                       content_type='multipart/form-data')
        
        # Verify session has data
        with client.session_transaction() as sess:
            assert 'conversion_id' in sess
            assert 'conversion_files' in sess
        
        # Reset session
        response = client.get('/reset_session')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        
        # Verify session is cleared
        with client.session_transaction() as sess:
            assert 'conversion_id' not in sess
            assert 'conversion_files' not in sess
    
    def test_reset_session_deletes_user_files(self, client, sample_csv_file, column_mapping, app):
        """Test session reset immediately deletes user's files from disk."""
        # Upload and convert
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'test.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            upload_response = client.post('/upload',
                                        data=data,
                                        content_type='multipart/form-data')
        
        json_data = upload_response.get_json()
        session_id = json_data['session_id']
        
        # Verify files exist
        download_folder = app.config['DOWNLOAD_FOLDER']
        session_files = list(download_folder.glob(f"{session_id}_*"))
        assert len(session_files) > 0, "Files should exist after upload"
        
        # Reset session
        client.get('/reset_session')
        
        # Verify files are deleted
        session_files_after = list(download_folder.glob(f"{session_id}_*"))
        assert len(session_files_after) == 0, "Files should be deleted after reset"


class TestCleanupSessionFiles:
    """Test cleanup_session_files() function."""
    
    def test_cleanup_deletes_all_session_files(self, client, sample_csv_file, column_mapping, app):
        """Test cleanup_session_files deletes all files for a given session."""
        # Upload to create files
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'test.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response = client.post('/upload',
                                 data=data,
                                 content_type='multipart/form-data')
        
        session_id = response.get_json()['session_id']
        
        # Verify files exist
        download_folder = app.config['DOWNLOAD_FOLDER']
        files_before = list(download_folder.glob(f"{session_id}_*"))
        assert len(files_before) > 0
        
        # Run cleanup
        deleted_count = cleanup_session_files(session_id)
        
        # Verify files deleted
        assert deleted_count > 0
        files_after = list(download_folder.glob(f"{session_id}_*"))
        assert len(files_after) == 0
    
    def test_cleanup_returns_correct_count(self, client, sample_csv_file, column_mapping, app):
        """Test cleanup_session_files returns correct number of deleted files."""
        # Upload to create files
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'test.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response = client.post('/upload',
                                 data=data,
                                 content_type='multipart/form-data')
        
        session_id = response.get_json()['session_id']
        
        # Count files
        download_folder = app.config['DOWNLOAD_FOLDER']
        expected_count = len(list(download_folder.glob(f"{session_id}_*")))
        
        # Run cleanup
        actual_count = cleanup_session_files(session_id)
        
        assert actual_count == expected_count
    
    def test_cleanup_handles_nonexistent_session(self, app):
        """Test cleanup_session_files handles non-existent session gracefully."""
        # Cleanup non-existent session should not raise error
        deleted_count = cleanup_session_files("nonexistent-session-id")
        assert deleted_count == 0


class TestCleanupOldFiles:
    """Test cleanup_old_files() function."""
    
    def test_cleanup_removes_old_files(self, app, tmp_path):
        """Test cleanup_old_files removes files older than 1 hour."""
        # Create a test file
        test_file = app.config['DOWNLOAD_FOLDER'] / "old_file.csv"
        test_file.write_text("test content")
        
        # Modify file timestamp to be 2 hours old
        two_hours_ago = time.time() - (2 * 60 * 60)
        test_file.touch()
        import os
        os.utime(test_file, (two_hours_ago, two_hours_ago))
        
        # Run cleanup
        deleted_count = cleanup_old_files()
        
        # File should be deleted
        assert not test_file.exists()
        assert deleted_count > 0
    
    def test_cleanup_preserves_recent_files(self, app):
        """Test cleanup_old_files does not delete recent files."""
        # Create a recent file
        recent_file = app.config['DOWNLOAD_FOLDER'] / "recent_file.csv"
        recent_file.write_text("test content")
        
        # Run cleanup
        cleanup_old_files()
        
        # Recent file should still exist
        assert recent_file.exists()
    
    def test_cleanup_handles_empty_directory(self, app):
        """Test cleanup_old_files handles empty directory gracefully."""
        # Should not raise error on empty directory
        deleted_count = cleanup_old_files()
        assert deleted_count >= 0


class TestFileIsolation:
    """Test file isolation between different user sessions."""
    
    def test_session_files_isolated(self, client, sample_csv_file, column_mapping):
        """Test files from different sessions are kept separate."""
        # User 1 upload
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'user1.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response1 = client.post('/upload',
                                  data=data,
                                  content_type='multipart/form-data')
        
        session_id_1 = response1.get_json()['session_id']
        
        # Reset for user 2
        client.get('/reset_session')
        
        # User 2 upload
        with open(sample_csv_file, 'rb') as f:
            data = {
                'file': (f, 'user2.csv'),
                'column_mapping': json.dumps(column_mapping)
            }
            response2 = client.post('/upload',
                                  data=data,
                                  content_type='multipart/form-data')
        
        session_id_2 = response2.get_json()['session_id']
        
        # Verify sessions are different
        assert session_id_1 != session_id_2
        
        # Cleanup user 1 files should not affect user 2
        cleanup_session_files(session_id_1)
        
        # User 2 files should still exist
        with client.session_transaction() as sess:
            # Current session is user 2
            pass
        
        # User 2's files should be downloadable
        user2_files = response2.get_json()['files']
        download_response = client.get(f"/download/{user2_files[0]['path']}")
        assert download_response.status_code == 200


class TestCleanupOnPageLoad:
    """Test automatic cleanup when page loads."""
    
    def test_index_triggers_cleanup(self, client, app):
        """Test accessing index page triggers automatic file cleanup."""
        # Create an old file
        old_file = app.config['DOWNLOAD_FOLDER'] / "old_test.csv"
        old_file.write_text("old content")
        
        # Make it old (2 hours)
        two_hours_ago = time.time() - (2 * 60 * 60)
        import os
        os.utime(old_file, (two_hours_ago, two_hours_ago))
        
        # Access index page
        client.get('/')
        
        # Old file should be cleaned up
        assert not old_file.exists()
