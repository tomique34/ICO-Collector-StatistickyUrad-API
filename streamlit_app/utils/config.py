#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Konfigurácia pre ICO Collector Streamlit App
"""

import os

# ====== API Konfigurácia ======
RPO_BASE_URL = "https://api.statistics.sk/rpo/v1/search"
ONLY_ACTIVE = True

# ====== Performance Nastavenia ======
MAX_WORKERS = 6
MAX_REQ_PER_MIN = 60
REQUEST_TIMEOUT = 12
RETRY_COUNT = 3
RETRY_SLEEP_BASE = 0.7
BATCH_SIZE = 60

# ====== Default Hodnoty ======
DEFAULT_COLUMN_NAME = "Firma"
DEFAULT_SHEET_NAME = None

# ====== File Upload Limity ======
MAX_FILE_SIZE_MB = 200
ALLOWED_FILE_TYPES = ['.xlsx', '.xls']

# ====== Streamlit Konfigurácia ======
PAGE_TITLE = "ICO Collector - Získavanie IČO firiem"
PAGE_ICON = "🔍"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# ====== Vizualizácia ======
CHART_COLORS = {
    'success': '#28a745',
    'error': '#dc3545', 
    'warning': '#ffc107',
    'info': '#17a2b8',
    'primary': '#007bff'
}

# ====== Environment Variables ======
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# ====== Deployment Settings ======
STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', 8501))
STREAMLIT_SERVER_ADDRESS = os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost')