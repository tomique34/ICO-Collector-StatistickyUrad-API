# 🧪 Testing Guide pre ICO Collector Streamlit App

Kompletný prehľad testovania pre ICO Collector Streamlit aplikáciu.

## 📋 Prehľad testov

### 🎯 Test štruktúra
```
tests/
├── __init__.py                 # Tests package
├── README_TESTING.md          # Tento súbor
├── conftest.py               # Pytest fixtures a konfigurácia
├── test_streamlit_app.py     # Hlavné testy aplikácie
├── test_ico_processor.py     # Testy ICO processing logiky
├── test_components.py        # Testy UI komponentov
```

### 🔧 Test konfigurácia
- **pytest.ini** - Základná pytest konfigurácia
- **conftest.py** - Fixtures a test setup
- **requirements_test.txt** - Test dependencies

## 🚀 Spustenie testov

### Možnosť 1: Bez dependencies (základné testy)
```bash
# Spustenie custom test runnera
python3 run_tests.py
```
**Čo sa testuje:**
- ✅ Syntax kontrola všetkých Python súborov
- ✅ Existencia kľúčových súborov a adresárov
- ✅ Základná štruktúra aplikácie
- ✅ Konfiguračné súbory

### Možnosť 2: S inštalovanými dependencies
```bash
# Inštalácia dependencies
pip install -r requirements_streamlit.txt
pip install -r requirements_test.txt

# Spustenie pytest
pytest tests/ -v

# Alebo unittest
python -m unittest discover tests -v

# Alebo náš custom runner (s pokročilými testami)
python3 run_tests.py
```

### Možnosť 3: Špecifické test kategórie
```bash
# Iba unit testy
pytest -m unit

# Iba slow testy
pytest -m slow

# Bez slow testov
pytest -m "not slow"

# S coverage reportom
pytest --cov=. --cov-report=html
```

## 📊 Test kategórie

### 🔹 Unit Tests (`test_streamlit_app.py`)
**Čo testujú:**
- Validácia Excel súborov
- Spracovanie dát v DataFrame
- Generovanie výsledných súborov
- Error handling pre edge cases
- Performance s veľkými datasetmi

**Príklady testov:**
```python
def test_validate_excel_file_success()
def test_validate_column_data_valid()
def test_prepare_dataframe_for_processing()
def test_create_excel_download()
```

### 🔹 ICO Processor Tests (`test_ico_processor.py`)
**Čo testujú:**
- API integrácia (mocked)
- Normalizácia názvov firiem
- Rate limiting
- Retry mechanizmy
- Batch processing
- Session state management

**Príklady testov:**
```python
def test_search_company_success()
def test_normalize_company_name()
def test_process_companies_with_progress()
def test_rate_limiting()
```

### 🔹 Component Tests (`test_components.py`)
**Čo testujú:**
- UI komponenty (ak sú dostupné)
- Streamlit session state
- File upload validácia
- Progress display
- Results dashboard

## 🧩 Test Fixtures (conftest.py)

### 📄 Dátové fixtures
- `sample_dataframe` - Test DataFrame s firmami
- `sample_excel_file` - Mock Excel súbor
- `sample_processing_results` - Mock výsledky
- `mock_api_response` - Mock API odpoveď

### 🔧 Utility fixtures
- `mock_streamlit_session` - Mock session state
- `temp_excel_file` - Dočasný Excel súbor na disku
- `mock_ico_processor` - Mock ICOProcessor trieda

### Príklad použitia:
```python
def test_with_sample_data(sample_dataframe, sample_processing_results):
    # Test s predpripraveným DataFrame
    assert len(sample_dataframe) == 6
    assert 'ICO' in sample_processing_results
```

## ⚙️ Konfigurácia testov

### pytest.ini nastavenia
```ini
[tool:pytest]
testpaths = tests
addopts = --verbose --tb=short --color=yes
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests that require API access
```

