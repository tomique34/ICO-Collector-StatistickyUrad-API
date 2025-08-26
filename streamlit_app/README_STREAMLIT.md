# ICO Collector - Streamlit Web Aplikácia

**Verzia:** 2.0  
**Dátum vytvorenia:** 25. august 2025  
**Autor:** Tomas Vince  
**Kontakt:** https://linkedin.com/in/tomasvince

Moderná web aplikácia pre automatické získavanie IČO slovenských firiem pomocou REST API Štatistického úradu SR s pokročilými vizualizáciami a používateľsky prívetivým rozhraním.

## 🌟 Funkcie Web Aplikácie

### 🎯 Hlavné Features
- **📤 Drag & Drop Upload** - Jednoduché nahrávanie Excel súborov
- **🔍 Interaktívny Výber** - Výber harku a stĺpca s náhľadom dát
- **📊 Real-time Progress** - Live monitoring spracovania s metrikami
- **📈 Pokročilé Vizualizácie** - Grafy, charts a dashboard
- **💾 Multiple Export Options** - Excel, CSV, JSON s formátovaním
- **🇸🇰 Slovenské Rozhranie** - Kompletne v slovenčine
- **📱 Responsive Design** - Optimalizované pre všetky zariadenia

### 🆚 Výhody oproti CLI verzii
| Feature | CLI Verzia | Web Aplikácia |
|---------|------------|---------------|
| Používateľské rozhranie | ❌ Terminál | ✅ Moderné web UI |
| File upload | 📁 Lokálny súbor | 🌐 Drag & drop |
| Progress monitoring | ⏳ Text progress | 📊 Live dashboard |
| Výsledky | 📄 Textový výstup | 📈 Interaktívne grafy |
| Export | 💾 Excel/CSV | 💎 Formátované súbory |
| Insights | ❌ Žiadne | 🔍 Pokročilé analýzy |

## 🚀 Rýchly Štart

### Predpoklady
- **Python 3.8+**
- **Internetové pripojenie**
- **Moderný web browser**

### 1. Inštalácia
```bash
# Navigácia do Streamlit adresára
cd streamlit_app

# Inštalácia závislostí
pip install -r requirements_streamlit.txt
```

### 2. Spustenie Aplikácie
```bash
# Základné spustenie
streamlit run streamlit_app.py

# Alebo s custom portom
streamlit run streamlit_app.py --server.port 8502

# S verbose logovaním
streamlit run streamlit_app.py --logger.level debug
```

### 3. Prístup k Aplikácii
Otvorte browser a choďte na:
- **Lokálne**: http://localhost:8501
- **Sieť**: http://YOUR_IP:8501

## 📋 Používanie Aplikácie

### Krok 1: Nahratie Excel Súboru
1. 📤 Kliknite na upload area alebo pretiahnite súbor
2. ✅ Aplikácia automaticky validuje súbor
3. 📊 Zobrazí sa náhľad a základné info

### Krok 2: Konfigurácia
1. 📋 Vyberte hark zo zoznamu dostupných harkov
2. 📊 Vyberte stĺpec obsahujúci názvy firiem
3. 🛡️ Skontrolujte validáciu dát

### Krok 3: Spracovanie
1. 🚀 Kliknite "Spustiť spracovanie"
2. 📈 Sledujte real-time progress a metriky
3. ⏸️ Možnosť zastavenia počas spracovania

### Krok 4: Výsledky
1. 📊 Prezrite si dashboard s vizualizáciami
2. 🔍 Analyzujte detailné výsledky
3. 💾 Stiahnite výsledky v požadovanom formáte

## ⚙️ Konfigurácia

### Environment Variables
```bash
# Aplikácia
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# API nastavenia
export MAX_REQ_PER_MIN=60
export REQUEST_TIMEOUT=12
export RETRY_COUNT=3

# Debug
export DEBUG=false
export LOG_LEVEL=INFO
```

### Streamlit Config (`.streamlit/config.toml`)
```toml
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
showErrorDetails = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

# Nastavenie working directory
WORKDIR /app

# Kopírovanie requirements
COPY requirements_streamlit.txt .
RUN pip install --no-cache-dir -r requirements_streamlit.txt

# Kopírovanie aplikácie
COPY . .

# Expose port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Spustenie aplikácie
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  ico-collector:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DEBUG=false
      - MAX_REQ_PER_MIN=60
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Docker Build & Run
```bash
# Build image
docker build -t ico-collector-streamlit .

# Run container
docker run -p 8501:8501 --name ico-collector ico-collector-streamlit

# Run s docker-compose
docker-compose up -d
```

## ☁️ Cloud Deployment

### 1. Streamlit Cloud (Odporúčané)
```bash
# 1. Push kód na GitHub
git push origin main

