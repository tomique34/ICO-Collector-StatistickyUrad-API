# Enhanced version of get_ico.py - odfiltruje z nazvu firmy s.r.o., a.s., s.p.o., a.s.
# a vyhladá výsledky na zaklade obchodneho mena firmy

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import re
import unicodedata
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests
import pandas as pd
from tqdm import tqdm
import sys

# ====== Konštanty ======
DEFAULT_COLUMN_NAME = "Firma"
DEFAULT_SHEET_NAME = None  # prvý hark
RPO_BASE = "https://api.statistics.sk/rpo/v1/search"
ONLY_ACTIVE = True
INTERACTIVE_MODE = True

# Limity / výkon
MAX_WORKERS = 6
MAX_REQ_PER_MIN = 60
REQUEST_TIMEOUT = 12
RETRY_COUNT = 3
RETRY_SLEEP_BASE = 0.7
BATCH_SIZE = 60

# ====== LOGGING ======
def setup_logging() -> Path:
    logs_dir = Path("LOGS")
    logs_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logfile = logs_dir / f"rpo_lookup_{ts}.log"

    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logfile

# ====== Excel handling ======
def list_excel_sheets(file_path: Path) -> List[str]:
    """
    Vráti zoznam všetkých harkov v Excel súbore.
    """
    try:
        excel_file = pd.ExcelFile(file_path)
        return excel_file.sheet_names
    except Exception as e:
        logging.error(f"Chyba pri čítaní harkov z {file_path}: {e}")
        return []

def get_user_sheet_choice(sheets: List[str]) -> str:
    """
    Interaktívny výber harku používateľom.
    """
    if len(sheets) == 1:
        print(f"Excel obsahuje jeden harok: '{sheets[0]}'")
        return sheets[0]
    
    print(f"\nExcel súbor obsahuje harky: {sheets}")
    while True:
        choice = input(f"Vyber harok (stlač Enter pre '{sheets[0]}'): ").strip()
        if not choice:
            return sheets[0]
        if choice in sheets:
            return choice
        print(f"Neplatný harok '{choice}'. Dostupné harky: {sheets}")

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

# ====== Normalizácia názvov ======
LEGAL_FORMS_REGEX = re.compile(
    r"""
    (?:,\s*)?
    (?:
        s\.?\s*r\.?\s*o\.?
      | spol\.\s*s\.?\s*r\.?\s*o\.?
      | a\.?\s*s\.?
      | v\.?\s*o\.?\s*s\.?
      | k\.?\s*s\.?
      | n\.?\s*o\.?
      | o\.?\s*z\.?
      | štátny\s+podnik
      | š\.?\s*p\.?
      | družstvo
      | akciová\s+spoločnosť
      | komanditná\s+spoločnosť
      | verejná\s+obchodná\s+spoločnosť
      | nezisková\s+organizácia
      | občianske\s+združenie
    )$
    """,
    re.IGNORECASE | re.VERBOSE
)
SPACES_REGEX = re.compile(r"\s+")

