FROM python:3.11-slim

# Metadata
LABEL maintainer="Tomas Vince <https://linkedin.com/in/tomasvince>"
LABEL description="ICO Collector Streamlit Web App"
LABEL version="2.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Create non-root user for security
RUN groupadd -r streamlit && useradd -r -g streamlit -s /bin/bash streamlit

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements_streamlit.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements_streamlit.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs && chown -R streamlit:streamlit /app

# Switch to non-root user
USER streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", \
           "--server.port=8501", \
           "--server.address=0.0.0.0", \
           "--server.enableCORS=false", \
           "--server.enableXsrfProtection=false"]