#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File upload komponenty pre ICO Collector Streamlit App
"""

import streamlit as st
import pandas as pd
from typing import Optional, Tuple, Dict, Any
from utils.excel_handler import validate_excel_file, load_excel_file, get_sheet_names
from assets.localization import *

def render_advanced_file_uploader():
    """
    Pokročilý file uploader s dodatočnými funkciami.
    """
    st.markdown("### 📤 Nahranie Excel súboru")
    
    # Informačný box o podporovaných formátoch
    with st.expander("ℹ️ Podporované formáty a požiadavky", expanded=False):
        st.markdown("""
        **Podporované formáty:**
        - `.xlsx` (Excel 2007+)
        - `.xls` (Excel 97-2003)
        
        **Požiadavky na súbor:**
        - Maximálna veľkosť: 200 MB
        - Musí obsahovať aspoň jeden hark s údajmi
        - Musí obsahovať stĺpec s názvami firiem
        
        **Odporúčania:**
        - Názvy firiem by mali byť v jednom stĺpci
        - Prázdne riadky budú ignorované
        - Pre lepšie výsledky používajte úplné názvy firiem
        """)
    
    # File uploader s custom štýlom
    uploaded_file = st.file_uploader(
        label="Vyberte Excel súbor",
        type=['xlsx', 'xls'],
        help="Pretiahnite súbor sem alebo kliknite pre výber",
        accept_multiple_files=False,
        key="main_file_uploader"
    )
    
    if uploaded_file is not None:
        return process_uploaded_file(uploaded_file)
    
    # Ukážkové dáta pre testovanie
    with st.expander("🧪 Vyskúšajte s ukážkovými dátami", expanded=False):
        st.markdown("""
        Ak nemáte vlastný súbor, môžete si vytvoriť ukážkové dáta:
        """)
        
        if st.button("📊 Vytvoriť ukážkové dáta"):
            sample_data = create_sample_data()
            return sample_data, "Ukážkové dáta", None
    
    return None, None, None

def process_uploaded_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
    """
    Spracuje nahraný súbor a vráti základné informácie.
    """
    # Validácia súboru
    is_valid, error_msg = validate_excel_file(uploaded_file)
    
    if not is_valid:
        st.error(f"❌ {error_msg}")
        return None, None, error_msg
    
    # Úspešné nahranie
    st.success(f"✅ Súbor úspešne nahraný: **{uploaded_file.name}**")
    
    # Základné informácie o súbore
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📏 Veľkosť", f"{file_size_mb:.2f} MB")
    with col2:
        st.metric("📄 Typ", uploaded_file.type.split('/')[-1].upper())
    with col3:
        upload_time = st.empty()
        upload_time.metric("⏰ Nahraný", "Teraz")
    
    # Načítanie Excel súboru
    excel_file, error_msg = load_excel_file(uploaded_file)
    if error_msg:
        st.error(f"❌ {error_msg}")
        return None, None, error_msg
    
    # Získanie zoznamu harkov
    sheet_names = get_sheet_names(excel_file)
    
    st.info(f"📋 Súbor obsahuje **{len(sheet_names)}** hark(ov): {', '.join(sheet_names)}")
    
    return excel_file, uploaded_file.name, None

def render_file_preview(df: pd.DataFrame, max_rows: int = 10):
    """
    Vykresli náhľad nahraného súboru.
    """
    if df is None or df.empty:
        st.warning("⚠️ Žiadne dáta na zobrazenie")
        return
    
    st.markdown("### 👀 Náhľad dát")
    
    # Základné info o súbore
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Riadky", len(df))
    with col2:
        st.metric("📋 Stĺpce", len(df.columns))
    with col3:
        non_empty_cells = df.count().sum()
        total_cells = len(df) * len(df.columns)
        fill_rate = (non_empty_cells / total_cells) * 100 if total_cells > 0 else 0
        st.metric("📈 Naplnenosť", f"{fill_rate:.1f}%")
    
    # Náhľad dát
    display_df = df.head(max_rows)
    st.dataframe(
        display_df, 
        use_container_width=True,
        hide_index=False
    )
    
    if len(df) > max_rows:
        st.info(f"Zobrazených prvých {max_rows} riadkov z {len(df)} celkovo")
    
    # Informácie o stĺpcoch
    with st.expander("📋 Detail stĺpcov", expanded=False):
        column_info = []
        for col in df.columns:
            non_null_count = df[col].notna().sum()
            null_count = len(df) - non_null_count
            dtype = str(df[col].dtype)
            
            column_info.append({
                'Stĺpec': col,
                'Typ': dtype,
                'Platné': non_null_count,
                'Prázdne': null_count,
                'Naplnenosť (%)': f"{(non_null_count / len(df)) * 100:.1f}%"
            })
        
        column_df = pd.DataFrame(column_info)
        st.dataframe(column_df, use_container_width=True)

def create_sample_data() -> pd.DataFrame:
    """
    Vytvorí ukážkové dáta na testovanie.
    """
    sample_companies = [
        "Orange Slovensko, a.s.",
        "Slovak Telekom, a.s.",
        "Tesco Stores SR, a.s.",
        "Kaufland Slovenská republika v.o.s.",
        "Lidl Slovenská republika, v.o.s.",
        "COOP Jednota Slovensko",
        "Slovenská sporiteľňa, a.s.",
        "Všeobecná zdravotná poisťovňa, a.s.",
        "Union zdravotná poisťovňa, a.s.",
        "Dôvera zdravotná poisťovňa, a.s.",
        "Železnice Slovenskej republiky",
        "Slovenský plynárenský priemysel, a.s.",
        "Západoslovenská energetika, a.s.",
        "Východoslovenská energetika, a.s.",
        "Stredoslovenská energetika, a.s."
    ]
    
    # Pridanie ďalších stĺpcov pre realistickejšie dáta
    sample_data = {
        'Firma': sample_companies,
        'Mesto': [
            'Bratislava', 'Bratislava', 'Trnava', 'Bratislava', 'Nitra',
            'Bratislava', 'Bratislava', 'Bratislava', 'Bratislava', 'Bratislava',
            'Bratislava', 'Bratislava', 'Trenčín', 'Košice', 'Žilina'
        ],
        'Sektor': [
            'Telekomunikácie', 'Telekomunikácie', 'Maloobchod', 'Maloobchod', 'Maloobchod',
            'Maloobchod', 'Bankovníctvo', 'Poisťovníctvo', 'Poisťovníctvo', 'Poisťovníctvo',
            'Doprava', 'Energetika', 'Energetika', 'Energetika', 'Energetika'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    st.success("✅ Vytvorené ukážkové dáta s 15 firmami")
    st.info("💡 Tieto dáta môžete použiť na vyskúšanie aplikácie")
    
    return df

def render_file_validation_results(validation_results: Dict[str, Any]):
    """
    Vykresli výsledky validácie súboru.
    """
    if not validation_results:
        return
    
    st.markdown("### 🛡️ Výsledky validácie")
    
    if validation_results.get('is_valid', False):
        st.success("✅ Súbor prošiel validáciou")
    else:
        st.error("❌ Súbor neprešiel validáciou")
    
    # Detailné výsledky
    if validation_results.get('errors'):
        st.error("**Chyby:**")
        for error in validation_results['errors']:
            st.error(f"• {error}")
    
    if validation_results.get('warnings'):
        st.warning("**Upozornenia:**")
        for warning in validation_results['warnings']:
            st.warning(f"• {warning}")
    
    if validation_results.get('info'):
        st.info("**Informácie:**")
        for info in validation_results['info']:
            st.info(f"• {info}")

def render_drag_drop_area():
    """
    Vykresli custom drag & drop oblasť.
    """
    # Custom CSS pre drag & drop
    st.markdown("""
    <style>
    .drag-drop-area {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 40px;
        text-align: center;
        background-color: #fafafa;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    .drag-drop-area:hover {
        border-color: #1f77b4;
        background-color: #f0f8ff;
    }
    .drag-drop-text {
        font-size: 18px;
        color: #666666;
        margin-bottom: 10px;
    }
    .drag-drop-subtext {
        font-size: 14px;
        color: #999999;
    }
    </style>
    
    <div class="drag-drop-area">
        <div class="drag-drop-text">
            📁 Pretiahnite Excel súbor sem
        </div>
        <div class="drag-drop-subtext">
            alebo kliknite nižšie pre výber súboru<br>
            Podporované formáty: .xlsx, .xls | Max. 200 MB
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_file_upload_tips():
    """
    Zobrazí tipy pre nahrávanie súborov.
    """
    with st.expander("💡 Tipy pre lepšie výsledky", expanded=False):
        st.markdown("""
        **Pre najlepšie výsledky:**
        
        1. **Kvalitné dáta**: Používajte presné a úplné názvy firiem
        2. **Formátovanie**: Jeden názov firmy na riadok v jednom stĺpci
        3. **Čistenie**: Odstráňte prebytočné medzery a znaky
        4. **Konzistentnosť**: Používajte konzistentné formáty názvov
        
        **Vyhýbajte sa:**
        - Zlúčeným bunkám
        - Prázdnym riadkom medzi údajmi
        - Špeciálnym znakom v názvoch stĺpcov
        - Príliš krátkym alebo neúplným názvom firiem
        """)

