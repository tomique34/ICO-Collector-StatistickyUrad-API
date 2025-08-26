# ICO Collector - Automatické získavanie IČO firiem

**Verzia:** 2.1  
**Dátum vytvorenia:** 25. august 2025  
**Autor:** Tomas Vince  
**Kontakt:** https://linkedin.com/in/tomasvince

Tento projekt automaticky dohľadáva identifikačné čísla organizácií (IČO) slovenských firiem pomocou REST API Štatistického úradu SR. Poskytuje **konzolové skripty** aj **modernu webovu aplikáciu** pre jednoduchú prácu s Excel súbormi a automatické obohacovanie o IČO údaje z Registra právnych osôb (RPO).

## 📋 Dostupné verzie

### 🖥️ **Konzolové skripty** (Python)
- `get_ico_chatgpt.py` - základná verzia
- `get_ico_v2.py` - rozšírená verzia s pokročilými funkciami

### 🌐 **Webová aplikácia** (Streamlit)
- Moderné grafické rozhranie
- Real-time progress monitoring  
- Interaktívne grafy a štatistiky
- Jednoduchý upload a download súborov

## Funkcionalita

### Základná verzia (`get_ico_chatgpt.py`)
- ✅ Načítanie Excel súboru s firmami
- ✅ Dohľadávanie IČO cez RPO API
- ✅ Paralelné zpracovanie (6 vlákien)
- ✅ Rate limiting (max 60 požiadaviek/minútu)
- ✅ Retry mechanizmus s exponenciálnym backoffom
- ✅ Export do Excel a CSV formátu
- ✅ Validácia slovenských IČO podľa kontrolného súčtu

### Rozšírená verzia (`get_ico_v2.py`)
- ✅ Všetky funkcie základnej verzie
- ✅ **Inteligentné čistenie názvov firiem** - odstraňuje právne formy (s.r.o., a.s., atď.)
- ✅ **Viacero variantov vyhľadávania** - skúša rôzne varianty názvu
- ✅ **Handling diakritiky** - normalizácia slovenských znakov
- ✅ **Progress bar** - vizuálny indikátor postupu
- ✅ **Detailné logovanie** - komplexné záznamy do LOGS/ priečinka
- ✅ **Interaktívne zadanie** - používateľ zadá cestu k súboru
- ✅ **Rozšírené výsledky** - dodatočné informácie o zhode
- ✅ **Nové: Podpora viacerých harkov** - interaktívny výber harku
- ✅ **Nové: Dynamický výber stĺpca** - používateľ volí názov stĺpca s firmami

## Požiadavky na systém

- **Python 3.7+** (testované na Python 3.13)
- **Internetové pripojenie** pre API volania
- **Excel súbor** s názvami firiem v stĺpci "Firma"

## Inštalácia a nastavenie prostredia

### 1. Klonovanie/stiahnutie projektu
```bash
git clone <repository-url>
cd ICO-Collector_via_StatistickyUrad_API
```

### 2. Vytvorenie virtuálneho prostredia
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Inštalácia závislostí
```bash
pip install -r requirements.txt
```

### 4. Verifikácia inštalácie
```bash
python -c "import pandas, requests, openpyxl; print('Všetky balíčky úspešne nainštalované!')"
```

## Príprava vstupných údajov

### Formát Excel súboru
Vytvorte Excel súbor (`.xlsx`) s týmito požiadavkami:
- **Povinný stĺpec**: `Firma` - obsahuje názvy firiem
- **Príklad obsahu**:
  ```
  Firma
  Apple Slovakia s.r.o.
  Microsoft Slovakia, spol. s r.o.
  Google Slovakia a.s.
  Orange Slovensko, a.s.
  ```


## Spustenie aplikácií

### 🌐 Webová aplikácia (Streamlit) - ODPORÚČANÁ

