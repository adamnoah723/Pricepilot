FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Selenium (with architecture detection)
RUN apt-get update && \
    if [ "$(uname -m)" = "x86_64" ]; then \
        # Fetch Google's public key and dearmor it into a keyring file so apt can
        # reference it with 'signed-by'. This avoids using the deprecated 'apt-key'
        # and works on slim images where apt-key may be missing.
        wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-linux-signing-keyring.gpg && \
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
        apt-get update && \
        apt-get install -y google-chrome-stable; \
    else \
        apt-get install -y chromium chromium-driver; \
    fi && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]