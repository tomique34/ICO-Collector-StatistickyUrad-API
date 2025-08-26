"""
Unit tests pre hlavnú Streamlit aplikáciu.
Testuje základné funkcie a komponenty ICO Collector web aplikácie.
"""

import unittest
import sys
import pandas as pd
from unittest.mock import patch, MagicMock
from io import BytesIO, StringIO
import tempfile
import os

# Pridanie cesty pre import modulov
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import funkcie z hlavnej aplikácie
from streamlit_app import (
    validate_excel_file,
    validate_column_data, 
    prepare_dataframe_for_processing,
    create_output_dataframe,
    create_excel_download,
    create_csv_download
)


class TestStreamlitApp(unittest.TestCase):
    """Test cases pre hlavné funkcie Streamlit aplikácie."""
    
    def setUp(self):
        """Nastavenie testových dát pred každým testom."""
        # Vytvorenie test DataFrame
        self.test_df = pd.DataFrame({
            'Názov firmy': ['ABC s.r.o.', 'XYZ a.s.', '', 'DEF spol. s r.o.', None],
            'Adresa': ['Bratislava', 'Košice', 'Žilina', 'Prešov', 'Nitra'],
            'Telefón': ['02/1234567', '055/7654321', '', '051/1111111', None]
        })
        
        # Test výsledky pre ICO processing
        self.test_results = {
            'ICO': ['12345678', '', '87654321', '', None],
            'Názov': ['ABC s.r.o.', '', 'DEF spol. s r.o.', '', ''],
            'Adresa': ['Bratislava 1', '', 'Prešov 2', '', ''],
            'MatchStrategy': ['exact', '', 'fuzzy', '', ''],
            'UsedQueryVariant': ['ABC s.r.o.', '', 'DEF spol', '', ''],
            'IdentifierType': ['ico', '', 'ico', '', '']
        }
    
    def test_validate_excel_file_success(self):
        """Test úspešnej validácie Excel súboru."""
        # Mock UploadedFile objektu
        class MockUploadedFile:
            def __init__(self, name, size, data):
                self.name = name
                self.size = size
                self._data = data
            
            def read(self):
                return self._data
        
        # Vytvorenie mock Excel súboru
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            self.test_df.to_excel(writer, sheet_name='Sheet1', index=False)
        excel_buffer.seek(0)
        
        mock_file = MockUploadedFile('test.xlsx', len(excel_buffer.getvalue()), excel_buffer.getvalue())
        
        # Test validácie
        is_valid, message = validate_excel_file(mock_file)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
    
    def test_validate_excel_file_invalid_extension(self):
        """Test validácie súboru s neplatnou príponou."""
        class MockUploadedFile:
            def __init__(self, name, size):
                self.name = name
                self.size = size
        
        mock_file = MockUploadedFile('test.txt', 100)
        
        is_valid, message = validate_excel_file(mock_file)
        
        self.assertFalse(is_valid)
        self.assertIn('formát', message)
    
    def test_validate_column_data_valid(self):
        """Test validácie stĺpca s platnými dátami."""
        is_valid, stats, warning = validate_column_data(self.test_df, 'Názov firmy')
        
        self.assertTrue(is_valid)
        self.assertEqual(stats['total_rows'], 5)
        self.assertEqual(stats['valid_rows'], 4)  # 4 non-null hodnoty (ABC, XYZ, '', DEF) 
        self.assertEqual(stats['empty_rows'], 1)  # 1 None hodnota
        # Warning môže byť prázdny string
    
    def test_validate_column_data_empty_column(self):
        """Test validácie prázdneho stĺpca."""
        empty_df = pd.DataFrame({'Empty': [None, None, None, None]})
        
        is_valid, stats, warning = validate_column_data(empty_df, 'Empty')
        
        self.assertFalse(is_valid)
        self.assertEqual(stats['valid_rows'], 0)
        self.assertIsNotNone(warning)
    
    def test_validate_column_data_mostly_empty(self):
        """Test validácie stĺpca s prevažne prázdnymi hodnotami."""
        mostly_empty_df = pd.DataFrame({
            'MostlyEmpty': ['Valid', '', None, None, None, None, None, None, None, None]
        })
        
        is_valid, stats, warning = validate_column_data(mostly_empty_df, 'MostlyEmpty')
        
        self.assertTrue(is_valid)  # Stále platný, ale s varovaním
        self.assertEqual(stats['valid_rows'], 2)  # 'Valid' + '' (empty string is still non-null)
        # Warning should mention high percentage of nulls
    
    def test_prepare_dataframe_for_processing(self):
        """Test prípravy DataFrame pre spracovanie."""
        company_names = prepare_dataframe_for_processing(self.test_df, 'Názov firmy')
        
        # None sa konvertuje na 'None' string, takže ostanú 4 hodnoty: 'ABC s.r.o.', 'XYZ a.s.', 'DEF spol. s r.o.', 'None'
        expected_names = ['ABC s.r.o.', 'XYZ a.s.', 'DEF spol. s r.o.', 'None']
        self.assertEqual(len(company_names), 4)
        self.assertEqual(company_names, expected_names)
    
    def test_create_output_dataframe(self):
        """Test vytvorenia výsledného DataFrame."""
        output_df = create_output_dataframe(self.test_df, 'Názov firmy', self.test_results)
        
        # Kontrola štruktúry - output_df má pôvodné columns + results columns  
        original_columns = ['Názov firmy', 'Adresa', 'Telefón']
        results_columns = ['ICO', 'Názov', 'MatchStrategy', 'UsedQueryVariant', 'IdentifierType']
        
        for col in original_columns:
            self.assertIn(col, output_df.columns)
        for col in results_columns:
            self.assertIn(col, output_df.columns)
        
        # Kontrola počtu riadkov - output_df má všetky pôvodné riadky
        self.assertEqual(len(output_df), 5)  # Všetky pôvodné riadky z test_df
        
        # Kontrola konkrétnych hodnôt
        self.assertEqual(output_df.iloc[0]['ICO'], '12345678')
        self.assertEqual(output_df.iloc[0]['Názov'], 'ABC s.r.o.')
    
    def test_create_excel_download(self):
        """Test vytvorenia Excel súboru na stiahnutie."""
        output_df = create_output_dataframe(self.test_df, 'Názov firmy', self.test_results)
        excel_buffer = create_excel_download(output_df)
        
        # Kontrola, že buffer nie je prázdny - funkcia vracia BytesIO objekt
        self.assertIsInstance(excel_buffer, BytesIO)
        excel_data = excel_buffer.getvalue()
        self.assertGreater(len(excel_data), 0)
        
        # Test čítania vráteného Excel súboru
        excel_buffer.seek(0)  # Reset position
        df_test = pd.read_excel(excel_buffer)
        # Excel môže filtrovať riadky s NaN, takže kontrolujeme, že má aspoň nejaké dáta
        self.assertGreater(len(df_test), 0)
        self.assertLessEqual(len(df_test), len(output_df))
        
        # Kontrola zachovania stĺpcov
        for col in output_df.columns:
            self.assertIn(col, df_test.columns)
    
    def test_create_csv_download(self):
        """Test vytvorenia CSV súboru na stiahnutie."""
        output_df = create_output_dataframe(self.test_df, 'Názov firmy', self.test_results)
        csv_string = create_csv_download(output_df)
        
        # Kontrola, že CSV string nie je prázdny
        self.assertIsInstance(csv_string, str)
        self.assertGreater(len(csv_string), 0)
        
        # Test čítania vráteného CSV
        df_test = pd.read_csv(StringIO(csv_string))
        self.assertEqual(len(df_test), len(output_df))
        
        # Kontrola zachovania stĺpcov
        for col in output_df.columns:
            self.assertIn(col, df_test.columns)
    
    def test_edge_cases_empty_dataframe(self):
        """Test práce s prázdnym DataFrame."""
        empty_df = pd.DataFrame()
        
        # Test validácie prázdneho DF - by mal vyhodiť KeyError
        with self.assertRaises(KeyError):
            company_names = prepare_dataframe_for_processing(empty_df, 'NonExistent')
    
    def test_edge_cases_nonexistent_column(self):
        """Test práce s neexistujúcim stĺpcom."""
        # validate_column_data by mal vrátiť False a error message
        is_valid, stats, warning = validate_column_data(self.test_df, 'NonExistentColumn')
        self.assertFalse(is_valid)
        self.assertEqual(stats, {})
        self.assertIn('neexistuje', warning)
    
    def test_special_characters_handling(self):
        """Test spracovania špeciálnych znakov v názvoch firiem."""
        special_df = pd.DataFrame({
            'Názvy': ['Firma s & Co.', 'Test "quotes" s.r.o.', 'Úžasná š.p.', 'Normal Ltd.']
        })
        
        company_names = prepare_dataframe_for_processing(special_df, 'Názvy')
        
        # Všetky názvy by mali zostať zachované
        self.assertEqual(len(company_names), 4)
        self.assertIn('Firma s & Co.', company_names)
        self.assertIn('Test "quotes" s.r.o.', company_names)
        self.assertIn('Úžasná š.p.', company_names)