#### Lokálne spustenie
```bash
# 1. Prejdite do streamlit_app/ priečinka
cd streamlit_app/

# 2. Spustite quick setup (automatická inštalácia)
./quick_setup.sh

# 3. Alebo manuálne nastavenie:
python3 -m venv ico_collector_env
source ico_collector_env/bin/activate  # macOS/Linux
# alebo ico_collector_env\Scripts\activate  # Windows
pip install -r requirements_streamlit.txt

# 4. Spustenie aplikácie
streamlit run streamlit_app.py
```

Aplikácia bude dostupná na: **http://localhost:8501**

#### Docker kontajner
```bash
# V streamlit_app/ priečinku
docker build -t ico-collector-streamlit .
docker run -p 8501:8501 ico-collector-streamlit
```

**Funkcie webovej aplikácie:**
- 🎯 **Drag & drop upload** Excel súborov
- 📊 **Real-time progress** monitoring
- 📈 **Interaktívne grafy** - úspešnosť, stratégie zhody
- 💾 **Jednoduché exporty** - Excel/CSV stiahnuť jedným klikom
- 🔍 **Filtrovanie výsledkov** - úspešné/neúspešné/všetky
- 📱 **Responzívne rozhranie** - funguje na mobile i desktop

### 🖥️ Konzolové skripty

#### Základná verzia
```bash
python get_ico_chatgpt.py
```
- **Interaktívne zadávanie súboru** - používateľ volí Excel súbor
- **Výber harku** - zobrazí dostupné harky a umožní výber
- **Výber stĺpca** - zobrazí dostupné stĺpce a umožní výber
- Vytvorí výstupné súbory s príponou `_s_ICO`

#### Rozšírená verzia
```bash
python get_ico_v2.py
```
- **Interaktívne zadávanie súboru** - používateľ volí Excel súbor
- **Výber harku** - zobrazí dostupné harky a umožní výber
- **Výber stĺpca** - zobrazí dostupné stĺpce a umožní výber  
- **Validácia dát** - kontrola prázdnych hodnôt pred spracovaním
- Vytvorí výstupné súbory s príponou `_s_ICO`
- Vytvorí log súbor v priečinku `LOGS/`

## Výstupné súbory

### Excel súbor (`*_s_ICO.xlsx`)
Pôvodné údaje + nové stĺpce:

**Základná verzia:**
- `ICO` - nájdené IČO alebo prázdne

**Rozšírená verzia:**
- `CleanName` - vyčistený názov firmy
- `ICO` - nájdené IČO
- `UsedQueryVariant` - použitý variant názvu pri vyhľadávaní
- `MatchedFullName` - presný názov z RPO
- `IdentifierType` - typ identifikátora (ICO/Other)
- `MatchStrategy` - stratégia zhody (exact/first)
- `Notes` - poznámky o spracovaní

### CSV súbor (`*_s_ICO.csv`)
Rovnaké údaje ako Excel v CSV formáte (UTF-8).

### Log súbory (iba v2)
V priečinku `LOGS/` - detailné záznamy o spracovaní:
- Časy API volaní
- Chybové stavy
- Štatistiky úspešnosti

## Príklady použitia

### 🌐 Webová aplikácia (odporúčané)

```bash
# Quick start
cd streamlit_app/
./quick_setup.sh

# Po spustení prejdite na http://localhost:8501
# 1. Nahrajte Excel súbor pomocou drag & drop
# 2. Vyberte hark a stĺpec s firmami  
# 3. Kliknite na "Spracovať firmy"
# 4. Sledujte real-time progress a výsledky
# 5. Stiahnite výsledky jedným klikom (Excel/CSV)
```

### 🖥️ Konzolové skripty

