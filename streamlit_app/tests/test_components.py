"""
Unit tests pre Streamlit komponenty.
Testuje jednotlivé UI komponenty a ich funkcionalitu.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import pandas as pd
from io import BytesIO

# Pridanie cesty pre import modulov
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import komponentov na testovanie
try:
    from components.file_upload import validate_uploaded_file
    from components.progress_display import create_progress_metrics
    from components.results_dashboard import create_results_summary
except ImportError as e:
    # Fallback ak komponenty nie sú dostupné
    print(f"Warning: Could not import components: {e}")


class TestFileUploadComponent(unittest.TestCase):
    """Test cases pre file upload komponent."""
    
    def setUp(self):
        """Nastavenie testových dát."""
        self.test_df = pd.DataFrame({
            'Názov firmy': ['ABC s.r.o.', 'XYZ a.s.', 'DEF spol.'],
            'IČO': ['12345678', '87654321', '11223344'],
            'Adresa': ['Bratislava', 'Košice', 'Žilina']
        })
    
    @unittest.skipIf('validate_uploaded_file' not in globals(), "Component not available")
    def test_validate_uploaded_file_excel(self):
        """Test validácie nahraného Excel súboru."""
        # Vytvorenie mock Excel súboru
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            self.test_df.to_excel(writer, sheet_name='TestSheet', index=False)
        excel_buffer.seek(0)
        
        is_valid, message = validate_uploaded_file(excel_buffer, 'test.xlsx')
        
        self.assertTrue(is_valid)
        self.assertIn('úspešne', message.lower())
    
    @unittest.skipIf('validate_uploaded_file' not in globals(), "Component not available")
    def test_validate_uploaded_file_invalid(self):
        """Test validácie neplatného súboru."""
        invalid_buffer = BytesIO(b'invalid content')
        
        is_valid, message = validate_uploaded_file(invalid_buffer, 'test.txt')
        
        self.assertFalse(is_valid)
        self.assertIn('nepodporovaný', message.lower())


class TestProgressDisplayComponent(unittest.TestCase):
    """Test cases pre progress display komponent."""
    
    @unittest.skipIf('create_progress_metrics' not in globals(), "Component not available")
    def test_create_progress_metrics(self):
        """Test vytvorenia progress metrík."""
        stats = {
            'total_companies': 100,
            'processed_companies': 45,
            'successful_matches': 38,
            'failed_searches': 7,
            'is_processing': True
        }
        
        metrics = create_progress_metrics(stats)
        
        self.assertIsInstance(metrics, dict)
        self.assertEqual(metrics['progress'], 0.45)  # 45/100
        self.assertEqual(metrics['success_rate'], 84.44)  # 38/45 * 100
    
    @unittest.skipIf('create_progress_metrics' not in globals(), "Component not available")
    def test_create_progress_metrics_zero_division(self):
        """Test progress metrík s nulami."""
        stats = {
            'total_companies': 0,
            'processed_companies': 0,
            'successful_matches': 0,
            'failed_searches': 0,
            'is_processing': False
        }
        
        metrics = create_progress_metrics(stats)
        
        self.assertEqual(metrics['progress'], 0.0)
        self.assertEqual(metrics['success_rate'], 0.0)


class TestResultsDashboardComponent(unittest.TestCase):
    """Test cases pre results dashboard komponent."""
    
    def setUp(self):
        """Nastavenie testových výsledkov."""
        self.test_results = {
            'ICO': ['12345678', '', '87654321', '', '11223344'],
            'Názov': ['Firma 1', '', 'Firma 3', '', 'Firma 5'],
            'Adresa': ['Adresa 1', '', 'Adresa 3', '', 'Adresa 5'],
            'MatchStrategy': ['exact', '', 'fuzzy', '', 'variant']
        }
    
    @unittest.skipIf('create_results_summary' not in globals(), "Component not available")
    def test_create_results_summary(self):
        """Test vytvorenia sumáru výsledkov."""
        summary = create_results_summary(self.test_results)
        
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary['total_processed'], 5)
        self.assertEqual(summary['successful_matches'], 3)
        self.assertEqual(summary['failed_searches'], 2)
        self.assertEqual(summary['success_rate'], 60.0)  # 3/5 * 100


class TestStreamlitUIIntegration(unittest.TestCase):
    """Integračné testy pre Streamlit UI komponenty."""
    
    def setUp(self):
        """Setup pre UI testy."""
        # Mock Streamlit session state
        self.mock_session_state = {}
    
    @patch('streamlit.session_state', new_callable=dict)
    def test_session_state_management(self, mock_st_session):
        """Test správy session state."""
        # Simulácia nastavenia session state
        mock_st_session['uploaded_file'] = 'test.xlsx'
        mock_st_session['processing_results'] = {'ICO': ['12345']}
        
        self.assertIn('uploaded_file', mock_st_session)
        self.assertIn('processing_results', mock_st_session)
        
        # Test čistenia session state
        mock_st_session.clear()
        self.assertEqual(len(mock_st_session), 0)
    
    def test_component_data_flow(self):
        """Test toku dát medzi komponentmi."""
        # Simulácia postupnosti: upload -> validation -> processing -> results
        
        # 1. File upload
        test_data = pd.DataFrame({'Companies': ['Test s.r.o.']})
        
        # 2. Validation
        self.assertFalse(test_data.empty)
        self.assertIn('Companies', test_data.columns)
        
        # 3. Processing simulation
        companies = test_data['Companies'].tolist()
        self.assertEqual(len(companies), 1)
        
        # 4. Results simulation
        results = {
            'ICO': ['12345678'],
            'Názov': ['Test s.r.o.'],
            'MatchStrategy': ['exact']
        }
        
        self.assertEqual(len(results['ICO']), len(companies))


class TestErrorHandling(unittest.TestCase):
    """Test cases pre error handling v komponentoch."""
    
    def test_empty_dataframe_handling(self):
        """Test spracovania prázdneho DataFrame."""
        empty_df = pd.DataFrame()
        
        # Simulácia komponentu, ktorý by mal zvládnuť prázdny DF
        try:
            result = len(empty_df)
            self.assertEqual(result, 0)
        except Exception as e:
            self.fail(f"Empty DataFrame handling failed: {e}")
    
    def test_missing_column_handling(self):
        """Test spracovania chýbajúceho stĺpca."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        # Test prístupu k neexistujúcemu stĺpcu
        with self.assertRaises(KeyError):
            _ = df['NonExistent']
    
    def test_none_value_handling(self):
        """Test spracovania None hodnôt."""
        test_data = [None, '', 'Valid', None, 'Another Valid']
        
        # Filtrovanie None a prázdnych hodnôt
        filtered = [x for x in test_data if x and str(x).strip()]
        
        self.assertEqual(len(filtered), 2)
        self.assertIn('Valid', filtered)
        self.assertIn('Another Valid', filtered)


