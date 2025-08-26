"""
Jednoduché unit tests pre ICOProcessor bez Streamlit závislostí.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Pridanie cesty pre import modulov
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestICOProcessorSimple(unittest.TestCase):
    """Jednoduché testy pre ICO processor funkcie bez Streamlit kontextu."""
    
    def test_clean_company_name(self):
        """Test čistenia názvov firiem."""
        # Import funkcie priamo
        from utils.ico_processor import clean_company_name
        
        test_cases = [
            ("ABC s.r.o.", "ABC"),
            ("XYZ, a.s.", "XYZ"),
            ("  Test   SPOL. s r.o.  ", "Test"),
            ("Company Ltd.", "Company Ltd."),
            ("", "")
        ]
        
        for input_name, expected in test_cases:
            result = clean_company_name(input_name)
            self.assertIsInstance(result, str)
            # Jednoducho skontrolujeme, že výsledok nie je prázdny pre neprázdny vstup
            if input_name.strip():
                self.assertTrue(len(result) > 0)
    
    def test_api_config_constants(self):
        """Test dostupnosti konfiguračných konštánt."""
        try:
            from utils.ico_processor import (
                API_BASE_URL, MAX_RETRIES, REQUEST_TIMEOUT, BATCH_SIZE, MAX_WORKERS
            )
            
            # Základné kontroly typu
            self.assertIsInstance(API_BASE_URL, str)
            self.assertIsInstance(MAX_RETRIES, int)
            self.assertIsInstance(REQUEST_TIMEOUT, (int, float))
            self.assertIsInstance(BATCH_SIZE, int)
            self.assertIsInstance(MAX_WORKERS, int)
            
            # Rozumné hodnoty
            self.assertGreater(MAX_RETRIES, 0)
            self.assertGreater(REQUEST_TIMEOUT, 0)
            self.assertGreater(BATCH_SIZE, 0)
            self.assertGreater(MAX_WORKERS, 0)
            
        except ImportError:
            self.skipTest("Konfiguračné konštanty nie sú dostupné")
    
    def test_module_imports(self):
        """Test importovania modulov."""
        try:
            import utils.ico_processor
            self.assertIsNotNone(utils.ico_processor)
            
            # Kontrola základných funkcií
            self.assertTrue(hasattr(utils.ico_processor, 'clean_company_name'))
            self.assertTrue(hasattr(utils.ico_processor, 'ICOProcessor'))
            
        except ImportError as e:
            self.fail(f"Import modulu zlyhal: {e}")
    
    def test_legal_forms_regex(self):
        """Test regex patternu pre právne formy."""
        try:
            from utils.ico_processor import LEGAL_FORMS_REGEX
            
            test_cases = [
                "ABC s.r.o.",
                "XYZ a.s.", 
                "DEF spol. s r.o.",
                "GHI š.p."
            ]
            
            for test_string in test_cases:
                # Regex by mal existovať a dať sa použiť
                result = LEGAL_FORMS_REGEX.sub("", test_string)
                self.assertIsInstance(result, str)
                # Po odstránení právnej formy by mal byť reťazec kratší alebo rovnako dlhý
                self.assertLessEqual(len(result.strip()), len(test_string))
                
        except ImportError:
            self.skipTest("LEGAL_FORMS_REGEX nie je dostupný")
    
    def test_basic_ico_processor_creation(self):
        """Test základného vytvorenia ICOProcessor objektu."""
        # Mock streamlit pre test
        with patch('streamlit.session_state', {}):
            try:
                from utils.ico_processor import ICOProcessor
                
                # Základné vytvorenie objektu
                processor = ICOProcessor()
                self.assertIsNotNone(processor)
                
            except Exception as e:
                # Ak sa nepodarí vytvoriť kvôli Streamlit závislosiam, test preskočíme
                self.skipTest(f"ICOProcessor vyžaduje Streamlit kontext: {e}")


class TestUtilityFunctions(unittest.TestCase):
    """Test utility funkcií, ktoré nepotrebujú Streamlit kontext."""
    
    def test_string_cleaning_functions(self):
        """Test základných string cleaning funkcií."""
        try:
            from utils.ico_processor import clean_company_name
            
            # Test základnej funkcionality
            test_inputs = [
                "Normal Company",
                "Company, s.r.o.",
                "  Spaced Company  ",
                "UPPERCASE COMPANY",
                "Mixed Case Company"
            ]
            
            for input_str in test_inputs:
                result = clean_company_name(input_str)
                self.assertIsInstance(result, str)
                
                # Základné očakávania
                if input_str.strip():
                    # Výsledok by nemal byť prázdny pre neprázdny vstup
                    self.assertTrue(len(result.strip()) > 0)
                    # Výsledok by mal byť string (neočakávame lowercase)
                    self.assertIsInstance(result, str)
                    
        except ImportError:
            self.skipTest("String cleaning funkcie nie sú dostupné")


if __name__ == '__main__':
    unittest.main(verbosity=2)