# ⚡ Quick Start Guide

Najrýchlejší spôsob ako spustiť ICO Collector Streamlit aplikáciu.

## 🚀 One-click setup (Automatický)

```bash
# Spustite automatický setup script
./quick_setup.sh
```

Script automaticky:
- ✅ Vytvorí virtual environment
- ✅ Nainštaluje všetky dependencies  
- ✅ Spustí testy
- ✅ Ponúkne spustenie aplikácie

## ⚡ Manuálny 3-step setup

```bash
# 1️⃣ Vytvorte virtual environment
python3 -m venv ico_collector_env
source ico_collector_env/bin/activate

# 2️⃣ Nainštalujte dependencies
pip install -r requirements_streamlit.txt

# 3️⃣ Spustite aplikáciu
streamlit run streamlit_app.py
```

## 🔧 Čo bolo opravené

### ✅ Config warnings VYRIEŠENÉ
```
Odstránené deprecated nastavenia z .streamlit/config.toml:
❌ global.dataFrameSerialization = "legacy"
❌ client.caching = true
❌ client.displayEnabled = true  
❌ runner.installTracer = false
❌ runner.fixMatplotlib = true
❌ deprecation.showfileUploaderEncoding = false
❌ deprecation.showImageFormat = false
❌ deprecation.showPyplotGlobalUse = false
```

### ✅ Import errors VYRIEŠENÉ
```python
# Graceful import handling s error messages:
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    st.error("❌ plotly nie je nainštalovaný. Spustite: pip install plotly>=5.15.0")
    st.stop()
```

### ✅ Static file warning VYRIEŠENÝ
```toml
[server]
enableStaticServing = false  # Vypnuté static serving
```

## 🎯 Po spustení

Aplikácia bude dostupná na: **http://localhost:8501**

**Očakávaný čistý output:**
```
You can now view your Streamlit app in your browser.
URL: http://localhost:8501
```

**BEZ warning správ!** 🎉

## 🛠️ Riešenie problémov

### "externally-managed-environment"
✅ **VYRIEŠENÉ** - používame virtual environment

### "No module named 'plotly'"  
✅ **VYRIEŠENÉ** - graceful error handling + install instructions

### Config deprecation warnings
✅ **VYRIEŠENÉ** - aktualizovaný config.toml

### "Static folder not found"
✅ **VYRIEŠENÉ** - enableStaticServing = false

## 📊 Test výsledky

Po opravách by mali všetky testy prechádzať:
```
🔍 Kontrola syntax Python súborov...
  ✅ streamlit_app.py - syntax OK
  ✅ utils/ico_processor.py - syntax OK  
  ✅ assets/localization.py - syntax OK

🎉 Všetky testy prešli úspešne!
```

---

**🎯 Cieľ dosiahnutý: Čistý startup bez warnings a errors!**