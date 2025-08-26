#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ICO Collector - Streamlit Web Aplikácia
Moderná web aplikácia pre automatické získavanie IČO slovenských firiem
"""

import streamlit as st
from datetime import datetime
import time
from io import BytesIO

# Optional imports s error handling
try:
    import pandas as pd
except ImportError:
    st.error("❌ pandas nie je nainštalovaný. Spustite: pip install pandas>=2.0.0")
    st.stop()

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    st.error("❌ plotly nie je nainštalovaný. Spustite: pip install plotly>=5.15.0")
    st.stop()
    PLOTLY_AVAILABLE = False

# Import lokálnych modulov s error handling
try:
    from utils.config import *
except ImportError as e:
    st.error(f"❌ Chyba pri načítaní konfigurácie: {e}")
    st.stop()

try:
    from utils.excel_handler import *
except ImportError as e:
    st.error(f"❌ Chyba pri načítaní Excel handler: {e}")
    st.stop()

try:
    from utils.ico_processor import ICOProcessor
except ImportError as e:
    st.error(f"❌ Chyba pri načítaní ICO processor: {e}")
    st.stop()

try:
    from assets.localization import *
except ImportError as e:
    st.error(f"❌ Chyba pri načítaní lokalizácie: {e}")
    st.stop()

# ====== Konfigurácia stránky ======
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE,
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "ICO Collector - Automatické získavanie IČO slovenských firiem pomocou API Štatistického úradu SR"
    }
)

# ====== Hlavička aplikácie ======
def render_header():
    """Vykresli hlavičku aplikácie."""
    st.title(MAIN_TEXTS['app_title'])
    st.markdown(f"### {MAIN_TEXTS['app_subtitle']}")
    st.markdown("---")
    
    # Info box s prehľadom funkcionalít
    with st.expander("ℹ️ O aplikácii", expanded=False):
        st.markdown("""
        **ICO Collector** je moderná web aplikácia pre automatické získavanie 
        identifikačných čísiel organizácií (IČO) slovenských firiem pomocou 
        REST API Štatistického úradu SR.
        
        **Hlavné funkcie:**
        - 📤 Nahranie Excel súborov s firmami
        - 🔍 Automatické vyhľadávanie IČO cez RPO API
        - 📊 Real-time progress monitoring
        - 📈 Vizualizácie a štatistiky
        - 💾 Export výsledkov do Excel/CSV formátu
        - 🇸🇰 Plne v slovenskom jazyku
        """)

# ====== Sidebar s nastaveniami ======
def render_sidebar():
    """Vykresli sidebar s nastaveniami."""
    st.sidebar.title(MAIN_TEXTS['sidebar_title'])
    
    # Aktuálne nastavenia API
    with st.sidebar.expander("🔧 API Nastavenia"):
        st.write(f"**Max požiadaviek/min:** {MAX_REQ_PER_MIN}")
        st.write(f"**Timeout:** {REQUEST_TIMEOUT}s")
        st.write(f"**Retry pokusy:** {RETRY_COUNT}")
        st.write(f"**Batch veľkosť:** {BATCH_SIZE}")
        st.write(f"**Paralelné vlákna:** {MAX_WORKERS}")
    
    # Informácie o session state
    if st.session_state.get('processing_stats', {}).get('is_processing'):
        st.sidebar.warning("⚠️ Spracovanie prebieha...")
        if st.sidebar.button("🛑 Zastaviť spracovanie"):
            processor = ICOProcessor()
            processor.stop_processing()
            st.sidebar.success("✅ Spracovanie zastavené")
    
    # Debug informácie (ak je zapnuté)
    if DEBUG:
        with st.sidebar.expander("🐛 Debug Info"):
            st.json(dict(st.session_state))

# ====== Upload sekcia ======
def render_file_upload():
    """Vykresli sekciu pre nahranie súboru."""
    st.header(MAIN_TEXTS['upload_title'])
    
    uploaded_file = st.file_uploader(
        label=UPLOAD_TEXTS['file_uploader_label'],
        type=['xlsx', 'xls'],
        help=UPLOAD_TEXTS['file_uploader_help'],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # Validácia súboru
        is_valid, error_msg = validate_excel_file(uploaded_file)
        
        if not is_valid:
            st.error(f"{UPLOAD_TEXTS['upload_error']}: {error_msg}")
            return None
        
        st.success(f"{UPLOAD_TEXTS['file_uploaded_success']}: {uploaded_file.name}")
        
        # Informácie o súbore
        file_size_mb = uploaded_file.size / (1024 * 1024)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Veľkosť súboru", f"{file_size_mb:.2f} MB")
        with col2:
            st.metric("Typ súboru", uploaded_file.type)
        
        return uploaded_file
    
    return None

# ====== Výber harku a stĺpca ======
def render_sheet_column_selection(uploaded_file):
    """Vykresli sekciu pre výber harku a stĺpca."""
    if uploaded_file is None:
        return None, None, None
    
    st.header(SHEET_COLUMN_TEXTS['sheet_selection_title'])
    
    # Načítanie Excel súboru
    excel_file, error_msg = load_excel_file(uploaded_file)
    if error_msg:
        st.error(error_msg)
        return None, None, None
    
    # Získanie zoznamu harkov
    sheet_names = get_sheet_names(excel_file)
    
    # Výber harku
    selected_sheet = st.selectbox(
        SHEET_COLUMN_TEXTS['sheet_selection_label'],
        sheet_names,
        help=HELPER_TEXTS['tooltip_sheet_selection']
    )
    
    if selected_sheet:
        # Načítanie dát z vybraného harku
        df, error_msg = load_sheet_data(excel_file, selected_sheet)
        if error_msg:
            st.error(error_msg)
            return None, None, None
        
        if df.empty:
            st.warning(SHEET_COLUMN_TEXTS['empty_sheet'])
            return None, None, None
        
        # Náhľad harku
        with st.expander(SHEET_COLUMN_TEXTS['sheet_preview_title'], expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
            st.info(f"Celkový počet riadkov: {len(df)}")
        
        st.header(SHEET_COLUMN_TEXTS['column_selection_title'])
        
        # Výber stĺpca
        columns = df.columns.tolist()
        default_column = DEFAULT_COLUMN_NAME if DEFAULT_COLUMN_NAME in columns else columns[0]
        
        selected_column = st.selectbox(
            SHEET_COLUMN_TEXTS['column_selection_label'],
            columns,
            index=columns.index(default_column) if default_column in columns else 0,
            help=HELPER_TEXTS['tooltip_column_selection']
        )
        
        if selected_column:
            # Validácia stĺpca
            is_valid, stats, warning = validate_column_data(df, selected_column)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(VALIDATION_TEXTS['total_rows'], stats['total_rows'])
            with col2:
                st.metric(VALIDATION_TEXTS['valid_rows'], stats['valid_rows'])
            with col3:
                st.metric(VALIDATION_TEXTS['empty_rows'], stats['empty_rows'])
            
            if warning:
                st.warning(f"⚠️ {warning}")
            
            if is_valid:
                # Náhľad dát zo stĺpca
                with st.expander(SHEET_COLUMN_TEXTS['data_preview_title'], expanded=True):
                    preview_data = df[selected_column].dropna().head(10).tolist()
                    for i, company in enumerate(preview_data, 1):
                        st.write(f"{i}. {company}")
                
                return df, selected_sheet, selected_column
            else:
                st.error(VALIDATION_TEXTS['no_valid_data'])
    
    return None, None, None

# ====== Spracovanie ======
def render_processing_section(df, sheet_name, column_name):
    """Vykresli sekciu pre spracovanie dát."""
    if df is None or column_name is None:
        return None
    
    st.header(MAIN_TEXTS['processing_title'])
    
    # Príprava dát
    company_names = prepare_dataframe_for_processing(df, column_name)
    
    st.info(f"Pripravené na spracovanie: **{len(company_names)}** firiem z harku **'{sheet_name}'**, stĺpec **'{column_name}'**")
    
    # Tlačidlá pre spracovanie
    col1, col2 = st.columns([1, 3])
    with col1:
        start_processing = st.button(
            PROCESSING_TEXTS['start_processing'],
            type="primary",
            disabled=st.session_state.get('processing_stats', {}).get('is_processing', False)
        )
    
    # Progress sekcia
    if start_processing or st.session_state.get('processing_stats', {}).get('is_processing'):
        st.markdown("---")
        st.subheader(PROCESSING_TEXTS['progress_title'])
        
        # Inicializácia procesora
        processor = ICOProcessor()
        
        if start_processing:
            # Reset štatistík
            processor.reset_stats()
            
            # Spracovanie s progress monitoringom
            with st.spinner(PROCESSING_TEXTS['processing_in_progress']):
                results = processor.process_companies_with_progress(company_names)
            
            st.success(PROCESSING_TEXTS['processing_complete'])
            
            # Uloženie výsledkov do session state
            st.session_state.processing_results = results
            st.session_state.processed_df = df
            st.session_state.processed_column = column_name
            
            return results
        
        else:
            # Zobrazenie aktuálneho priebehu ak spracovanie prebieha
            stats = processor.get_processing_statistics()
            if stats:
                progress = stats['processed_companies'] / max(1, stats['total_companies'])
                st.progress(progress)
                st.write(f"Spracované: {stats['processed_companies']}/{stats['total_companies']}")
    
    return st.session_state.get('processing_results')

# ====== Výsledky a vizualizácie ======
def render_results_section(results, df, column_name):
    """Vykresli sekciu s výsledkami a vizualizáciami."""
    if not results:
        return
    
    st.header(MAIN_TEXTS['results_title'])
    
    # Vytvorenie output DataFrame
    output_df = create_output_dataframe(df, column_name, results)
    
    # Štatistiky
    total_companies = len(results['ICO'])
    successful_matches = sum(1 for ico in results['ICO'] if ico)
    success_rate = (successful_matches / total_companies) * 100 if total_companies > 0 else 0
    
    # Metriky
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(RESULTS_TEXTS['total_processed'], total_companies)
    with col2:
        st.metric(RESULTS_TEXTS['successful_matches'], successful_matches)
    with col3:
        st.metric(RESULTS_TEXTS['failed_searches'], total_companies - successful_matches)
    with col4:
        st.metric(RESULTS_TEXTS['success_rate'], f"{success_rate:.1f}%")
    
    # Grafické vizualizácie
    col1, col2 = st.columns(2)
    
    # Graf úspešnosti
    with col1:
        fig_pie = px.pie(
            values=[successful_matches, total_companies - successful_matches],
            names=['Úspešné', 'Neúspešné'],
            title='Úspešnosť vyhľadávania IČO',
            color_discrete_map={'Úspešné': CHART_COLORS['success'], 'Neúspešné': CHART_COLORS['error']}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Graf stratégií zhody
    with col2:
        if 'MatchStrategy' in results:
            # Filter out None values before counting
            strategy_data = [s for s in results['MatchStrategy'] if s is not None]
            if strategy_data:
                strategy_counts = pd.Series(strategy_data).value_counts()
                if len(strategy_counts) > 0:
                    # Vytvorenie DataFrame pre Plotly
                    chart_df = pd.DataFrame({
                        'Stratégia': strategy_counts.index,
                        'Počet': strategy_counts.values
                    })
                    fig_bar = px.bar(
                        chart_df,
                        x='Stratégia',
                        y='Počet',
                        title='Stratégie zhody',
                        color='Počet',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Žiadne dáta pre zobrazenie stratégií zhody")
            else:
                st.info("Žiadne úspešné vyhľadávania pre zobrazenie stratégií")
    
    # Tabuľka s výsledkami
    st.subheader("📋 Detailné výsledky")
    
    # Filter pre zobrazenie
    show_option = st.radio(
        "Zobraziť:",
        ["Všetky záznamy", "Iba úspešné", "Iba neúspešné"],
        horizontal=True
    )
    
    if show_option == "Iba úspešné":
        filtered_df = output_df[output_df['ICO'].notna()]
    elif show_option == "Iba neúspešné":
        filtered_df = output_df[output_df['ICO'].isna()]
    else:
        filtered_df = output_df
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download sekcia
    st.subheader(MAIN_TEXTS['download_title'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel download
        excel_buffer = create_excel_download(output_df)
        st.download_button(
            label="📊 Stiahnuť Excel súbor",
            data=excel_buffer,
            file_name=f"ico_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        # CSV download
        csv_data = create_csv_download(output_df)
        st.download_button(
            label="📋 Stiahnuť CSV súbor",
            data=csv_data,
            file_name=f"ico_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Dodatočné insights
    with st.expander("💡 Dodatočné informácie", expanded=False):
        st.write("**Top 5 najčastejšie používané varianty názvov:**")
        if 'UsedQueryVariant' in results:
            variant_data = [v for v in results['UsedQueryVariant'] if v]
            if variant_data:
                variant_counts = pd.Series(variant_data).value_counts().head()
                st.bar_chart(variant_counts)
            else:
                st.info("Žiadne varianty na zobrazenie")
        
        st.write("**Rozdelenie typov identifikátorov:**")
        if 'IdentifierType' in results:
            id_type_data = [t for t in results['IdentifierType'] if t]
            if id_type_data:
                id_type_counts = pd.Series(id_type_data).value_counts()
                st.bar_chart(id_type_counts)
            else:
                st.info("Žiadne typy identifikátorov na zobrazenie")

# ====== Hlavná aplikácia ======
def main():
    """Hlavná funkcia aplikácie."""
    
    # Rendering komponentov
    render_header()
    render_sidebar()
    
    # Upload sekcia
    uploaded_file = render_file_upload()
    
    if uploaded_file:
        # Výber harku a stĺpca
        df, sheet_name, column_name = render_sheet_column_selection(uploaded_file)
        
        if df is not None and column_name:
            # Spracovanie
            results = render_processing_section(df, sheet_name, column_name)
            
            # Výsledky
            if results:
                render_results_section(results, df, column_name)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
        "ICO Collector © 2025 | Powered by Streamlit | "
        "<a href='https://api.statistics.sk' target='_blank'>API Štatistického úradu SR</a> | "
        "Crafted by <a href='https://linkedin.com/in/tomasvince' target='_blank' style='color: #0066cc;'>Tomique</a>"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()