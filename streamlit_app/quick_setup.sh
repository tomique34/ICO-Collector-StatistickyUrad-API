#!/bin/bash
# Quick setup script pre ICO Collector Streamlit aplikáciu

set -e  # Exit on any error

echo "🚀 ICO Collector - Quick Setup"
echo "================================"

# Kontrola, či sme v správnom adresári
if [[ ! -f "streamlit_app.py" ]]; then
    echo "❌ streamlit_app.py nenájdený. Spustite tento script v streamlit_app/ adresári."
    exit 1
fi

# Kontrola Python
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 nie je nainštalovaný."
    exit 1
fi

echo "✅ Python3 je dostupný: $(python3 --version)"

# Vytvorenie virtual environment
VENV_NAME="ico_collector_env"

if [[ -d "$VENV_NAME" ]]; then
    echo "📁 Virtual environment $VENV_NAME už existuje"
    read -p "❓ Chcete ho znovu vytvoriť? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️ Odstráňujem starý virtual environment..."
        rm -rf "$VENV_NAME"
    else
        echo "📦 Používam existujúci virtual environment"
    fi
fi

if [[ ! -d "$VENV_NAME" ]]; then
    echo "📦 Vytváram virtual environment: $VENV_NAME"
    python3 -m venv "$VENV_NAME"
fi

# Aktivácia virtual environment
echo "🔧 Aktivujem virtual environment..."
source "$VENV_NAME/bin/activate"

# Upgrade pip
echo "⬆️ Aktualizujem pip..."
pip install --upgrade pip

# Inštalácia dependencies
echo "📋 Inštalujem dependencies z requirements_streamlit.txt..."
if [[ -f "requirements_streamlit.txt" ]]; then
    pip install -r requirements_streamlit.txt
else
    echo "❌ requirements_streamlit.txt neexistuje!"
    exit 1
fi

# Overenie inštalácie
echo "🔍 Overujem inštaláciu..."

# Test dependencies
python3 -c "
try:
    import streamlit
    import pandas
    import plotly
    import requests
    import openpyxl
    print('✅ Všetky dependencies sú dostupné!')
except ImportError as e:
    print(f'❌ Chýba dependency: {e}')
    exit(1)
"

# Syntax check
echo "🔍 Kontrolujem syntax aplikácie..."
python3 -m py_compile streamlit_app.py
echo "✅ Syntax check OK"

# Spustenie testov
if [[ -f "run_clean_tests.py" ]]; then
    echo "🧪 Spúšťam clean test suite..."
    python3 run_clean_tests.py
elif [[ -f "run_tests.py" ]]; then
    echo "🧪 Spúšťam základné testy..."
    python3 run_tests.py
fi

echo ""
echo "🎉 Setup úspešne dokončený!"
echo "================================"
echo ""
echo "🚀 Pre spustenie aplikácie:"
echo "1️⃣ source $VENV_NAME/bin/activate"
echo "2️⃣ streamlit run streamlit_app.py"
echo ""
echo "🌐 Aplikácia bude dostupná na: http://localhost:8501"
echo ""
echo "📖 Pre viac informácií si prečítajte SETUP_INSTRUCTIONS.md"
echo ""

# Ponuka na automatické spustenie
read -p "❓ Chcete spustiť aplikáciu teraz? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "🚀 Spúšťam Streamlit aplikáciu..."
    echo "🌐 Otvorte http://localhost:8501 vo vašom browseri"
    echo "⏹️ Pre zastavenie stlačte Ctrl+C"
    echo ""
    streamlit run streamlit_app.py
fi