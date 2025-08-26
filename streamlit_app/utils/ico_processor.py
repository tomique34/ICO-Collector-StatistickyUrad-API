#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Core ICO processing logika pre Streamlit App
Adaptované z get_ico_v2.py s Streamlit integráciou
"""

import time
import re
import unicodedata
import logging
from typing import Optional, Dict, Any, List, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import streamlit as st
import requests
from .config import *

# ====== Normalizácia názvov firiem ======
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
    """Odstráni diakritiku zo slovenského textu."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

def clean_company_name(name: str) -> str:
    """Vyčistí názov firmy od právnych foriem a prebytočných znakov."""
    if not name:
        return ""
    n = str(name).strip().strip('"\'`')
    if "," in n:
        n = n.split(",", 1)[0].strip()
    n = LEGAL_FORMS_REGEX.sub("", n).strip()
    n = SPACES_REGEX.sub(" ", n)
    return n

def generate_query_variants(name: str) -> List[str]:
    """Generuje rôzne varianty názvu firmy na vyhľadávanie."""
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
    """Normalizuje IČO na 8-miestne číslo."""
    if not value:
        return None
    digits = re.sub(r"\D+", "", value)
    return digits if len(digits) == 8 else None

def names_match(a: str, b: str) -> bool:
    """Porovná dva názvy firiem po vyčistení."""
    return clean_company_name(a).casefold() == clean_company_name(b).casefold()