def strip_accents(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def clean_company_name(name: str) -> str:
    if not name:
        return ""
    n = str(name).strip().strip("„”\"'`")
    if "," in n:
        n = n.split(",", 1)[0].strip()
    n = LEGAL_FORMS_REGEX.sub("", n).strip()
    n = SPACES_REGEX.sub(" ", n)
    return n

def generate_query_variants(name: str) -> List[str]:
    variants = []
    raw = name.strip()
    cleaned = clean_company_name(raw)
    for x in (raw, cleaned, strip_accents(raw), strip_accents(cleaned)):
        x = x.strip()
        if x and x not in variants:
            variants.append(x)
    return variants

# ====== IČO extrakcia ======
def normalize_ico(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    digits = re.sub(r"\D+", "", value)
    return digits if len(digits) == 8 else None

def names_match(a: str, b: str) -> bool:
    return clean_company_name(a).casefold() == clean_company_name(b).casefold()

def choose_best_record(records: List[Dict[str, Any]], query_name: str) -> Tuple[Optional[Dict[str, Any]], str]:
    for rec in records:
        for fn in rec.get("fullNames", []) or []:
            if names_match(fn.get("value") or "", query_name):
                return rec, "exact"
    return (records[0], "first") if records else (None, "first")

def extract_ico_from_record(record: Dict[str, Any]) -> Tuple[Optional[str], str]:
    for ident in record.get("identifiers", []) or []:
        type_val = (ident.get("type", {}).get("value") or "").casefold()
        val = normalize_ico(ident.get("value"))
        if type_val in {"ico", "ičo", "ico_sk"} and val:
            return val, "ICO"
    for ident in record.get("identifiers", []) or []:
        val = normalize_ico(ident.get("value"))
        if val:
            return val, "Other"
    return None, "Other"

# ====== Volanie RPO ======
def rpo_lookup_detail(company_name: str) -> Dict[str, Optional[str]]:
    variants = generate_query_variants(company_name)
    for variant in variants:
        params = {"fullName": variant, "onlyActive": str(ONLY_ACTIVE).lower()}
        for attempt in range(1, RETRY_COUNT + 1):
            try:
                r = requests.get(RPO_BASE, params=params, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    data = r.json()
                    records = (data or {}).get("results") or []
                    if not records:
                        break
                    best, match_strategy = choose_best_record(records, variant)
                    if not best:
                        break
                    ico, id_type = extract_ico_from_record(best)
                    matched_name = None
                    for fn in best.get("fullNames", []) or []:
                        matched_name = fn.get("value") or matched_name
                    if ico:
                        return {
                            "ICO": ico,
                            "UsedQueryVariant": variant,
                            "MatchedFullName": matched_name,
                            "IdentifierType": id_type,
                            "MatchStrategy": match_strategy,
                            "Notes": None,
                        }
                    else:
                        return {
                            "ICO": None,
                            "UsedQueryVariant": variant,
                            "MatchedFullName": matched_name,
                            "IdentifierType": id_type,
                            "MatchStrategy": match_strategy,
                            "Notes": "Identifiers without valid ICO",
                        }
                time.sleep(RETRY_SLEEP_BASE * attempt)
            except requests.RequestException as e:
                logging.warning(f"RequestException for '{company_name}' variant '{variant}': {e}")
                time.sleep(RETRY_SLEEP_BASE * attempt)
    return {
        "ICO": None,
        "UsedQueryVariant": variants[0] if variants else None,
        "MatchedFullName": None,
        "IdentifierType": None,
        "MatchStrategy": None,
        "Notes": "Not found after variants/retries",
    }

# ====== Rate limiter ======
class RateLimiter:
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
            sleep_for = max(0, 60 - elapsed)
            if sleep_for > 0:
                logging.info(f"Rate limit reached, sleeping {sleep_for:.1f}s")
                time.sleep(sleep_for)
            self.window_start = time.monotonic()
            self.count = 0
        self.count += 1

# ====== Spracovanie s progres barom ======
def process_with_progress(names: List[str]) -> Dict[str, List[Optional[str]]]:
    n = len(names)
    limiter = RateLimiter(MAX_REQ_PER_MIN)

    icos, used_variants, matched_fullnames, id_types, match_strats, notes, clean_names = (
        [None] * n, [None] * n, [None] * n, [None] * n, [None] * n, [None] * n,
        [clean_company_name(x or "") for x in names]
    )

    def task(i: int, name: str) -> Dict[str, Optional[str]]:
        limiter.acquire()
        return rpo_lookup_detail(name)

    from tqdm import tqdm
    with tqdm(total=n, desc="Spracovanie firiem", unit="firma") as pbar:
        for offset in range(0, n, BATCH_SIZE):
            idxs = list(range(offset, min(offset + BATCH_SIZE, n)))
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
                fut_map = {pool.submit(task, i, names[i]): i for i in idxs}
                for fut in as_completed(fut_map):
                    i = fut_map[fut]
                    try:
                        res = fut.result()
                        icos[i] = res.get("ICO")
                        used_variants[i] = res.get("UsedQueryVariant")
                        matched_fullnames[i] = res.get("MatchedFullName")
                        id_types[i] = res.get("IdentifierType")
                        match_strats[i] = res.get("MatchStrategy")
                        notes[i] = res.get("Notes")
                    except Exception as e:
                        notes[i] = f"Exception: {e}"
                        logging.error(f"Exception processing index {i}, name '{names[i]}': {e}")
                    pbar.update(1)
            time.sleep(1.0)

    return {
        "ICO": icos,
        "CleanName": clean_names,
        "UsedQueryVariant": used_variants,
        "MatchedFullName": matched_fullnames,
        "IdentifierType": id_types,
        "MatchStrategy": match_strats,
        "Notes": notes,
    }

# ====== Main ======
def main():
    logfile = setup_logging()
    start_time = time.time()
    logging.info("==== RPO Lookup Started ====")

    # 1. Získanie cesty k súboru
    src = input("Zadaj názov zdrojového Excel súboru (.xlsx), napr. firmy.xlsx: ").strip()
    if not src:
        print("Nebolo zadané meno súboru. Končím.")
        return
    src_path = Path(src)
    if not src_path.exists():
        print(f"Súbor '{src_path}' neexistuje. Skontroluj cestu/názov.")
        return
    if src_path.suffix.lower() != ".xlsx":
        print("Očakávam .xlsx súbor.")
        return

    # 2. Výber harku
    sheets = list_excel_sheets(src_path)
    if not sheets:
        print("Nepodarilo sa načítať harky z Excel súboru.")
        return
    
    selected_sheet = get_user_sheet_choice(sheets)
    logging.info(f"Selected sheet: {selected_sheet}")
    
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
    logging.info(f"Selected column: {selected_column}")
    
    # 5. Validácia dát v stĺpci
    if not validate_column_data(df, selected_column):
        print("Spracovanie prerušené kvôli problémom s dátami.")
        return

    # 6. Príprava výstupných súborov
    out_xlsx = src_path.with_name(f"{src_path.stem}_s_ICO.xlsx")
    out_csv  = src_path.with_name(f"{src_path.stem}_s_ICO.csv")

    # 7. Extrakcia a spracovanie dát
    names = df[selected_column].astype(str).fillna("").tolist()
    logging.info(f"Loaded {len(names)} companies from {src_path}, sheet '{selected_sheet}', column '{selected_column}'")

    print(f"\n📊 Začínam spracovanie {len(names)} firiem…")
    print(f"📁 Hark: '{selected_sheet}'")
    print(f"📋 Stĺpec: '{selected_column}'")
    print(f"💾 Výstupy: {out_xlsx.name}, {out_csv.name}\n")
    
    details = process_with_progress(names)

    df["CleanName"] = details["CleanName"]
    df["ICO"] = details["ICO"]
    df["UsedQueryVariant"] = details["UsedQueryVariant"]
    df["MatchedFullName"] = details["MatchedFullName"]
    df["IdentifierType"] = details["IdentifierType"]
    df["MatchStrategy"] = details["MatchStrategy"]
    df["Notes"] = details["Notes"]

    df.to_excel(out_xlsx, index=False)
    df.to_csv(out_csv, index=False, encoding="utf-8")

    ok = sum(1 for x in details["ICO"] if x)
    elapsed = time.time() - start_time
    elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))

    logging.info(f"Finished: {ok}/{len(names)} ICO found")
    logging.info(f"Runtime: {elapsed_str}")
    logging.info(f"Outputs saved: {out_xlsx}, {out_csv}")

    print(f"Hotovo: {ok}/{len(names)} nájdených IČO")
    print(f"Výstupy uložené: {out_xlsx}  |  {out_csv}")
    print(f"Log súbor: {logfile}")
    print(f"Celkový čas behu: {elapsed_str}")

if __name__ == "__main__":
    main()