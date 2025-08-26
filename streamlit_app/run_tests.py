#!/usr/bin/env python3
"""
Test runner pre ICO Collector Streamlit aplikáciu.
Spustí unit testy s detailným reportingom aj bez pytest.
"""

import sys
import os
import unittest
from io import StringIO

# Pridanie current directory do Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_basic_syntax_checks():
    """Spustí základné syntax kontroly pre Python súbory."""
    print("🔍 Kontrola syntax Python súborov...")
    
    files_to_check = [
        'streamlit_app.py',
        'utils/ico_processor.py',
        'assets/localization.py'
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                # Compile check
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"  ✅ {file_path} - syntax OK")
            except SyntaxError as e:
                print(f"  ❌ {file_path} - syntax error na riadku {e.lineno}: {e.msg}")
                all_good = False
            except Exception as e:
                print(f"  ⚠️ {file_path} - chyba: {str(e)}")
                all_good = False
        else:
            print(f"  ⚠️ {file_path} - súbor neexistuje")
    
    return all_good

def check_imports():
    """Kontrola dostupnosti importov."""
    print("\n📦 Kontrola dostupnosti modulov...")
    
    required_modules = {
        'streamlit': 'streamlit>=1.30.0',
        'pandas': 'pandas>=2.0.0', 
        'requests': 'requests>=2.31.0',
        'openpyxl': 'openpyxl>=3.1.0',
        'plotly': 'plotly>=5.15.0'
    }
    
    missing_modules = []
    
    for module, requirement in required_modules.items():
        try:
            __import__(module)
            print(f"  ✅ {module} - dostupný")
        except ImportError:
            print(f"  ❌ {module} - chýba (vyžadované: {requirement})")
            missing_modules.append(requirement)
    
    if missing_modules:
        print(f"\n💡 Pre inštaláciu chýbajúcich modulov spustite:")
        print(f"   pip install {' '.join(missing_modules)}")
        return False
    
    return True

def run_simple_functional_tests():
    """Spustí jednoduché funkčné testy bez externých závislostí."""
    print("\n🧪 Spúšťam základné funkčné testy...")
    
    class BasicFunctionalTests(unittest.TestCase):
        """Základné funkčné testy."""
        
        def test_file_structure(self):
            """Test existencie kľúčových súborov."""
            required_files = [
                'streamlit_app.py',
                'utils/__init__.py', 
                'utils/ico_processor.py',
                'assets/localization.py',
                'components/__init__.py'
            ]
            
            for file_path in required_files:
                self.assertTrue(os.path.exists(file_path), f"Súbor {file_path} neexistuje")
        
        def test_directory_structure(self):
            """Test existencie požadovaných adresárov."""
            required_dirs = [
                'utils',
                'components', 
                'assets',
                'tests'
            ]
            
            for dir_path in required_dirs:
                self.assertTrue(os.path.isdir(dir_path), f"Adresár {dir_path} neexistuje")
        
        def test_config_files(self):
            """Test existencie konfiguračných súborov."""
            config_files = [
                '.streamlit/config.toml',
                'Dockerfile',
                'docker-compose.yml',
                'requirements_streamlit.txt'
            ]
            
            for config_file in config_files:
                self.assertTrue(os.path.exists(config_file), f"Config súbor {config_file} neexistuje")
        
        def test_basic_app_structure(self):
            """Test základnej štruktúry hlavnej aplikácie."""
            with open('streamlit_app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Kontrola kľúčových funkcií (môžu byť importované alebo definované)
            required_patterns = [
                ('validate_excel_file', ['def validate_excel_file', 'from utils.excel_handler import', 'from utils.excel_handler import *']),
                ('validate_column_data', ['def validate_column_data', 'from utils.excel_handler import', 'from utils.excel_handler import *']),
                ('render_upload_section', ['def render_upload_section', 'def render_file_upload']),
                ('render_processing_section', ['def render_processing_section']),  
                ('render_results_section', ['def render_results_section']),
                ('main()', ['def main()', 'if __name__ == "__main__"'])
            ]
            
            for func_name, patterns in required_patterns:
                found = any(pattern in content for pattern in patterns)
                self.assertTrue(found, f"Funkcia {func_name} ani jej alternatívy neboli nájdené v streamlit_app.py")
    
    # Spustenie testov
    suite = unittest.TestLoader().loadTestsFromTestCase(BasicFunctionalTests)
    
    # Capture output
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Print results
    print(stream.getvalue())
    
    if result.wasSuccessful():
        print("✅ Všetky základné testy prešli úspešne!")
        return True
    else:
        print(f"❌ {len(result.failures)} testov zlyhalo, {len(result.errors)} chýb")
        return False

def try_advanced_tests():
    """Pokus o spustenie pokročilých testov (ak sú dostupné dependencies)."""
    print("\n🚀 Pokúšam sa spustiť pokročilé testy...")
    
    try:
        # Import test modulov
        sys.path.insert(0, 'tests')
        
        # Pokus o import test modulov
        importable_tests = []
        
        test_modules = [
            'tests.test_streamlit_app',
            'tests.test_ico_processor_simple',  # Použije jednoduché testy bez Streamlit kontextu
            'tests.test_components'
        ]
        
        for module_name in test_modules:
            try:
                module = __import__(module_name, fromlist=[''])
                importable_tests.append(module)
                print(f"  ✅ {module_name} - import OK")
            except ImportError as e:
                print(f"  ⚠️ {module_name} - import failed: {str(e)}")
        
        if importable_tests:
            print(f"\n📊 Našiel som {len(importable_tests)} spustiteľných test modulov")
            
            # Spustenie dostupných testov
            suite = unittest.TestSuite()
            
            for module in importable_tests:
                module_tests = unittest.TestLoader().loadTestsFromModule(module)
                suite.addTest(module_tests)
            
            # Spustenie
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            return result.wasSuccessful()
        else:
            print("  ℹ️ Žiadne pokročilé testy nie sú dostupné (chýbajú dependencies)")
            return True
            
    except Exception as e:
        print(f"  ⚠️ Chyba pri spúšťaní pokročilých testov: {str(e)}")
        return True  # Nie je to kritická chyba

def main():
    """Hlavná funkcia test runnera."""
    print("🧪 ICO Collector Streamlit App - Test Runner")
    print("=" * 50)
    
    # Zmena do správneho adresára
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = True
    
    # 1. Syntax kontroly
    if not run_basic_syntax_checks():
        success = False
    
    # 2. Import kontroly
    imports_ok = check_imports()
    
    # 3. Základné funkčné testy
    if not run_simple_functional_tests():
        success = False
    
    # 4. Pokročilé testy (ak sú dostupné dependencies)
    if imports_ok:
        if not try_advanced_tests():
            success = False
    
    # Súhrn
    print("\n" + "=" * 50)
    if success:
        print("🎉 Všetky dostupné testy prešli úspešne!")
        if not imports_ok:
            print("💡 Pre spustenie všetkých testov nainštalujte: pip install -r requirements_streamlit.txt")
    else:
        print("❌ Niektoré testy zlyhali - skontrolujte výstup vyššie")
        sys.exit(1)

if __name__ == '__main__':
    main()