```bash
# Aktivácia virtuálneho prostredia
source venv/bin/activate  # Linux/Mac
# alebo
venv\Scripts\activate     # Windows

# Spustenie rozšírenej verzie
python get_ico_v2.py

# Zadanie názvu súboru
> Zadaj názov zdrojového Excel súboru (.xlsx), napr. firmy.xlsx: firmy.xlsx

# Výber harku (ak má súbor viacero harkov)
> Excel súbor obsahuje harky: ['Sheet1', 'Firmy_SK', 'Companies']
> Vyber hark (stlač Enter pre 'Sheet1'): Firmy_SK

# Výber stĺpca
> Dostupné stĺpce: ['Názov', 'Firma', 'Company_Name', 'Adresa']
> Zadaj názov stĺpca s firmami (Enter pre 'Firma'): Názov

# Validácia dát
✅ Stĺpec 'Názov' obsahuje 50 validných záznamov.

# Spracovanie
📊 Začínam spracovanie 50 firiem…
📁 Hark: 'Firmy_SK'
📋 Stĺpec: 'Názov'
💾 Výstupy: firmy_s_ICO.xlsx, firmy_s_ICO.csv

Spracovanie firiem: 100%|██████████| 50/50 [01:05<00:00,  1.30s/firma]

✅ Hotovo: 48/50 nájdených IČO
📁 Výstupy: firmy_s_ICO.xlsx, firmy_s_ICO.csv
Log súbor: LOGS/rpo_lookup_2025-08-25_14-30-15.log
Celkový čas behu: 00:01:05
```

## Konfigurácia

V hlavičke skriptov môžete upraviť:

```python
MAX_WORKERS = 6              # Počet súbežných vlákien
MAX_REQ_PER_MIN = 60         # Limit požiadaviek za minútu
REQUEST_TIMEOUT = 12         # Timeout pre API volanie (sekundy)
RETRY_COUNT = 3              # Počet pokusov pri chybe
BATCH_SIZE = 60              # Veľkosť dávky
```

## API dokumentácia

Projekt využíva REST API Štatistického úradu SR:
- **URL**: https://api.statistics.sk/rpo/v1/search
- **Dokumentácia**: https://susrrpo.docs.apiary.io/
- **Parameter fullName**: názov firmy na vyhľadávanie
- **Parameter onlyActive**: true = iba aktívne firmy

## Riešenie problémov

### Webová aplikácia (Streamlit)

#### "Session state has no attribute" chyba
```bash
# Reštartujte aplikáciu
Ctrl+C
streamlit run streamlit_app.py
```

#### Streamlit sa nespustí
```bash
# Overte inštaláciu
pip install streamlit
streamlit --version

# Alebo použite quick setup
./quick_setup.sh
```

#### Docker problémy
```bash
# Znovu buildnite image
docker build --no-cache -t ico-collector-streamlit .
docker run -p 8501:8501 ico-collector-streamlit
```

### Konzolové skripty

#### Chyba "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

#### Chyba "File not found"
- Skontrolujte cestu k Excel súboru
- Overte, že súbor má príponu `.xlsx`
- Overte, že súbor obsahuje stĺpec "Firma"

### Všeobecné problémy

#### Pomalé spracovanie
- API má limit 60 požiadaviek/minútu
- Pri veľkom počte firiem bude spracovanie trvať dlhšie
- Neprekračujte odporúčané limity

#### API nedostupnosť
- Skontrolujte internetové pripojenie
- API môže byť dočasne nedostupné
- Skript automaticky opakuje neúspešné pokusy

#### Všetky firmy "neúspešné"
- Overte názvy firiem v Excel súbore
- Firmy musia existovať v slovenskom registri
- Skúste známe slovenské firmy (napr. "Slovnaft", "Tesco Stores SR")

## Licencia

Tento projekt je určený na vzdelávacie a nekomerčné účely. Rešpektujte podmienky používania RPO API.

## Podpora

V prípade problémov:
1. Skontrolujte log súbory v `LOGS/` priečinku
2. Overte správnosť vstupných údajov
3. Skontrolujte konfiguráciu virtuálneho prostredia