def render_file_statistics(df: pd.DataFrame):
    """
    Vykresli podrobné štatistiky o nahranom súbore.
    """
    if df is None or df.empty:
        return
    
    st.markdown("### 📊 Štatistiky súboru")
    
    # Základné metriky
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Riadky", len(df))
    
    with col2:
        st.metric("Stĺpce", len(df.columns))
    
    with col3:
        memory_usage = df.memory_usage(deep=True).sum()
        st.metric("Pamäť", f"{memory_usage / 1024:.1f} KB")
    
    with col4:
        numeric_cols = len(df.select_dtypes(include='number').columns)
        st.metric("Číselné stĺpce", numeric_cols)
    
    # Graf typov dát
    dtype_counts = df.dtypes.value_counts()
    if len(dtype_counts) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Typy dát:**")
            for dtype, count in dtype_counts.items():
                st.write(f"• {dtype}: {count} stĺpcov")
        
        with col2:
            # Graf distribúcie prázdnych hodnôt
            null_counts = df.isnull().sum().sort_values(ascending=False)
            if null_counts.max() > 0:
                st.markdown("**Top 5 stĺpcov s prázdnymi hodnotami:**")
                for col, count in null_counts.head().items():
                    if count > 0:
                        percentage = (count / len(df)) * 100
                        st.write(f"• {col}: {count} ({percentage:.1f}%)")