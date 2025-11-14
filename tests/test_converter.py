"""
Tests for core CSV conversion functionality
Ensures data transformation accuracy and reliability
"""

import pytest
from web_app.app import (
    normalize_phone,
    normalize_tags,
    build_short_summary,
    build_import_note,
    convert_row
)


class TestPhoneNormalization:
    """Test phone number normalization - critical for CRM data quality."""
    
    def test_normalize_10_digit_phone(self):
        """Test standard 10-digit phone number."""
        assert normalize_phone("5551234567") == "(555) 123-4567"
    
    def test_normalize_11_digit_phone_with_country_code(self):
        """Test 11-digit phone with leading 1 (US country code)."""
        assert normalize_phone("15551234567") == "(555) 123-4567"
    
    def test_normalize_phone_with_formatting(self):
        """Test phone already formatted - should preserve format."""
        assert normalize_phone("(555) 123-4567") == "(555) 123-4567"
    
    def test_normalize_phone_with_dashes(self):
        """Test phone with dash formatting."""
        assert normalize_phone("555-123-4567") == "(555) 123-4567"
    
    def test_normalize_phone_with_spaces(self):
        """Test phone with space formatting."""
        assert normalize_phone("555 123 4567") == "(555) 123-4567"
    
    def test_normalize_phone_with_dots(self):
        """Test phone with dot formatting."""
        assert normalize_phone("555.123.4567") == "(555) 123-4567"
    
    def test_normalize_phone_with_mixed_formatting(self):
        """Test phone with mixed non-digit characters."""
        assert normalize_phone("+1 (555) 123-4567") == "(555) 123-4567"
    
    def test_normalize_empty_phone(self):
        """Test empty phone number."""
        assert normalize_phone("") == ""
    
    def test_normalize_none_phone(self):
        """Test None phone number."""
        assert normalize_phone(None) == ""
    
    def test_normalize_invalid_phone_too_short(self):
        """Test invalid phone - too few digits."""
        result = normalize_phone("123")
        assert result == "123"  # Returns original if can't parse
    
    def test_normalize_invalid_phone_too_long(self):
        """Test invalid phone - too many digits."""
        result = normalize_phone("123456789012")
        assert result == "123456789012"  # Returns original


class TestTagNormalization:
    """Test tag deduplication and formatting - prevents duplicate imports."""
    
    def test_normalize_semicolon_separated_tags(self):
        """Test tags separated by semicolons."""
        assert normalize_tags("buyer; seller; investor") == "buyer; seller; investor"
    
    def test_normalize_comma_separated_tags(self):
        """Test tags separated by commas - converts to semicolons."""
        assert normalize_tags("buyer, seller, investor") == "buyer; seller; investor"
    
    def test_normalize_pipe_separated_tags(self):
        """Test tags separated by pipes - converts to semicolons."""
        assert normalize_tags("buyer|seller|investor") == "buyer; seller; investor"
    
    def test_deduplicate_tags(self):
        """Test duplicate tag removal - critical for data quality."""
        assert normalize_tags("buyer; buyer; seller; buyer") == "buyer; seller"
    
    def test_normalize_mixed_delimiters(self):
        """Test tags with mixed delimiters."""
        assert normalize_tags("buyer, seller; investor|lead") == "buyer; seller; investor; lead"
    
    def test_normalize_tags_with_whitespace(self):
        """Test tags with extra whitespace - should trim."""
        assert normalize_tags("  buyer  ;  seller  ;  investor  ") == "buyer; seller; investor"
    
    def test_normalize_empty_tags(self):
        """Test empty tag string."""
        assert normalize_tags("") == ""
    
    def test_normalize_none_tags(self):
        """Test None tags."""
        assert normalize_tags(None) == ""
    
    def test_normalize_tags_preserves_order(self):
        """Test that tag order is preserved after deduplication."""
        result = normalize_tags("zebra; apple; buyer; apple")
        assert result == "zebra; apple; buyer"


