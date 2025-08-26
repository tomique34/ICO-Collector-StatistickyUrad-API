#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Slovenská lokalizácia pre ICO Collector Streamlit App
"""

# ====== Hlavné Texty ======
MAIN_TEXTS = {
    'app_title': '🔍 ICO Collector',
    'app_subtitle': 'Automatické získavanie IČO slovenských firiem',
    'page_title': 'ICO Collector - Získavanie IČO firiem',
    'sidebar_title': '⚙️ Nastavenia',
    'upload_title': '📤 Nahranie Excel súboru',
    'processing_title': '🔄 Spracovanie dát',
    'results_title': '📊 Výsledky a štatistiky',
    'download_title': '💾 Stiahnutie výsledkov'
}

# ====== Upload Sekcia ======
UPLOAD_TEXTS = {
    'file_uploader_label': 'Vyberte Excel súbor (.xlsx)',
    'file_uploader_help': 'Maximálna veľkosť súboru: 200 MB',
    'drag_drop_text': 'Pretiahnite súbor sem alebo kliknite pre výber',
    'supported_formats': 'Podporované formáty: .xlsx, .xls',
    'file_uploaded_success': '✅ Súbor úspešne nahraný',
    'file_too_large': '❌ Súbor je príliš veľký (max 200 MB)',
    'invalid_file_format': '❌ Neplatný formát súboru (očakáva sa .xlsx alebo .xls)',
    'upload_error': '❌ Chyba pri nahrávaní súboru'
}

# ====== Výber Harku a Stĺpca ======
SHEET_COLUMN_TEXTS = {
    'sheet_selection_title': '📋 Výber harku',
    'sheet_selection_label': 'Vyberte hark na spracovanie:',
    'available_sheets': 'Dostupné harky:',
    'sheet_preview_title': '👀 Náhľad vybraného harku',
    'column_selection_title': '📊 Výber stĺpca s firmami',
    'column_selection_label': 'Vyberte stĺpec obsahujúci názvy firiem:',
    'available_columns': 'Dostupné stĺpce:',
    'data_preview_title': '🔍 Náhľad dát',
    'no_data': 'Žiadne dáta na zobrazenie',
    'empty_sheet': 'Vybraný hark je prázdny',
    'sheet_error': 'Chyba pri načítaní harku'
}

# ====== Validácia Dát ======
VALIDATION_TEXTS = {
    'validation_title': '🛡️ Validácia dát',
    'total_rows': 'Celkový počet riadkov:',
    'valid_rows': 'Platné záznamy:',
    'empty_rows': 'Prázdne záznamy:',
    'validation_success': '✅ Validácia úspešná',
    'validation_warning': '⚠️ Upozornenie pri validácii',
    'validation_error': '❌ Chyba pri validácii',
    'no_valid_data': 'Vybraný stĺpec neobsahuje žiadne platné dáta',
    'mostly_empty': 'Vybraný stĺpec obsahuje veľa prázdnych hodnôt',
    'data_quality_good': 'Kvalita dát je dobrá',
    'proceed_question': 'Pokračovať so spracovaním?'
}

# ====== Spracovanie ======
PROCESSING_TEXTS = {
    'start_processing': '🚀 Spustiť spracovanie',
    'processing_in_progress': '⏳ Spracovanie prebíha...',
    'processing_complete': '✅ Spracovanie dokončené',
    'processing_failed': '❌ Spracovanie zlyhalo',
    'progress_title': '📈 Priebeh spracovávania',
    'current_progress': 'Aktuálny pokrok:',
    'processed_companies': 'Spracované firmy:',
    'found_icos': 'Nájdené IČO:',
    'processing_speed': 'Rýchlosť spracovania:',
    'estimated_time': 'Odhadovaný čas:',
    'companies_per_minute': 'firiem/min',
    'time_elapsed': 'Uplynulý čas:',
    'time_remaining': 'Zostávajúci čas:',
    'stop_processing': '⏹️ Zastaviť spracovanie'
}

# ====== Štatistiky a Výsledky ======
RESULTS_TEXTS = {
    'statistics_title': '📊 Štatistiky spracovania',
    'success_rate': 'Úspešnosť:',
    'total_processed': 'Celkovo spracované:',
    'successful_matches': 'Úspešné zhody:',
    'failed_searches': 'Neúspešné vyhľadávania:',
    'processing_time': 'Čas spracovania:',
    'avg_response_time': 'Priemerný čas odpovede:',
    'api_calls_made': 'API volania:',
    'data_quality_score': 'Kvalita výsledkov:',
    'export_options': '📥 Možnosti exportu',
    'download_excel': '📊 Stiahnuť Excel',
    'download_csv': '📋 Stiahnuť CSV',
    'results_summary': '📋 Súhrn výsledkov',
    'processing_insights': '💡 Prehľady a insights'
}

# ====== Chybové Hlášky ======
ERROR_MESSAGES = {
    'file_processing_error': 'Chyba pri spracovaní súboru',
    'api_connection_error': 'Chyba pripojenia k API',
    'invalid_data_format': 'Neplatný formát dát',
    'processing_interrupted': 'Spracovanie bolo prerušené',
    'insufficient_data': 'Nedostatok dát na spracovanie',
    'server_timeout': 'Časový limit servera vypršal',
    'unknown_error': 'Neznáma chyba',
    'try_again': 'Skúste to znova',
    'contact_support': 'Kontaktujte podporu',
    'check_connection': 'Skontrolujte internetové pripojenie'
}

# ====== Pomocné Texty ======
HELPER_TEXTS = {
    'tooltip_file_upload': 'Nahrajte Excel súbor obsahujúci zoznam firiem',
    'tooltip_sheet_selection': 'Vyberte hark, ktorý obsahuje údaje o firmách',
    'tooltip_column_selection': 'Vyberte stĺpec obsahujúci názvy firiem na spracovanie',
    'tooltip_processing': 'Spracovanie môže trvať niekoľko minút v závislosti od počtu firiem',
    'tooltip_results': 'Výsledky zobrazujú nájdené IČO a dodatočné informácie',
    'info_api_limits': 'API má limit 60 požiadaviek za minútu',
    'info_data_quality': 'Čistejšie dáta = lepšie výsledky vyhľadávania',
    'info_processing_time': 'Čas spracovania závisí od počtu firiem a kvality dát'
}

# ====== Menu a Navigácia ======
MENU_TEXTS = {
    'home': 'Domov',
    'upload': 'Nahranie',
    'processing': 'Spracovanie',
    'results': 'Výsledky',
    'help': 'Pomoc',
    'about': 'O aplikácii',
    'settings': 'Nastavenia'
}

# ====== Formátovanie ======
FORMAT_TEXTS = {
    'percentage': '%',
    'seconds': 's',
    'minutes': 'min',
    'hours': 'hod',
    'items': 'položiek',
    'of': 'z',
    'completed': 'dokončené',
    'in_progress': 'prebieha',
    'pending': 'čaká',
    'failed': 'zlyhalo'
}