FROM python:3.12.8-slim

WORKDIR /app

# Install necessary OS dependencies for Playwright browsers
RUN apt-get update && apt-get install -y \
    wget \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-6 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    libgtk-3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libcups2 \
    libnss3 \
    libatk1.0-0 \
    libpangocairo-1.0-0 \
    libxshmfence1 \
    fonts-liberation \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and download browser binaries
RUN pip install playwright && playwright install --with-deps chromium

# Copy application code
COPY . /app

# Expose necessary ports
EXPOSE 11000 27017 8081