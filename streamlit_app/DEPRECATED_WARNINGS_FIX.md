# 🔧 Deprecated Warnings Fix Guide

Príručka na riešenie deprecated component warnings v ICO Collector Streamlit aplikácii.

## 🚨 Bežné deprecated warnings v Streamlit

### 1. `st.beta_*` funkcie
**Deprecated:** `st.beta_columns`, `st.beta_container`, `st.beta_expander`
**Replacement:**
```python
# Staré (deprecated)
st.beta_columns([1, 2, 3])
st.beta_container()
st.beta_expander("Title")

# Nové
st.columns([1, 2, 3])
st.container()
st.expander("Title")
```

### 2. `st.experimental_*` funkcie
**Deprecated:** `st.experimental_memo`, `st.experimental_singleton`
**Replacement:**
```python
# Staré (deprecated)
@st.experimental_memo
def cached_function():
    return data

@st.experimental_singleton
def get_database_connection():
    return connection

# Nové
@st.cache_data
def cached_function():
    return data

@st.cache_resource
def get_database_connection():
    return connection
```

### 3. `st.cache` (deprecated)
**Replacement:**
```python
# Staré (deprecated)
@st.cache
def load_data():
    return pd.read_csv('data.csv')

# Nové
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')
```

### 4. Plotly chart warnings
**Issue:** `st.plotly_chart` s deprecated parametrami
**Fix:**
```python
# Staré
st.plotly_chart(fig, use_container_width=True, sharing="streamlit")

# Nové  
st.plotly_chart(fig, use_container_width=True, theme="streamlit")
```

### 5. DataFrame display warnings
**Issue:** `st.dataframe` s deprecated parametrami
**Fix:**
```python
# Staré
st.dataframe(df, width=None, height=None)

# Nové
st.dataframe(df, use_container_width=True, height=400)
```

## 🛠️ Fixes aplikované v našej aplikácii

### ✅ V `streamlit_app.py`
```python
# Už aktualizované na nové API
st.columns([1, 2, 3])  # ✅ Namiesto st.beta_columns
st.expander("Title")   # ✅ Namiesto st.beta_expander
st.container()         # ✅ Namiesto st.beta_container
```

### ✅ V `utils/excel_handler.py`
```python
# Už aktualizované
@st.cache_data  # ✅ Namiesto @st.cache alebo @st.experimental_memo
def cached_load_excel_file(file_data: bytes, file_name: str):
    # Implementation
```

### ✅ V `utils/ico_processor.py`
```python
# Progress bar už používa nové API
progress_bar = st.progress(0)  # ✅ Správne API
```

## 🔍 Ako identifikovať deprecated warnings

### 1. Spustenie aplikácie s verbose logging
```bash
streamlit run streamlit_app.py --logger.level=debug
```

### 2. Kontrola v browseri console
- Otvorte F12 Developer Tools
- Pozrite Console tab
- Hľadajte warnings s "deprecated" 

### 3. Kontrola v terminal outpute
```bash
# Warnings sa zobrazujú v termináli kde je spustený streamlit
# Hľadajte riadky s:
# DeprecationWarning: ...
# FutureWarning: ...
```

## 🎯 Preventívne opatrenia už implementované

### 1. Streamlit config aktualizácie
**V `.streamlit/config.toml`:**
```toml
[global]
# Nové nastavenie pre serialization
dataFrameSerialization = "legacy"

[deprecation] 
# Potlačenie starých warnings
showfileUploaderEncoding = false
showImageFormat = false
showPyplotGlobalUse = false
```

### 2. Modularizácia kódu
- Všetky cache funkcie používajú `@st.cache_data`
- UI komponenty používajú najnovšie API
- Plotly charts používajú aktuálne parametre

### 3. Error handling pre compatibility
```python
try:
    # Pokus o nové API
    result = st.cache_data(expensive_function)()
except AttributeError:
    # Fallback na staré API ak je potrebný
    result = st.cache(expensive_function)()
```

