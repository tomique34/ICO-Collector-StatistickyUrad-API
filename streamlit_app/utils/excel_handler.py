#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Excel file handling utilities pre ICO Collector Streamlit App
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st
from io import BytesIO

def validate_excel_file(uploaded_file) -> Tuple[bool, str]:
    """
    Validuje nahraný Excel súbor.
    
    Returns:
        Tuple[bool, str]: (je_platny, error_message)
    """
    if uploaded_file is None:
        return False, "Nie je vybraný žiadny súbor"
    
    # Kontrola typu súboru
    if not uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
        return False, "Nepodporovaný formát súboru. Použite .xlsx alebo .xls"
    
    # Kontrola veľkosti súboru (v bajtoch)
    if uploaded_file.size > 200 * 1024 * 1024:  # 200 MB
        return False, "Súbor je príliš veľký (max 200 MB)"
    
    return True, ""

def load_excel_file(uploaded_file) -> Tuple[Optional[pd.ExcelFile], str]:
    """
    Načíta Excel súbor a vráti ExcelFile objekt.
    
    Returns:
        Tuple[Optional[pd.ExcelFile], str]: (excel_file, error_message)
    """
    try:
        # Načítanie súboru do BytesIO
        bytes_data = uploaded_file.read()
        excel_file = pd.ExcelFile(BytesIO(bytes_data))
        return excel_file, ""
    except Exception as e:
        return None, f"Chyba pri načítaní súboru: {str(e)}"

def get_sheet_names(excel_file: pd.ExcelFile) -> List[str]:
    """
    Vráti zoznam názvov harkov v Excel súbore.
    """
    return excel_file.sheet_names

def load_sheet_data(excel_file: pd.ExcelFile, sheet_name: str) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Načíta dáta z konkrétneho harku.
    
    Returns:
        Tuple[Optional[pd.DataFrame], str]: (dataframe, error_message)
    """
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        return df, ""
    except Exception as e:
        return None, f"Chyba pri načítaní harku '{sheet_name}': {str(e)}"

def get_column_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyzuje stĺpce v DataFrame a vráti informácie o nich.
    """
    column_info = {}
    
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        total_count = len(df)
        null_count = total_count - non_null_count
        
        column_info[col] = {
            'total_rows': total_count,
            'non_null_rows': non_null_count,
            'null_rows': null_count,
            'null_percentage': (null_count / total_count) * 100 if total_count > 0 else 0,
            'data_type': str(df[col].dtype),
            'sample_values': df[col].dropna().head(3).tolist()
        }
    
    return column_info

def validate_column_data(df: pd.DataFrame, column: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    Validuje dáta v konkrétnom stĺpci.
    
    Returns:
        Tuple[bool, Dict[str, Any], str]: (je_platny, statistiky, warning_message)
    """
    if column not in df.columns:
        return False, {}, f"Stĺpec '{column}' neexistuje"
    
    total_rows = len(df)
    non_null_rows = df[column].notna().sum()
    null_rows = total_rows - non_null_rows
    null_percentage = (null_rows / total_rows) * 100 if total_rows > 0 else 0
    
    stats = {
        'total_rows': total_rows,
        'valid_rows': non_null_rows,
        'empty_rows': null_rows,
        'empty_percentage': null_percentage,
        'data_quality': 'excellent' if null_percentage < 5 else 'good' if null_percentage < 20 else 'poor'
    }
    
    # Varovné hlášky
    warning = ""
    if non_null_rows == 0:
        return False, stats, f"Stĺpec '{column}' je úplne prázdny"
    elif null_percentage > 50:
        warning = f"Stĺpec obsahuje {null_rows} prázdnych hodnôt z {total_rows} ({null_percentage:.1f}%)"
    elif null_percentage > 20:
        warning = f"Stĺpec obsahuje {null_rows} prázdnych hodnôt ({null_percentage:.1f}%)"
    
    return True, stats, warning

def prepare_dataframe_for_processing(df: pd.DataFrame, column: str) -> List[str]:
    """
    Pripraví zoznam názvov firiem na spracovanie.
    """
    # Filtrovanie a čistenie dát
    company_names = df[column].astype(str).fillna("").str.strip()
    
    # Odstránenie prázdnych riadkov
    company_names = company_names[company_names != ""]
    
    return company_names.tolist()

def create_output_dataframe(original_df: pd.DataFrame, column: str, results: Dict[str, List]) -> pd.DataFrame:
    """
    Vytvorí výstupný DataFrame s pôvodnými dátami a výsledkami.
    """
    # Vytvorenie kópie pôvodného DataFrame
    output_df = original_df.copy()
    
    # Pridanie nových stĺpcov s výsledkami
    for key, values in results.items():
        # Zabezpečenie, že máme správny počet hodnôt
        while len(values) < len(output_df):
            values.append(None)
        output_df[key] = values[:len(output_df)]
    
    return output_df

def create_excel_download(df: pd.DataFrame) -> BytesIO:
    """
    Vytvorí Excel súbor na stiahnutie.
    """
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Výsledky', index=False)
        
        # Získanie worksheet objektu pre formátovanie
        worksheet = writer.sheets['Výsledky']
        
        # Automatické prispôsobenie šírky stĺpcov
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Maximálna šírka 50
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output

def create_csv_download(df: pd.DataFrame) -> str:
    """
    Vytvorí CSV súbor na stiahnutie.
    """
    return df.to_csv(index=False, encoding='utf-8')

@st.cache_data
def cached_load_excel_file(file_data: bytes, file_name: str) -> Tuple[Optional[List[str]], str]:
    """
    Cached verzia načítania Excel súboru pre lepšiu výkonnosť.
    """
    try:
        excel_file = pd.ExcelFile(BytesIO(file_data))
        return excel_file.sheet_names, ""
    except Exception as e:
        return None, f"Chyba pri načítaní súboru: {str(e)}"

@st.cache_data  
def cached_load_sheet_data(file_data: bytes, sheet_name: str) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Cached verzia načítania harku pre lepšiu výkonnosť.
    """
    try:
        df = pd.read_excel(BytesIO(file_data), sheet_name=sheet_name)
        return df, ""
    except Exception as e:
        return None, f"Chyba pri načítaní harku '{sheet_name}': {str(e)}"