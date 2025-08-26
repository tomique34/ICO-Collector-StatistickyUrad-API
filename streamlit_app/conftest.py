"""
Pytest konfiguračný súbor pre ICO Collector Streamlit aplikáciu.
Obsahuje fixtures a setup pre jednotlivé testy.
"""

import pytest
import pandas as pd
from io import BytesIO
import tempfile
import os
from unittest.mock import MagicMock


@pytest.fixture
def sample_dataframe():
    """Fixture pre testovací DataFrame s firmami."""
    return pd.DataFrame({
        'Názov firmy': [
            'ABC Software s.r.o.',
            'XYZ Trading a.s.',
            'DEF Manufacturing spol. s r.o.',
            '',  # Prázdny riadok
            None,  # None hodnota
            'GHI Services š.p.'
        ],
        'Adresa': [
            'Bratislava',
            'Košice', 
            'Žilina',
            'Prešov',
            'Nitra',
            'Trenčín'
        ],
        'Telefón': [
            '+421 2 1234567',
            '+421 55 7654321',
            '',
            '+421 51 1111111',
            None,
            '+421 32 2222222'
        ]
    })


@pytest.fixture
def sample_excel_file(sample_dataframe):
    """Fixture pre testovací Excel súbor."""
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        sample_dataframe.to_excel(writer, sheet_name='Firmy', index=False)
        # Pridanie druhého harku
        sample_dataframe.head(3).to_excel(writer, sheet_name='Top3', index=False)
    excel_buffer.seek(0)
    return excel_buffer


@pytest.fixture
def sample_processing_results():
    """Fixture pre výsledky spracovania."""
    return {
        'ICO': ['12345678', '', '87654321', '', None, '11223344'],
        'Názov': [
            'ABC Software s.r.o.',
            '',
            'DEF Manufacturing spol. s r.o.',
            '',
            '',
            'GHI Services š.p.'
        ],
        'Adresa': [
            'Bratislava 1, 81101 Bratislava',
            '',
            'Žilina 2, 01001 Žilina',
            '',
            '',
            'Trenčín 3, 91101 Trenčín'
        ],
        'MatchStrategy': ['exact', '', 'fuzzy', '', '', 'variant'],
        'UsedQueryVariant': [
            'ABC Software s.r.o.',
            '',
            'DEF Manufacturing',
            '',
            '',
            'GHI Services'
        ],
        'IdentifierType': ['ico', '', 'ico', '', '', 'ico']
    }


@pytest.fixture
def mock_api_response():
    """Fixture pre mock API odpoveď."""
    return {
        "resultCount": 1,
        "results": [{
            "ico": "12345678",
            "nazov": "Testovacia firma s.r.o.",
            "adresa": {
                "ulica": "Testovacia ulica 123",
                "obec": "Bratislava", 
                "psc": "81101"
            },
            "pravnaForma": "112",
            "datumVzniku": "2020-01-01",
            "datumZanik": None
        }]
    }


@pytest.fixture
def mock_empty_api_response():
    """Fixture pre prázdnu API odpoveď."""
    return {
        "resultCount": 0,
        "results": []
    }


@pytest.fixture
def mock_streamlit_session():
    """Fixture pre mock Streamlit session state."""
    session_state = {}
    return session_state


@pytest.fixture
def temp_excel_file(sample_dataframe):
    """Fixture pre dočasný Excel súbor na disku."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
            sample_dataframe.to_excel(writer, sheet_name='TestSheet', index=False)
        
        yield temp_file.name
        
        # Cleanup
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


@pytest.fixture
def invalid_file_content():
    """Fixture pre neplatný súbor."""
    return BytesIO(b'This is not a valid Excel file content')


@pytest.fixture(scope="session")
def test_config():
    """Session-wide konfigurácia pre testy."""
    return {
        'api_base_url': 'https://data.statistics.sk/api',
        'max_retries': 3,
        'timeout': 30,
        'test_mode': True
    }


class MockICOProcessor:
    """Mock trieda pre ICOProcessor na testovanie."""
    
    def __init__(self):
        self.stats = {
            'total_companies': 0,
            'processed_companies': 0,
            'successful_matches': 0,
            'failed_searches': 0,
            'is_processing': False
        }
    
    def reset_stats(self):
        """Reset štatistík."""
        self.stats = {
            'total_companies': 0,
            'processed_companies': 0,
            'successful_matches': 0,
            'failed_searches': 0,
            'is_processing': False
        }
    
    def get_processing_statistics(self):
        """Vráti štatistiky spracovania."""
        stats = self.stats.copy()
        if stats['processed_companies'] > 0:
            stats['success_rate'] = (stats['successful_matches'] / stats['processed_companies']) * 100
        else:
            stats['success_rate'] = 0.0
        return stats
    
    def process_companies_with_progress(self, companies):
        """Mock spracovania firiem."""
        self.stats['total_companies'] = len(companies)
        self.stats['is_processing'] = True
        
        results = {
            'ICO': [],
            'Názov': [],
            'Adresa': [],
            'MatchStrategy': [],
            'UsedQueryVariant': [],
            'IdentifierType': []
        }
        
        for i, company in enumerate(companies):
            # Mock: každá druhá firma je úspešne nájdená
            if i % 2 == 0 and company.strip():
                results['ICO'].append(f"{12345678 + i}")
                results['Názov'].append(company)
                results['Adresa'].append(f"Test adresa {i}")
                results['MatchStrategy'].append('exact')
                results['UsedQueryVariant'].append(company)
                results['IdentifierType'].append('ico')
                self.stats['successful_matches'] += 1
            else:
                results['ICO'].append('')
                results['Názov'].append('')
                results['Adresa'].append('')
                results['MatchStrategy'].append('')
                results['UsedQueryVariant'].append('')
                results['IdentifierType'].append('')
            
            self.stats['processed_companies'] += 1
        
        self.stats['failed_searches'] = self.stats['processed_companies'] - self.stats['successful_matches']
        self.stats['is_processing'] = False
        
        return results


@pytest.fixture
def mock_ico_processor():
    """Fixture pre mock ICOProcessor."""
    return MockICOProcessor()


# Pytest hooks
def pytest_configure(config):
    """Konfigurácia pytest na začiatku behu testov."""
    # Registrácia custom markerov
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as requiring API access"
    )


def pytest_collection_modifyitems(config, items):
    """Modifikácia testovania pred spustením."""
    # Automatické pridanie markera pre slow testy
    for item in items:
        # Označenie integračných testov ako pomalé
        if "integration" in item.keywords:
            item.add_marker(pytest.mark.slow)
        
        # Označenie API testov
        if "api" in item.keywords:
            item.add_marker(pytest.mark.api)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Automatické nastavenie testovacieho prostredia."""
    # Setup pred testom
    os.environ['TESTING'] = '1'
    os.environ['LOG_LEVEL'] = 'ERROR'  # Potlačenie logov počas testov
    
    yield
    
    # Cleanup po teste
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
    if 'LOG_LEVEL' in os.environ:
        del os.environ['LOG_LEVEL']