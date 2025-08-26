#!/usr/bin/env python3
"""
Čistý test runner bez Streamlit warnings a s lepším reportingom.
"""

import unittest
import sys
import os
import warnings
import logging
from io import StringIO

# Potlačenie všetkých warnings
warnings.filterwarnings('ignore')

# Potlačenie Streamlit logs
logging.getLogger('streamlit').setLevel(logging.CRITICAL)

# Pridanie cesty
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Hlavná funkcia clean test runner."""
    print("🧪 ICO Collector - Clean Test Suite")
    print("=" * 40)
    
    # Zmena do správneho adresára
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Kontrola dependencies
    missing_deps = []
    required_modules = {
        'pandas': 'pandas>=2.0.0',
        'openpyxl': 'openpyxl>=3.1.0'
    }
    
    print("📦 Checking dependencies...")
    for module, requirement in required_modules.items():
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - missing")
            missing_deps.append(requirement)
    
    if missing_deps:
        print(f"\n💡 Install missing: pip install {' '.join(missing_deps)}")
        return False
    
    # Test suite
    print(f"\n🚀 Running test suite...")
    
    # Capture test output
    test_output = StringIO()
    
    # Spustenie testov s potlačeným outputom
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    try:
        # Načítanie iba funkčných testov
        from tests.test_streamlit_app import TestStreamlitApp, TestDataValidation
        from tests.test_ico_processor_simple import TestUtilityFunctions
        from tests.test_components import TestCustomValidators, TestErrorHandling
        
        # Pridanie specific test cases
        test_cases = [
            # Core functionality tests
            'test_validate_excel_file_success',
            'test_validate_excel_file_invalid_extension', 
            'test_validate_column_data_valid',
            'test_prepare_dataframe_for_processing',
            'test_create_excel_download',
            'test_create_csv_download',
            
            # Data handling tests
            'test_mixed_data_types',
            'test_special_characters_handling',
            
            # Utility tests
            'test_string_cleaning_functions',
            
            # Error handling
            'test_empty_dataframe_handling',
            'test_none_value_handling',
            
            # Validators
            'test_company_name_validator',
            'test_ico_format_validator'
        ]
        
        # Load specific tests
        for test_class in [TestStreamlitApp, TestDataValidation]:
            for test_case in test_cases:
                if hasattr(test_class, test_case):
                    suite.addTest(test_class(test_case))
        
        # Add utility tests
        suite.addTest(loader.loadTestsFromTestCase(TestUtilityFunctions))
        suite.addTest(loader.loadTestsFromTestCase(TestCustomValidators))
        suite.addTest(loader.loadTestsFromTestCase(TestErrorHandling))
        
        print(f"📊 Loaded {suite.countTestCases()} test cases")
        
    except ImportError as e:
        print(f"❌ Failed to load tests: {e}")
        return False
    
    # Spustenie s minimálnym outputom
    runner = unittest.TextTestRunner(
        stream=test_output,
        verbosity=1,
        buffer=True
    )
    
    result = runner.run(suite)
    
    # Custom reporting
    print(f"\n📈 Results Summary:")
    print(f"  • Tests run: {result.testsRun}")
    print(f"  • Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  • Failures: {len(result.failures)}")
    print(f"  • Errors: {len(result.errors)}")
    print(f"  • Skipped: {len(getattr(result, 'skipped', []))}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"  • Success rate: {success_rate:.1f}%")
    
    # Show only failures and errors (not the full traceback)
    if result.failures:
        print(f"\n❌ Failed tests:")
        for test, _ in result.failures:
            test_name = str(test).split()[0]
            print(f"  • {test_name}")
    
    if result.errors:
        print(f"\n💥 Error tests:")
        for test, _ in result.errors:
            test_name = str(test).split()[0] 
            print(f"  • {test_name}")
    
    # Final result
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️ {len(result.failures) + len(result.errors)} tests failed")
        print(f"📝 For detailed output run: python3 test_with_dependencies.py")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)