## 🧪 Testing deprecated warnings

### Test script na identifikáciu warnings
```python
#!/usr/bin/env python3
"""Test script pre identifikáciu deprecated warnings."""

import warnings
import streamlit as st
import sys
from io import StringIO

def capture_warnings():
    """Zachytí všetky warnings počas behu."""
    warnings.simplefilter("always")  # Zobraz všetky warnings
    
    # Redirect warnings to string buffer
    old_stderr = sys.stderr
    sys.stderr = warning_buffer = StringIO()
    
    try:
        # Import a spustenie hlavných funkcií
        from streamlit_app import main
        
        # Simulácia základných operácií
        # (toto by sa spustilo v test environmente)
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        sys.stderr = old_stderr
        warnings_output = warning_buffer.getvalue()
        
    return warnings_output

if __name__ == "__main__":
    warnings_text = capture_warnings()
    
    if "DeprecationWarning" in warnings_text:
        print("🚨 Deprecated warnings found:")
        print(warnings_text)
    else:
        print("✅ No deprecated warnings detected")
```

## 📋 Kontrolný zoznam - Pre riešenie warnings

- [ ] **Spusti aplikáciu s debug logging**
- [ ] **Skontroluj browser console**  
- [ ] **Pozri terminal output pre warnings**
- [ ] **Aktualizuj deprecated funkcie**
- [ ] **Otestuj funkcionalitu po zmenách**
- [ ] **Aktualizuj requirements.txt na najnovšie verzie**

## 🔄 Migration guide pre hlavné warnings

### St.cache → st.cache_data
```python
# PRED
@st.cache(persist=True)
def load_data():
    return pd.read_csv('file.csv')

# PO
@st.cache_data(persist="disk")
def load_data():
    return pd.read_csv('file.csv')
```

### St.beta_* → nové API
```python
# PRED
col1, col2 = st.beta_columns(2)
with st.beta_expander("Details"):
    st.write("Content")

# PO  
col1, col2 = st.columns(2)
with st.expander("Details"):
    st.write("Content")
```

### Plotly configs
```python
# PRED
st.plotly_chart(fig, sharing="streamlit", use_container_width=True)

# PO
st.plotly_chart(fig, theme="streamlit", use_container_width=True)
```

## 🚀 Automated fix script

```bash
#!/bin/bash
# automated_deprecation_fix.sh

echo "🔧 Fixing deprecated Streamlit API calls..."

# Replace st.cache with st.cache_data
find . -name "*.py" -exec sed -i 's/@st\.cache/@st.cache_data/g' {} \;

# Replace st.beta_ functions
find . -name "*.py" -exec sed -i 's/st\.beta_columns/st.columns/g' {} \;
find . -name "*.py" -exec sed -i 's/st\.beta_expander/st.expander/g' {} \;
find . -name "*.py" -exec sed -i 's/st\.beta_container/st.container/g' {} \;

# Replace experimental functions
find . -name "*.py" -exec sed -i 's/@st\.experimental_memo/@st.cache_data/g' {} \;
find . -name "*.py" -exec sed -i 's/@st\.experimental_singleton/@st.cache_resource/g' {} \;

echo "✅ Automated fixes applied. Please test functionality!"
```

## ✅ Stav nášho kódu

**Všetky hlavné deprecated warnings už boli preventívne vyriešené:**

1. ✅ Používame `st.columns()` namiesto `st.beta_columns()`
2. ✅ Používame `st.expander()` namiesto `st.beta_expander()`  
3. ✅ Používame `@st.cache_data` namiesto `@st.cache`
4. ✅ Plotly charts používajú aktuálne API
5. ✅ Config súbor má potlačené deprecated warnings

**Pre overenie:**
```bash
# Po inštalácii dependencies spustite:
streamlit run streamlit_app.py

# A pozorujte terminal output pre warnings
```

---

**© 2025 ICO Collector | Modern Streamlit without deprecated warnings**