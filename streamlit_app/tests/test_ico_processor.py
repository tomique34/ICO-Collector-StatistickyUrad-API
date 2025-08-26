"""
Unit tests pre ICOProcessor triedu a utility funkcie.
Testuje API integráciu, dátové spracovanie a error handling.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
import requests

# Pridanie cesty pre import modulov
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ico_processor import ICOProcessor


class TestICOProcessor(unittest.TestCase):
    """Test cases pre ICOProcessor triedu."""
    
    def setUp(self):
        """Nastavenie pred každým testom."""
        self.processor = ICOProcessor()
        
        # Mock API odpoveď
        self.mock_api_response = {
            "resultCount": 1,
            "results": [{
                "ico": "12345678",
                "nazov": "Test s.r.o.",
                "adresa": {
                    "ulica": "Testovacia 1",
                    "obec": "Bratislava",
                    "psc": "81101"
                },
                "pravnaForma": "112",
                "datumVzniku": "2020-01-01"
            }]
        }
        
        # Mock prázdna API odpoveď
        self.mock_empty_response = {
            "resultCount": 0,
            "results": []
        }
    
    def test_initialization(self):
        """Test inicializácie ICOProcessor."""
        self.assertIsNotNone(self.processor.session)
        self.assertEqual(self.processor.stats['total_companies'], 0)
        self.assertEqual(self.processor.stats['processed_companies'], 0)
        self.assertEqual(self.processor.stats['successful_matches'], 0)
    
    def test_reset_stats(self):
        """Test resetovania štatistík."""
        # Nastavenie nejakých hodnôt
        self.processor.stats['total_companies'] = 10
        self.processor.stats['processed_companies'] = 5
        self.processor.stats['successful_matches'] = 3
        
        # Reset
        self.processor.reset_stats()
        
        # Kontrola
        self.assertEqual(self.processor.stats['total_companies'], 0)
        self.assertEqual(self.processor.stats['processed_companies'], 0)
        self.assertEqual(self.processor.stats['successful_matches'], 0)
        self.assertFalse(self.processor.stats['is_processing'])
    
    def test_get_processing_statistics(self):
        """Test získania štatistík spracovania."""
        # Nastavenie testových hodnôt
        self.processor.stats.update({
            'total_companies': 10,
            'processed_companies': 5,
            'successful_matches': 3,
            'failed_searches': 2,
            'is_processing': True
        })
        
        stats = self.processor.get_processing_statistics()
        
        self.assertEqual(stats['total_companies'], 10)
        self.assertEqual(stats['processed_companies'], 5) 
        self.assertEqual(stats['successful_matches'], 3)
        self.assertEqual(stats['success_rate'], 60.0)  # 3/5 * 100
        self.assertTrue(stats['is_processing'])
    
    @patch('utils.ico_processor.requests.Session.get')
    def test_search_company_success(self, mock_get):
        """Test úspešného vyhľadania firmy."""
        # Mock úspešnej odpovede
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_response
        mock_get.return_value = mock_response
        
        result = self.processor._search_company("Test s.r.o.")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['ico'], '12345678')
        self.assertEqual(result['nazov'], 'Test s.r.o.')
        self.assertIn('adresa', result)
        
        # Kontrola API volania
        mock_get.assert_called_once()
    
    @patch('utils.ico_processor.requests.Session.get')
    def test_search_company_not_found(self, mock_get):
        """Test vyhľadania neexistujúcej firmy."""
        # Mock prázdnej odpovede
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_empty_response
        mock_get.return_value = mock_response
        
        result = self.processor._search_company("Neexistujúca firma")
        
        self.assertIsNone(result)
        mock_get.assert_called_once()
    
    @patch('utils.ico_processor.requests.Session.get')
    def test_search_company_api_error(self, mock_get):
        """Test spracovania API chyby."""
        # Mock chybnej odpovede
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        result = self.processor._search_company("Test firma")
        
        self.assertIsNone(result)
        mock_get.assert_called_once()
    
    @patch('utils.ico_processor.requests.Session.get')
    def test_search_company_http_error(self, mock_get):
        """Test spracovania HTTP chyby."""
        # Mock 500 chyby
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_get.return_value = mock_response
        
        result = self.processor._search_company("Test firma")
        
        self.assertIsNone(result)
        mock_get.assert_called_once()
    
    def test_normalize_company_name(self):
        """Test normalizácie názvov firiem."""
        test_cases = [
            ("ABC s.r.o.", "abc sro"),
            ("XYZ, a.s.", "xyz as"),
            ("  Test   SPOL. s r.o.  ", "test spol sro"),
            ("Firma s &amp; Co.", "firma s co"),
            ("Company Ltd.", "company ltd")
        ]
        
        for input_name, expected in test_cases:
            normalized = self.processor._normalize_company_name(input_name)
            self.assertEqual(normalized, expected, 
                           f"Failed for input '{input_name}': expected '{expected}', got '{normalized}'")
    
    def test_generate_search_variants(self):
        """Test generovania variantov pre vyhľadávanie."""
        company_name = "ABC Software s.r.o."
        variants = self.processor._generate_search_variants(company_name)
        
        # Kontrola, že sa generujú rôzne varianty
        self.assertGreater(len(variants), 1)
        self.assertIn(company_name, variants)  # Pôvodný názov
        
        # Kontrola, že obsahuje kratšie varianty
        shorter_variants = [v for v in variants if len(v) < len(company_name)]
        self.assertGreater(len(shorter_variants), 0)
    
    @patch('utils.ico_processor.ICOProcessor._search_company')
    def test_process_single_company_success(self, mock_search):
        """Test spracovania jednej firmy - úspech."""
        # Mock úspešného vyhľadania
        mock_search.return_value = {
            'ico': '12345678',
            'nazov': 'Test s.r.o.',
            'adresa': {'ulica': 'Test 1', 'obec': 'Bratislava', 'psc': '11111'}
        }
        
        result = self.processor._process_single_company("Test s.r.o.")
        
        self.assertEqual(result['ico'], '12345678')
        self.assertEqual(result['nazov'], 'Test s.r.o.')
        self.assertEqual(result['match_strategy'], 'exact')
        self.assertIn('formatted_address', result)
        
        # Kontrola, že sa volal search len raz (úspešný hit)
        self.assertEqual(mock_search.call_count, 1)
    
    @patch('utils.ico_processor.ICOProcessor._search_company')
    def test_process_single_company_fallback(self, mock_search):
        """Test spracovania jednej firmy - fallback na varianty."""
        # Mock: prvé volanie neúspešné, druhé úspešné
        mock_search.side_effect = [None, {
            'ico': '87654321',
            'nazov': 'Test',
            'adresa': {'ulica': 'Test 2', 'obec': 'Košice', 'psc': '22222'}
        }]
        
        result = self.processor._process_single_company("Test s.r.o.")
        
        self.assertEqual(result['ico'], '87654321')
        self.assertEqual(result['match_strategy'], 'variant')
        
        # Kontrola, že sa volal search 2x
        self.assertEqual(mock_search.call_count, 2)
    
    @patch('utils.ico_processor.ICOProcessor._search_company')
    def test_process_single_company_not_found(self, mock_search):
        """Test spracovania jednej firmy - nenájdené."""
        # Mock: všetky volania neúspešné
        mock_search.return_value = None
        
        result = self.processor._process_single_company("Neexistujúca firma")
        
        self.assertIsNone(result['ico'])
        self.assertEqual(result['match_strategy'], 'none')
        
        # Kontrola, že sa vyskúšali rôzne varianty
        self.assertGreater(mock_search.call_count, 1)
    
    @patch('utils.ico_processor.ICOProcessor._process_single_company')
    def test_process_companies_with_progress(self, mock_process_single):
        """Test spracovania zoznamu firiem s progress tracking."""
        # Mock výsledkov
        mock_process_single.side_effect = [
            {'ico': '11111111', 'nazov': 'Firma 1', 'match_strategy': 'exact'},
            {'ico': None, 'nazov': '', 'match_strategy': 'none'},
            {'ico': '33333333', 'nazov': 'Firma 3', 'match_strategy': 'variant'}
        ]
        
        companies = ["Firma 1 s.r.o.", "Neznáma firma", "Firma 3 a.s."]
        results = self.processor.process_companies_with_progress(companies)
        
        # Kontrola výsledkov
        self.assertEqual(len(results['ICO']), 3)
        self.assertEqual(results['ICO'][0], '11111111')
        self.assertIsNone(results['ICO'][1])
        self.assertEqual(results['ICO'][2], '33333333')
        
        # Kontrola štatistík
        self.assertEqual(self.processor.stats['total_companies'], 3)
        self.assertEqual(self.processor.stats['processed_companies'], 3)
        self.assertEqual(self.processor.stats['successful_matches'], 2)
        self.assertFalse(self.processor.stats['is_processing'])
    
    def test_format_address(self):
        """Test formátovania adresy."""
        address_data = {
            'ulica': 'Testovacia 123',
            'obec': 'Bratislava',
            'psc': '81101'
        }
        
        formatted = self.processor._format_address(address_data)
        expected = "Testovacia 123, 81101 Bratislava"
        
        self.assertEqual(formatted, expected)
    
    def test_format_address_partial(self):
        """Test formátovania neúplnej adresy."""
        address_data = {
            'obec': 'Košice'
        }
        
        formatted = self.processor._format_address(address_data)
        self.assertEqual(formatted, "Košice")
    
    def test_format_address_empty(self):
        """Test formátovania prázdnej adresy."""
        formatted = self.processor._format_address({})
        self.assertEqual(formatted, "")
        
        formatted = self.processor._format_address(None)
        self.assertEqual(formatted, "")


class TestICOProcessorIntegration(unittest.TestCase):
    """Integračné testy pre ICOProcessor (vyžadujú internetové pripojenie)."""
    
    def setUp(self):
        """Nastavenie pred testami."""
        self.processor = ICOProcessor()
    
    @unittest.skip("Integračný test - spustiť manuálne")
    def test_real_api_call(self):
        """Test skutočného API volania (skip by default)."""
        # Test s reálnou firmou
        result = self.processor._search_company("Slovenské elektrárne")
        
        if result:  # Ak sa našla firma
            self.assertIsNotNone(result['ico'])
            self.assertIsInstance(result['ico'], str)
            self.assertEqual(len(result['ico']), 8)  # IČO má 8 čísel
    
    @unittest.skip("Integračný test - spustiť manuálne") 
    def test_real_processing_flow(self):
        """Test skutočného spracovania (skip by default)."""
        companies = ["Slovnaft", "Orange Slovensko"]
        results = self.processor.process_companies_with_progress(companies)
        
        # Základné kontroly
        self.assertEqual(len(results['ICO']), 2)
        self.assertIsInstance(results, dict)


if __name__ == '__main__':
    # Spustenie testov s verbose output
    unittest.main(verbosity=2, buffer=True)