class TestCustomValidators(unittest.TestCase):
    """Test cases pre custom validátory."""
    
    def test_ico_format_validator(self):
        """Test validátora formátu IČO."""
        def validate_ico_format(ico):
            """Validátor pre formát IČO."""
            if not ico:
                return False
            ico_str = str(ico).strip()
            return len(ico_str) == 8 and ico_str.isdigit()
        
        # Testy
        self.assertTrue(validate_ico_format('12345678'))
        self.assertTrue(validate_ico_format(12345678))
        self.assertFalse(validate_ico_format('1234567'))  # Príliš krátke
        self.assertFalse(validate_ico_format('123456789'))  # Príliš dlhé
        self.assertFalse(validate_ico_format('1234567a'))  # Obsahuje písmeno
        self.assertFalse(validate_ico_format(''))  # Prázdne
        self.assertFalse(validate_ico_format(None))  # None
    
    def test_company_name_validator(self):
        """Test validátora názvu firmy."""
        def validate_company_name(name):
            """Validátor pre názov firmy."""
            if not name:
                return False, "Názov firmy nemôže byť prázdny"
            
            name = str(name).strip()
            if len(name) < 2:
                return False, "Názov firmy je príliš krátky"
            if len(name) > 200:
                return False, "Názov firmy je príliš dlhý"
            
            return True, "OK"
        
        # Testy
        valid, msg = validate_company_name('ABC s.r.o.')
        self.assertTrue(valid)
        
        valid, msg = validate_company_name('A')
        self.assertFalse(valid)
        self.assertIn('krátky', msg)
        
        valid, msg = validate_company_name('')
        self.assertFalse(valid)
        self.assertIn('prázdny', msg)
        
        valid, msg = validate_company_name('A' * 201)
        self.assertFalse(valid)
        self.assertIn('dlhý', msg)


if __name__ == '__main__':
    # Spustenie testov s podrobným výstupom
    unittest.main(verbosity=2, buffer=True)