#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import re
import requests
import pandas as pd
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# ====== Konfigurácia ======
INPUT_XLSX = "test_120firiem.xlsx"       # vstupný Excel so stĺpcom 'Firma' (zmeň podľa seba)
OUTPUT_XLSX = "test_120firiem_s_ICO.xlsx"
OUTPUT_CSV  = "test_120firiem_s_ICO.csv"
COLUMN_NAME = "Firma"

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
    df = pd.read_excel(INPUT_XLSX)
    if COLUMN_NAME not in df.columns:
        raise ValueError(f"Vstupný Excel neobsahuje stĺpec '{COLUMN_NAME}'.")

    names = df[COLUMN_NAME].astype(str).fillna("").tolist()
    icos = process_names(names)

    df["ICO"] = icos
    df.to_excel(OUTPUT_XLSX, index=False)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    ok = sum(1 for x in icos if x)
    print(f"Hotovo: {ok}/{len(icos)} nájdených IČO")
    print(f"Výstup: {OUTPUT_XLSX}, {OUTPUT_CSV}")


if __name__ == "__main__":
    main()