# 2. Choďte na https://share.streamlit.io/
# 3. Pripojte GitHub repository
# 4. Nastavte:
#    - Repository: your-username/ICO-Collector-StatistickyUrad-API
#    - Branch: main
#    - Main file path: streamlit_app/streamlit_app.py
```

### 2. Heroku Deployment
```bash
# Vytvorenie Procfile
echo "web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Heroku setup
heroku create ico-collector-app
heroku config:set MAX_REQ_PER_MIN=60
git push heroku main
```

### 3. AWS EC2/ECS
```bash
# EC2 User data script
#!/bin/bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo docker run -d -p 8501:8501 your-dockerhub-username/ico-collector
```

### 4. DigitalOcean App Platform
```yaml
# .do/app.yaml
name: ico-collector
services:
- name: web
  source_dir: /streamlit_app
  dockerfile_path: Dockerfile
  http_port: 8501
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
  envs:
  - key: MAX_REQ_PER_MIN
    value: "60"
```

## 🔧 Pokročilá Konfigurácia

### Custom Téma
```python
# V streamlit_app.py
st.set_page_config(
    page_title="ICO Collector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/ico-collector',
        'Report a bug': 'https://github.com/your-username/ico-collector/issues',
        'About': "ICO Collector v2.0 - Powered by Streamlit"
    }
)
```

### SSL/HTTPS Setup
```bash
# Nginx proxy config
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Load Balancing
```yaml
# docker-compose.yml s load balancer
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app1
      - app2
  
  app1:
    build: .
    expose:
      - "8501"
  
  app2:
    build: .
    expose:
      - "8501"
```

## 📊 Monitoring a Analytika

### Health Checks
```python
# health_check.py
import requests
import sys

def check_health():
    try:
        response = requests.get('http://localhost:8501/_stcore/health', timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    sys.exit(0 if check_health() else 1)
```

### Logging
```python
# Custom logging setup
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/streamlit_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics Collection
```python
# metrics.py
import streamlit as st
from datetime import datetime

def track_usage(event_name, metadata=None):
    """Track usage events for analytics."""
    if 'usage_events' not in st.session_state:
        st.session_state.usage_events = []
    
    event = {
        'timestamp': datetime.now().isoformat(),
        'event': event_name,
        'metadata': metadata or {}
    }
    
    st.session_state.usage_events.append(event)
```

## 🔒 Bezpečnosť

### CORS a Security Headers
```python
# security_middleware.py
def add_security_headers():
    st.markdown("""
    <script>
    // Security headers
    const meta = document.createElement('meta');
    meta.httpEquiv = 'Content-Security-Policy';
    meta.content = "default-src 'self'; script-src 'self' 'unsafe-inline'";
    document.head.appendChild(meta);
    </script>
    """, unsafe_allow_html=True)
```

### Rate Limiting
```python
# rate_limit.py
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, window=3600):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip):
        now = time.time()
        # Cleanup old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] 
            if now - req_time < self.window
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        self.requests[client_ip].append(now)
        return True
```

## 🚨 Troubleshooting

### Časté Problémy

**1. Port už používaný**
```bash
# Nájdenie procesu na porte
lsof -i :8501
# Zabitie procesu
kill -9 PID
```

**2. Memory Issues**
```python
# V streamlit_app.py
import gc
import streamlit as st

@st.cache_data(max_entries=10)
def cached_function():
    # Implementation
    pass

# Manual garbage collection
if st.button("Vyčistiť pamäť"):
    gc.collect()
    st.success("Pamäť vyčistená")
```

**3. Slow Performance**
```python
# Optimalizácie
- Použite st.cache_data pre expensive operations
- Limitujte počet zobrazených riadkov
- Implementujte lazy loading
- Použite connection pooling pre API
```

**4. API Timeout Issues**
```python
# V config.py
REQUEST_TIMEOUT = 30  # Zvýšte timeout
RETRY_COUNT = 5       # Viac pokusov
MAX_WORKERS = 4       # Menej paralelných requestov
```

### Debug Mode
```bash
# Spustenie s debug informáciami
streamlit run streamlit_app.py --logger.level debug --server.enableStaticServing false
```

### Performance Monitoring
```python
# performance_monitor.py
import time
import streamlit as st
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        st.sidebar.metric(
            f"⏱️ {func.__name__}",
            f"{(end_time - start_time):.2f}s"
        )
        
        return result
    return wrapper
```

## 📞 Podpora a Údržba

### Backup Strategy
```bash
# Automatický backup
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz streamlit_app/ logs/
```

### Update Process
```bash
# 1. Backup aktuálnej verzie
cp -r streamlit_app streamlit_app_backup

# 2. Pull najnovšie zmeny
git pull origin main

# 3. Update dependencies
pip install -r requirements_streamlit.txt --upgrade

# 4. Restart aplikácie
docker-compose restart
```

### Kontakt
- **Issues**: https://github.com/tomique34/ICO-Collector-StatistickyUrad-API/issues
- **LinkedIn**: https://linkedin.com/in/tomasvince
- **Email**: Dostupný cez LinkedIn profil

---

**© 2025 ICO Collector Streamlit App | Powered by Streamlit & Slovak Statistical Office API**