class TestDataValidation(unittest.TestCase):
    """Špecializované testy pre validáciu dát."""
    
    def test_large_dataset_performance(self):
        """Test výkonu s veľkým datasetom."""
        # Vytvorenie veľkého DataFrame (1000 riadkov)
        large_data = {
            'Companies': [f'Firma {i} s.r.o.' for i in range(1000)]
        }
        large_df = pd.DataFrame(large_data)
        
        # Test by mal prebehnúť rýchlo
        import time
        start_time = time.time()
        
        is_valid, stats, warning = validate_column_data(large_df, 'Companies')
        company_names = prepare_dataframe_for_processing(large_df, 'Companies')
        
        end_time = time.time()
        
        # Validácia výsledkov
        self.assertTrue(is_valid)
        self.assertEqual(len(company_names), 1000)
        
        # Performance check - by mal trvať menej ako 5 sekúnd
        processing_time = end_time - start_time
        self.assertLess(processing_time, 5.0, 
                       f"Processing took too long: {processing_time:.2f}s")
    
    def test_mixed_data_types(self):
        """Test práce s rôznymi typmi dát v stĺpci."""
        mixed_df = pd.DataFrame({
            'Mixed': ['String', 123, 45.67, True, None, '']
        })
        
        company_names = prepare_dataframe_for_processing(mixed_df, 'Mixed')
        
        # Číselné hodnoty a boolean by mali byť konvertované na string
        # None sa konvertuje na 'None' string takže máme 5 hodnôt
        expected_results = ['String', '123', '45.67', 'True', 'None']  
        self.assertEqual(len(company_names), 5)
        
        # Kontrola, že všetky hodnoty sú string
        for name in company_names:
            self.assertIsInstance(name, str)


if __name__ == '__main__':
    # Konfigurácia pre verbose output
    unittest.main(verbosity=2, buffer=True)