class TestShortSummary:
    """Test short summary generation - must fit Sierra's 128 char limit."""
    
    def test_summary_with_source_and_location(self):
        """Test summary with both source and location."""
        row = {'Source': 'Zillow', 'City': 'Austin', 'State': 'TX'}
        fub_cols = {'source': 'Source', 'city': 'City', 'state': 'State'}
        result = build_short_summary(row, fub_cols)
        assert result == "Source: Zillow | Location: Austin, TX"
    
    def test_summary_with_source_only(self):
        """Test summary with only source."""
        row = {'Source': 'Zillow', 'City': '', 'State': ''}
        fub_cols = {'source': 'Source', 'city': 'City', 'state': 'State'}
        result = build_short_summary(row, fub_cols)
        assert result == "Source: Zillow"
    
    def test_summary_with_location_only(self):
        """Test summary with only location."""
        row = {'Source': '', 'City': 'Austin', 'State': 'TX'}
        fub_cols = {'source': 'Source', 'city': 'City', 'state': 'State'}
        result = build_short_summary(row, fub_cols)
        assert result == "Location: Austin, TX"
    
    def test_summary_with_city_only(self):
        """Test summary with only city."""
        row = {'Source': '', 'City': 'Austin', 'State': ''}
        fub_cols = {'source': 'Source', 'city': 'City', 'state': 'State'}
        result = build_short_summary(row, fub_cols)
        assert result == "Location: Austin"
    
    def test_summary_truncates_long_text(self):
        """Test summary truncation at 128 characters."""
        long_source = "A" * 200
        row = {'Source': long_source, 'City': 'Austin', 'State': 'TX'}
        fub_cols = {'source': 'Source', 'city': 'City', 'state': 'State'}
        result = build_short_summary(row, fub_cols)
        assert len(result) <= 128
        assert "..." in result  # Should have ellipsis
    
    def test_summary_empty_when_no_data(self):
        """Test summary is empty when no source or location."""
        row = {'Source': '', 'City': '', 'State': ''}
        fub_cols = {'source': 'Source', 'city': 'City', 'state': 'State'}
        result = build_short_summary(row, fub_cols)
        assert result == ""


class TestImportNote:
    """Test import note building - captures additional data not in Sierra fields."""
    
    def test_import_note_with_notes(self):
        """Test import note includes FUB notes."""
        row = {'Notes': 'Looking for investment properties'}
        fub_cols = {'notes': 'Notes'}
        result = build_import_note(row, fub_cols)
        assert "Notes: Looking for investment properties" in result
    
    def test_import_note_with_search_criteria(self):
        """Test import note includes search criteria."""
        row = {'Search Criteria': '3 bed, 2 bath, Austin'}
        fub_cols = {'search_criteria': 'Search Criteria'}
        result = build_import_note(row, fub_cols)
        assert "Search Criteria: 3 bed, 2 bath, Austin" in result
    
    def test_import_note_empty_when_no_data(self):
        """Test import note is empty when no additional data."""
        row = {}
        fub_cols = {}
        result = build_import_note(row, fub_cols)
        assert result == ""


class TestRowConversion:
    """Test complete row conversion - ensures all fields map correctly."""
    
    def test_convert_row_basic_fields(self):
        """Test conversion of basic contact fields."""
        fub_row = {
            'First Name': 'John',
            'Last Name': 'Doe',
            'Email': 'john@example.com',
            'Phone': '5551234567',
            'City': 'Austin',
            'State': 'TX',
            'Source': 'Zillow'
        }
        fub_cols = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'phone': 'Phone',
            'city': 'City',
            'state': 'State',
            'source': 'Source'
        }
        
        result = convert_row(fub_row, fub_cols)
        
        assert result['First Name'] == 'John'
        assert result['Last Name'] == 'Doe'
        assert result['Full Name'] == 'John Doe'
        assert result['Email'] == 'john@example.com'
        assert result['Phone'] == '(555) 123-4567'  # Normalized
        assert result['City'] == 'Austin'
        assert result['State'] == 'TX'
        assert result['Lead Source'] == 'Zillow'
    
    def test_convert_row_full_name_generation(self):
        """Test full name is correctly generated from first and last."""
        fub_row = {'First Name': 'Jane', 'Last Name': 'Smith'}
        fub_cols = {'first_name': 'First Name', 'last_name': 'Last Name'}
        
        result = convert_row(fub_row, fub_cols)
        assert result['Full Name'] == 'Jane Smith'
    
    def test_convert_row_handles_missing_fields(self):
        """Test conversion handles missing optional fields gracefully."""
        fub_row = {'First Name': 'John'}
        fub_cols = {'first_name': 'First Name'}
        
        result = convert_row(fub_row, fub_cols)
        
        # Should not raise error, empty strings for missing fields
        assert result['First Name'] == 'John'
        assert result['Last Name'] == ''
        assert result['Email'] == ''
        assert result['Phone'] == ''
    
    def test_convert_row_normalizes_tags(self):
        """Test tags are normalized during conversion."""
        fub_row = {'Tags': 'buyer, buyer, seller'}
        fub_cols = {'tags': 'Tags'}
        
        result = convert_row(fub_row, fub_cols)
        assert result['Tags'] == 'buyer; seller'  # Deduplicated and formatted
