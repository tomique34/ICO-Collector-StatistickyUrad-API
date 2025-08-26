#!/usr/bin/env python3
"""
Quick test runner pre overenie, že sú opravené 3 failing testy.
"""

import unittest
import sys
import os
from io import BytesIO
import pandas as pd

# Pridanie cesty
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_specific_failing_tests():
    """Spustí iba tie 3 testy, ktoré zlyhávali."""
    print("🧪 Testing the 3 previously failing tests")
    print("=" * 45)
    
    try:
        # Test 1: Excel download test
        print("1️⃣ Testing create_excel_download...")
        from utils.excel_handler import create_output_dataframe, create_excel_download
        
        # Test data
        test_df = pd.DataFrame({
            'Názov firmy': ['ABC s.r.o.', 'XYZ a.s.', '', 'DEF spol.', None],
            'Adresa': ['BA', 'KE', 'ZA', 'PE', 'NR']
        })
        
        test_results = {
            'ICO': ['12345', '', '67890', '', None],
            'Názov': ['ABC', '', 'DEF', '', '']
        }
        
        output_df = create_output_dataframe(test_df, 'Názov firmy', test_results)
        excel_buffer = create_excel_download(output_df)
        
        # Validation
        assert isinstance(excel_buffer, BytesIO), "Excel buffer should be BytesIO"
        assert len(excel_buffer.getvalue()) > 0, "Excel buffer should not be empty"
        
        # Test reading back
        excel_buffer.seek(0)
        df_test = pd.read_excel(excel_buffer)
        assert len(df_test) > 0, "Read Excel should have data"
        assert len(df_test) <= len(output_df), "Read Excel should have <= original rows"
        print("   ✅ create_excel_download - PASS")
        
    except Exception as e:
        print(f"   ❌ create_excel_download - FAIL: {e}")
        return False
    
    try:
        # Test 2: Excel file validation
        print("2️⃣ Testing validate_excel_file...")
        from utils.excel_handler import validate_excel_file
        
        class MockFile:
            def __init__(self, name, size=100):
                self.name = name
                self.size = size
        
        mock_file = MockFile('test.txt')
        is_valid, message = validate_excel_file(mock_file)
        
        assert not is_valid, "Invalid file should return False"
        assert 'formát' in message, f"Message should contain 'formát', got: '{message}'"
        print("   ✅ validate_excel_file - PASS")
        
    except Exception as e:
        print(f"   ❌ validate_excel_file - FAIL: {e}")
        return False
    
    try:
        # Test 3: String cleaning function
        print("3️⃣ Testing clean_company_name...")
        from utils.ico_processor import clean_company_name
        
        test_cases = [
            "Normal Company",
            "Company, s.r.o.",
            "  Spaced Company  ",
        ]
        
        for test_input in test_cases:
            result = clean_company_name(test_input)
            assert isinstance(result, str), f"Result should be string, got {type(result)}"
            if test_input.strip():
                assert len(result.strip()) > 0, f"Result should not be empty for '{test_input}'"
        
        print("   ✅ clean_company_name - PASS")
        
    except Exception as e:
        print(f"   ❌ clean_company_name - FAIL: {e}")
        return False
    
    print("\n🎉 All 3 previously failing tests now PASS!")
    return True

if __name__ == '__main__':
    try:
        success = run_specific_failing_tests()
        if success:
            print("\n✅ Test fixes verification: SUCCESS")
            sys.exit(0)
        else:
            print("\n❌ Test fixes verification: FAILED")  
            sys.exit(1)
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Run: pip install -r requirements_streamlit.txt")
        sys.exit(1)