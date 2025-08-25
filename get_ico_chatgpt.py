#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Enhanced version with multi-sheet support and dynamic column selection

import time
import re
import requests
import pandas as pd
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import sys

# ====== Konfigurácia ======
DEFAULT_INPUT_XLSX = "test_120firiem.xlsx"  # predvolený vstupný súbor
DEFAULT_COLUMN_NAME = "Firma"
DEFAULT_SHEET_NAME = None  # prvý hark
INTERACTIVE_MODE = True

RPO_BASE = "https://api.statistics.sk/rpo/v1/search"
ONLY_ACTIVE = True

# Limity / výkon
MAX_WORKERS = 6                 # paralelizácia (6 vlákien je bezpečných)
MAX_REQ_PER_MIN = 60            # cieľ: neprekročiť ~60/min
REQUEST_TIMEOUT = 12            # s
RETRY_COUNT = 3
RETRY_SLEEP_BASE = 0.7          # s (exponenciálny backoff)
BATCH_SIZE = 60                 # dávkujeme ~60 a krátko spíme, aby sme držali tempo


# ====== Pomocné funkcie ======
def is_valid_ico(ico: str) -> bool:
    """
    Overí SK IČO – 8 číslic, kontrolný súčet podľa váh 8..2 (mod 11).
    """
    if not re.fullmatch(r"\d{8}", ico):
        return False
    digits = [int(ch) for ch in ico]
    weights = [8, 7, 6, 5, 4, 3, 2]
    s = sum(d * w for d, w in zip(digits[:7], weights))
    mod = s % 11
    check = {0: 1, 1: 0}.get(mod, 11 - mod)
    return digits[7] == check