def choose_best_record(records: List[Dict[str, Any]], query_name: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Vyberie najpravdepodobnejšiu zhodu z výsledkov."""
    for rec in records:
        for fn in rec.get("fullNames", []) or []:
            if names_match(fn.get("value") or "", query_name):
                return rec, "exact"
    return (records[0], "first") if records else (None, "first")

def extract_ico_from_record(record: Dict[str, Any]) -> Tuple[Optional[str], str]:
    """Extrahuje IČO zo záznamu RPO API."""
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

# ====== Rate Limiter ======
class ThreadSafeRateLimiter:
    """Thread-safe rate limiter bez závislosti na Streamlit session state."""
    
    def __init__(self, max_per_min: int):
        self.max_per_min = max_per_min
        self.window_start = time.monotonic()
        self.count = 0
        self._lock = None
        
        # Import threading only when needed
        try:
            import threading
            self._lock = threading.Lock()
        except ImportError:
            pass
    
    def acquire(self):
        """Získa povolenie na API call s rate limitingom."""
        if self._lock:
            with self._lock:
                self._acquire_internal()
        else:
            self._acquire_internal()
    
    def _acquire_internal(self):
        """Internal rate limiting logic."""
        now = time.monotonic()
        elapsed = now - self.window_start
        
        if elapsed >= 60:
            self.window_start = now
            self.count = 0
        
        if self.count >= self.max_per_min:
            sleep_for = max(0, 60 - elapsed)
            if sleep_for > 0:
                time.sleep(sleep_for)
            self.window_start = time.monotonic()
            self.count = 0
        
        self.count += 1

# ====== API Volania ======
def rpo_lookup_detail(company_name: str) -> Dict[str, Optional[str]]:
    """Zavolá RPO API a vráti detailné informácie o firme."""
    variants = generate_query_variants(company_name)
    for variant in variants:
        params = {"fullName": variant, "onlyActive": str(ONLY_ACTIVE).lower()}
        for attempt in range(1, RETRY_COUNT + 1):
            try:
                r = requests.get(RPO_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
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
                time.sleep(RETRY_SLEEP_BASE * attempt)
    
    return {
        "ICO": None,
        "UsedQueryVariant": variants[0] if variants else None,
        "MatchedFullName": None,
        "IdentifierType": None,
        "MatchStrategy": None,
        "Notes": "Not found after variants/retries",
    }

# ====== Streamlit Processing ======
class ICOProcessor:
    """Hlavná trieda pre spracovanie ICO s Streamlit integráciou."""
    
    def __init__(self):
        self.rate_limiter = ThreadSafeRateLimiter(MAX_REQ_PER_MIN)
        self.start_time = None
        self.processed_count = 0
        self.successful_count = 0
        
        # Progress tracking v session state
        if 'processing_stats' not in st.session_state:
            st.session_state.processing_stats = {
                'total': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'start_time': None,
                'current_company': '',
                'is_processing': False
            }
    
    def process_companies_with_progress(
        self, 
        company_names: List[str], 
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, List[Optional[str]]]:
        """
        Spracuje zoznam firiem s progress trackingom pre Streamlit.
        """
        n = len(company_names)
        
        # Inicializácia výsledkov
        icos = [None] * n
        used_variants = [None] * n
        matched_fullnames = [None] * n
        id_types = [None] * n
        match_strats = [None] * n
        notes = [None] * n
        clean_names = [clean_company_name(x or "") for x in company_names]
        
        # Session state setup
        st.session_state.processing_stats.update({
            'total': n,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': time.time(),
            'is_processing': True
        })
        
        # Progress containers v Streamlit
        progress_bar = st.progress(0)
        status_text = st.empty()
        metrics_cols = st.columns(4)
        
        def task(i: int, name: str) -> Dict[str, Optional[str]]:
            """Spracovanie jednej firmy."""
            self.rate_limiter.acquire()
            # Note: Avoid accessing st.session_state from worker threads
            return rpo_lookup_detail(name)
        
        # Batch processing s progress updates
        for offset in range(0, n, BATCH_SIZE):
            if not st.session_state.processing_stats['is_processing']:
                break  # Stop ak používateľ prerušil
                
            idxs = list(range(offset, min(offset + BATCH_SIZE, n)))
            
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
                fut_map = {pool.submit(task, i, company_names[i]): i for i in idxs}
                
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
                        
                        if res.get("ICO"):
                            st.session_state.processing_stats['successful'] += 1
                        else:
                            st.session_state.processing_stats['failed'] += 1
                            
                    except Exception as e:
                        notes[i] = f"Exception: {e}"
                        st.session_state.processing_stats['failed'] += 1
                    
                    # Progress update
                    st.session_state.processing_stats['processed'] += 1
                    progress = st.session_state.processing_stats['processed'] / n
                    
                    # UI Updates
                    progress_bar.progress(progress)
                    
                    # Status text
                    elapsed = time.time() - st.session_state.processing_stats['start_time']
                    speed = st.session_state.processing_stats['processed'] / elapsed if elapsed > 0 else 0
                    eta = (n - st.session_state.processing_stats['processed']) / speed if speed > 0 else 0
                    
                    status_text.text(
                        f"Spracované: {st.session_state.processing_stats['processed']}/{n} | "
                        f"Úspešné: {st.session_state.processing_stats['successful']} | "
                        f"Rýchlosť: {speed:.1f} firiem/min | "
                        f"ETA: {eta/60:.1f} min"
                    )
                    
                    # Metrics
                    with metrics_cols[0]:
                        st.metric("Spracované", st.session_state.processing_stats['processed'], f"/{n}")
                    with metrics_cols[1]:
                        st.metric("Úspešné", st.session_state.processing_stats['successful'])
                    with metrics_cols[2]:
                        st.metric("Neúspešné", st.session_state.processing_stats['failed'])
                    with metrics_cols[3]:
                        success_rate = (st.session_state.processing_stats['successful'] / 
                                      max(1, st.session_state.processing_stats['processed'])) * 100
                        st.metric("Úspešnosť", f"{success_rate:.1f}%")
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback({
                            'progress': progress,
                            'processed': st.session_state.processing_stats['processed'],
                            'successful': st.session_state.processing_stats['successful'],
                            'current_company': company_names[i] if i < len(company_names) else ''
                        })
            
            # Krátka pauza medzi batchmi
            time.sleep(1.0)
        
        # Finalizácia
        st.session_state.processing_stats['is_processing'] = False
        progress_bar.progress(1.0)
        
        return {
            "ICO": icos,
            "CleanName": clean_names,
            "UsedQueryVariant": used_variants,
            "MatchedFullName": matched_fullnames,
            "IdentifierType": id_types,
            "MatchStrategy": match_strats,
            "Notes": notes,
        }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Vráti štatistiky spracovania."""
        stats = st.session_state.processing_stats
        
        if stats['start_time']:
            total_time = time.time() - stats['start_time']
            
            return {
                'total_companies': stats['total'],
                'processed_companies': stats['processed'],
                'successful_matches': stats['successful'],
                'failed_searches': stats['failed'],
                'success_rate': (stats['successful'] / max(1, stats['processed'])) * 100,
                'total_time': total_time,
                'avg_time_per_company': total_time / max(1, stats['processed']),
                'processing_speed': (stats['processed'] / total_time * 60) if total_time > 0 else 0,
                'is_processing': stats['is_processing'],
                'current_company': stats.get('current_company', '')
            }
        
        return {}
    
    def stop_processing(self):
        """Zastaví spracovanie."""
        st.session_state.processing_stats['is_processing'] = False
    
    def reset_stats(self):
        """Resetuje štatistiky spracovania."""
        st.session_state.processing_stats = {
            'total': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'current_company': '',
            'is_processing': False
        }