### Markery pre testy
```python
@pytest.mark.slow
def test_large_dataset():
    # Pomalý test
    
@pytest.mark.api
def test_real_api_call():
    # Test vyžadujúci API prístup

@pytest.mark.integration
def test_full_workflow():
    # Integračný test
```

## 📈 Test Reports

### HTML Coverage Report
```bash
pytest --cov=. --cov-report=html
# Otvorí htmlcov/index.html
```

### Console Output
```bash
pytest tests/ -v --tb=short
```

### JUnit XML (pre CI/CD)
```bash
pytest --junitxml=test-results.xml
```

## 🔍 Debugging testov

### Verbose output
```bash
pytest -v -s tests/test_streamlit_app.py::TestStreamlitApp::test_validate_excel_file_success
```

### Print debugging
```python
def test_debug():
    result = some_function()
    print(f"Debug: result = {result}")  # Zobrazí sa s -s flag
    assert result is not None
```

### PDB debugging
```bash
pytest --pdb  # Vstúpi do debuggera pri prvej chybe
pytest --pdb-trace  # Vstúpi do debuggera na začiatku každého testu
```

## 🛠️ Custom Test Runner (run_tests.py)

Náš custom test runner poskytuje:

### Fázy testovania
1. **Syntax Check** - Kontrola Python syntax
2. **Import Check** - Kontrola dostupnosti modulov  
3. **Basic Functional Tests** - Základné testy bez dependencies
4. **Advanced Tests** - Pokročilé testy (ak sú dostupné dependencies)

### Výhody
- ✅ Funguje aj bez nainštalovaných dependencies
- ✅ Postupné testovanie s jasným feedbackom
- ✅ Automatická detekcia dostupných modulov
- ✅ User-friendly output s emoji a farbami

### Príklad výstupu
```
🧪 ICO Collector Streamlit App - Test Runner
==================================================
🔍 Kontrola syntax Python súborov...
  ✅ streamlit_app.py - syntax OK
  ✅ utils/ico_processor.py - syntax OK

📦 Kontrola dostupnosti modulov...
  ✅ streamlit - dostupný
  ✅ pandas - dostupný

🧪 Spúšťam základné funkčné testy...
✅ Všetky testy prešli úspešne!
```

## 🔧 Troubleshooting

### Časté problémy

**1. ModuleNotFoundError**
```bash
# Riešenie: Inštalácia dependencies
pip install -r requirements_streamlit.txt
```

**2. Syntax chyby**
```bash
# Kontrola syntax
python3 -m py_compile streamlit_app.py
```

**3. Import chyby**
```python
# Pridanie path pre testy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**4. Streamlit session state chyby**
```python
# Mock session state v testoch
@patch('streamlit.session_state', new_callable=dict)
def test_with_session_state(mock_session):
    mock_session['key'] = 'value'
```

### Performance Issues
- Použite `@st.cache_data` pre cache-ovanie
- Limitujte počet test dát
- Používajte mock objekty namiesto reálnych API volaní

## 📚 Najlepšie praktiky

### Test Writing
1. **Descriptive names** - názvy testov jasne popisujú čo testujú
2. **AAA Pattern** - Arrange, Act, Assert
3. **One assertion per test** - jeden test = jeden koncept
4. **Use fixtures** - znižujú duplikáciu kódu
5. **Mock external dependencies** - testy musia byť izolovateľné

### Test Organization
- Grupujte súvisiace testy do tried
- Používajte setup/teardown metódy pre prípravu
- Separujte unit, integration a end-to-end testy

### CI/CD Integration
```yaml
# Príklad GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements_test.txt
    pytest tests/ --junitxml=test-results.xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v1
```

## 📞 Podpora

Pri problémoch s testovaním:

1. **Skontrolujte syntax** pomocou `python3 run_tests.py`
2. **Overte dependencies** v requirements_streamlit.txt
3. **Spustite debug mode** s `pytest -v -s`
4. **Skontrolujte logs** v test output

---

**© 2025 ICO Collector Testing Suite | Comprehensive testing for reliable code**