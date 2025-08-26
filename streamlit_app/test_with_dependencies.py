#!/usr/bin/env python3
"""
Test runner pre kompletné testy s dependencies.
Spustí opravenej verzie testov, ktoré by mali prechádzať.
"""

import sys
import os
import unittest

# Zmena do správneho adresára
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Pridanie path
sys.path.insert(0, script_dir)

def run_fixed_tests():
    """Spustí opravenej verzie testov."""
    print("🧪 Running Fixed Tests with Dependencies")
    print("=" * 45)
    
    # Kontrola dependencies
    missing_deps = []
    required_modules = ['streamlit', 'pandas', 'requests', 'plotly', 'openpyxl']
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - available")
        except ImportError:
            print(f"❌ {module} - missing")
            missing_deps.append(module)
    
    if missing_deps:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing_deps)}")
        print("📦 Install with: pip install -r requirements_streamlit.txt")
        return False
    
    print("\n🚀 Running tests...")
    
    # Test suite s opravenými testami
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Načítanie testov z opravených modulov
    try:
        from tests.test_streamlit_app import TestStreamlitApp, TestDataValidation
        from tests.test_ico_processor_simple import TestICOProcessorSimple, TestUtilityFunctions
        from tests.test_components import TestCustomValidators, TestErrorHandling
        
        # Pridanie testov do suite
        suite.addTest(loader.loadTestsFromTestCase(TestStreamlitApp))
        suite.addTest(loader.loadTestsFromTestCase(TestDataValidation))
        suite.addTest(loader.loadTestsFromTestCase(TestICOProcessorSimple))
        suite.addTest(loader.loadTestsFromTestCase(TestUtilityFunctions))
        suite.addTest(loader.loadTestsFromTestCase(TestCustomValidators))
        suite.addTest(loader.loadTestsFromTestCase(TestErrorHandling))
        
        print(f"📊 Loaded {suite.countTestCases()} test cases")
        
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        return False
    
    # Spustenie testov
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Výsledky
    print(f"\n📈 Test Results:")
    print(f"  • Tests run: {result.testsRun}")
    print(f"  • Failures: {len(result.failures)}")
    print(f"  • Errors: {len(result.errors)}")
    print(f"  • Skipped: {len(getattr(result, 'skipped', []))}")
    
    if result.failures:
        print(f"\n❌ Failed tests:")
        for test, traceback in result.failures:
            print(f"  • {test}")
    
    if result.errors:
        print(f"\n💥 Error tests:")
        for test, traceback in result.errors:
            print(f"  • {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️ Some tests failed - check output above")
    
    return success

if __name__ == '__main__':
    success = run_fixed_tests()
    sys.exit(0 if success else 1)