# 🚀 Setup Instructions pre ICO Collector Streamlit App

## ⚠️ Dôležité - Externally Managed Python Environment

Váš systém používa externally managed Python environment (macOS s Homebrew). Pre bezpečnú inštaláciu dependencies potrebujete vytvoriť virtual environment.

## 🔧 Rýchla inštalácia

### Možnosť 1: Virtual Environment (Odporúčané)
```bash
# 1. Vytvorenie virtual environment
python3 -m venv ico_collector_env

# 2. Aktivácia virtual environment
source ico_collector_env/bin/activate

# 3. Inštalácia dependencies
pip install -r requirements_streamlit.txt

# 4. Spustenie aplikácie
streamlit run streamlit_app.py

# 5. Deaktivácia (keď skončíte)
deactivate
```

### Možnosť 2: User Install (Menej bezpečné)
```bash
# Inštalácia do user directory
pip install --user -r requirements_streamlit.txt

# Spustenie aplikácie
streamlit run streamlit_app.py
```

### Možnosť 3: System-wide Install (Nie je odporúčané)
```bash
# Iba ak viete čo robíte!
pip install --break-system-packages -r requirements_streamlit.txt
streamlit run streamlit_app.py
```

### Možnosť 4: pipx (Pre aplikácie)
```bash
# Inštalácia pipx ak ho nemáte
brew install pipx

# Inštalácia streamlit cez pipx
pipx install streamlit
# Potom inštalujte ostatné dependencies manuálne do virtual env
```

## 📋 Čo sa nainštaluje

Z `requirements_streamlit.txt`:
- **streamlit>=1.30.0** - Web framework
- **pandas>=2.0.0** - Data processing  
- **openpyxl>=3.1.0** - Excel file handling
- **requests>=2.31.0** - HTTP requests
- **plotly>=5.15.0** - Interactive visualizations
- **altair>=5.0.0** - Alternative charts
- **tqdm>=4.65.0** - Progress bars
- **numpy>=1.24.0** - Numerical computing
- **python-dateutil>=2.8.0** - Date utilities
- **pytz>=2023.1** - Timezone handling

## 🛠️ Riešenie problémov

### Problem: "No module named 'plotly'"
```bash
# V aktivovanom virtual environment:
pip install plotly>=5.15.0
```

### Problem: "No module named 'pandas'"
```bash
# V aktivovanom virtual environment:
pip install pandas>=2.0.0
```

### Problem: Config warnings
✅ **Vyriešené!** - Aktualizovaný `.streamlit/config.toml` bez deprecated nastavení.

### Problem: "Static folder not found"
✅ **Vyriešené!** - `enableStaticServing` je nastavené na `false`.

## 🎯 Overenie inštalácie

Po inštalácii spustite test:
```bash
# Aktivujte virtual environment
source ico_collector_env/bin/activate

# Test dependencies
python3 -c "
import streamlit
import pandas
import plotly
import requests
import openpyxl
print('✅ Všetky dependencies sú dostupné!')
"

# Syntax check aplikácie  
python3 -m py_compile streamlit_app.py
echo "✅ Syntax check OK"

# Test runner
python3 run_tests.py
```

## 🚀 Spustenie aplikácie

```bash
# 1. Aktivujte virtual environment
source ico_collector_env/bin/activate

# 2. Spustite aplikáciu
streamlit run streamlit_app.py

# 3. Otvorte browser na:
# http://localhost:8501
```

## 📊 Prvé spustenie

Po úspešnom spustení by ste mali vidieť:
```
You can now view your Streamlit app in your browser.
URL: http://localhost:8501
```

**Bez warning správ o deprecated config options!**

## 🔄 Pre vývoj

Ak budete meniť kód:

```bash
# Aktivácia dev environment
source ico_collector_env/bin/activate

# Inštalácia test dependencies
pip install -r requirements_test.txt

# Spustenie testov
pytest tests/ -v

# Syntax check
python3 run_tests.py
```

## 🐳 Docker alternatíva

Ak nechcete riešiť Python dependencies:

```bash
# Build Docker image
docker build -t ico-collector .

# Run container
docker run -p 8501:8501 ico-collector

# Otvorte http://localhost:8501
```

## 💡 Tipy

1. **Vždy používajte virtual environment** pre Python projekty
2. **Aktivujte environment** pred každým použitím aplikácie
3. **Aktualizujte dependencies** pravidelne: `pip install -r requirements_streamlit.txt --upgrade`
4. **Spustite testy** po zmenách: `python3 run_tests.py`

## 📞 Podpora

Pri problémech:
1. Skontrolujte, že máte aktivovaný virtual environment
2. Overte inštaláciu dependencies: `pip list`
3. Spustite syntax check: `python3 -m py_compile streamlit_app.py`
4. Pozrite sa na error log vo výstupe `streamlit run`

---

**© 2025 ICO Collector | Clean setup without system conflicts**