def normalize_ico(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    digits = re.sub(r"\D+", "", value)
    if len(digits) == 8 and is_valid_ico(digits):
        return digits
    # ak má 8 číslic ale bez validácie, stále vrátime — nie všetky záznamy majú správe
    # naplnené metadáta, no IČO býva korektné
    return digits if len(digits) == 8 else None


def choose_best_record(records: List[Dict[str, Any]], query_name: str) -> Optional[Dict[str, Any]]:
    """
    Z výsledkov vyber najpravdepodobnejšiu zhodu:
    1) presná (casefold) zhoda v poli fullNames[].value
    2) prvý záznam
    """
    q = query_name.strip().casefold()
    for rec in records:
        for fn in rec.get("fullNames", []) or []:
            name_val = (fn.get("value") or "").strip().casefold()
            if name_val == q:
                return rec
    return records[0] if records else None


def extract_ico_from_record(record: Dict[str, Any]) -> Optional[str]:
    """
    RPO odpoveď: ICO je v poli 'identifiers' (zvyknú tam byť rôzne identifikátory).
    Budeme hľadať 8-miestne číslo. Ak je k dispozícii 'type' s hodnotou ICO, preferujeme ho.
    """
    for ident in record.get("identifiers", []) or []:
        type_val = (ident.get("type", {}).get("value") or "").casefold()
        val = normalize_ico(ident.get("value"))
        if type_val in {"ico", "ičo", "ico_sk"} and val:
            return val

    # fallback: prvé validné 8-miestne číslo v identifiers
    for ident in record.get("identifiers", []) or []:
        val = normalize_ico(ident.get("value"))
        if val:
            return val
    return None


def rpo_lookup_ico(company_name: str) -> Optional[str]:
    """
    Zavolá RPO /search?fullName=...&onlyActive=true a vráti IČO alebo None.
    """
    params = {
        "fullName": company_name,
        "onlyActive": str(ONLY_ACTIVE).lower(),
    }

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            r = requests.get(RPO_BASE, params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                records = (data or {}).get("results") or []
                if not records:
                    return None
                best = choose_best_record(records, company_name)
                return extract_ico_from_record(best) if best else None

            # 429/5xx: jemný backoff
            time.sleep(RETRY_SLEEP_BASE * attempt)
        except requests.RequestException:
            time.sleep(RETRY_SLEEP_BASE * attempt)

    return None


class RateLimiter:
    """
    Jednoduchý limiter: max N požiadaviek za 60 s (posuvné okno).
    """
    def __init__(self, max_per_min: int):
        self.max_per_min = max_per_min
        self.window_start = time.monotonic()
        self.count = 0

    def acquire(self):
        now = time.monotonic()
        elapsed = now - self.window_start
        if elapsed >= 60:
            self.window_start = now
            self.count = 0

        if self.count >= self.max_per_min:
            sleep_for = 60 - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
            self.window_start = time.monotonic()
            self.count = 0

        self.count += 1


# ====== Excel handling ======
def list_excel_sheets(file_path: Path) -> List[str]:
    """
    Vráti zoznam všetkých harkov v Excel súbore.
    """
    try:
        excel_file = pd.ExcelFile(file_path)
        return excel_file.sheet_names
    except Exception as e:
        print(f"Chyba pri čítaní harkov z {file_path}: {e}")
        return []

def get_user_sheet_choice(sheets: List[str]) -> str:
    """
    Interaktívny výber harku používateľom.
    """
    if len(sheets) == 1:
        print(f"Excel obsahuje jeden hark: '{sheets[0]}'")
        return sheets[0]
    
    print(f"\nExcel súbor obsahuje harky: {sheets}")
    while True:
        choice = input(f"Vyber hark (stlač Enter pre '{sheets[0]}'): ").strip()
        if not choice:
            return sheets[0]
        if choice in sheets:
            return choice
        print(f"Neplatný hark '{choice}'. Dostupné harky: {sheets}")

def get_user_column_choice(df: pd.DataFrame, default: str = DEFAULT_COLUMN_NAME) -> str:
    """
    Interaktívny výber stĺpca používateľom.
    """
    columns = df.columns.tolist()
    print(f"\nDostupné stĺpce: {columns}")
    
    while True:
        choice = input(f"Zadaj názov stĺpca s firmami (Enter pre '{default}'): ").strip()
        if not choice:
            if default in columns:
                return default
            else:
                print(f"Predvolený stĺpec '{default}' neexistuje. Vyber zo zoznamu.")
                continue
        if choice in columns:
            return choice
        print(f"Neplatný stĺpec '{choice}'. Dostupné stĺpce: {columns}")

def validate_column_data(df: pd.DataFrame, column: str) -> bool:
    """
    Validuje dáta v stĺpci - kontroluje prázdne hodnoty a typ.
    """
    if column not in df.columns:
        return False
    
    total_rows = len(df)
    non_null_rows = df[column].notna().sum()
    empty_rows = total_rows - non_null_rows
    
    if non_null_rows == 0:
        print(f"⚠️  Stĺpec '{column}' je úplne prázdny!")
        return False
    
    if empty_rows > 0:
        print(f"⚠️  Stĺpec '{column}' obsahuje {empty_rows}/{total_rows} prázdnych hodnôt.")
        choice = input("Pokračovať? (y/n): ").strip().lower()
        if choice not in ['y', 'yes', 'a', 'ano', '']:
            return False
    
    print(f"✅ Stĺpec '{column}' obsahuje {non_null_rows} validných záznamov.")
    return True

def get_user_input_file() -> Optional[Path]:
    """
    Interaktívne získanie vstupného súboru.
    """
    while True:
        src = input(f"Zadaj názov zdrojového Excel súboru (Enter pre '{DEFAULT_INPUT_XLSX}'): ").strip()
        if not src:
            src = DEFAULT_INPUT_XLSX
        
        src_path = Path(src)
        if not src_path.exists():
            print(f"Súbor '{src_path}' neexistuje. Skontroluj cestu/názov.")
            continue
        
        if src_path.suffix.lower() != ".xlsx":
            print("Očakávam .xlsx súbor.")
            continue
            
        return src_path


def process_names(names: List[str]) -> List[Optional[str]]:
    """
    Spracuje mená s paralelizáciou a rate-limitom (~60/min).
    """
    results: List[Optional[str]] = [None] * len(names)
    limiter = RateLimiter(MAX_REQ_PER_MIN)

    def task(i: int, name: str) -> Optional[str]:
        limiter.acquire()
        return rpo_lookup_ico(name)

    for offset in range(0, len(names), BATCH_SIZE):
        idxs = list(range(offset, min(offset + BATCH_SIZE, len(names))))
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            fut_map = {pool.submit(task, i, names[i]): i for i in idxs}
            for fut in as_completed(fut_map):
                i = fut_map[fut]
                try:
                    results[i] = fut.result()
                except Exception:
                    results[i] = None

        # krátka pauza medzi dávkami (držíme rytmus, šetríme API)
        time.sleep(1.0)

    return results


def main():
    print("🔍 ICO Collector - Základná verzia")
    print("=" * 40)
    
    # 1. Získanie vstupného súboru
    src_path = get_user_input_file()
    if not src_path:
        return
    
    # 2. Výber harku
    sheets = list_excel_sheets(src_path)
    if not sheets:
        print("Nepodarilo sa načítať harky z Excel súboru.")
        return
    
    selected_sheet = get_user_sheet_choice(sheets)
    
    # 3. Načítanie vybraného harku
    try:
        df = pd.read_excel(src_path, sheet_name=selected_sheet)
    except Exception as e:
        print(f"Chyba pri načítaní harku '{selected_sheet}': {e}")
        return
    
    if df.empty:
        print(f"Hark '{selected_sheet}' je prázdny.")
        return
    
    # 4. Výber stĺpca
    selected_column = get_user_column_choice(df, DEFAULT_COLUMN_NAME)
    
    # 5. Validácia dát v stĺpci
    if not validate_column_data(df, selected_column):
        print("Spracovanie prerušené kvôli problémom s dátami.")
        return

    # 6. Príprava výstupných súborov
    output_xlsx = src_path.with_name(f"{src_path.stem}_s_ICO.xlsx")
    output_csv = src_path.with_name(f"{src_path.stem}_s_ICO.csv")

    # 7. Extrakcia a spracovanie dát
    names = df[selected_column].astype(str).fillna("").tolist()
    
    print(f"\n📊 Začínam spracovanie {len(names)} firiem…")
    print(f"📁 Hark: '{selected_sheet}'")
    print(f"📋 Stĺpec: '{selected_column}'")
    print(f"💾 Výstupy: {output_xlsx.name}, {output_csv.name}\n")
    
    icos = process_names(names)

    # 8. Uloženie výsledkov
    df["ICO"] = icos
    df.to_excel(output_xlsx, index=False)
    df.to_csv(output_csv, index=False, encoding="utf-8")

    # 9. Štatistiky
    ok = sum(1 for x in icos if x)
    print(f"\n✅ Hotovo: {ok}/{len(icos)} nájdených IČO")
    print(f"📁 Výstupy: {output_xlsx.name}, {output_csv.name}")


if __name__ == "__main__":
    main()