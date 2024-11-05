# Use the official Python image from the Docker Hub
FROM python:3.12-slim

RUN pip install --no-cache-dir awslambdaric

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl\
    wget \
    gnupg \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libxkbcommon0 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libasound2 \
    libxshmfence1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libdrm2 \
    libxfixes3 \
    libxext6 \
    libxrender1 \
    libdbus-1-3 \
    libxtst6 \
    libxss1 \
    libgtk-3-0 \
    libxshmfence1 \
    libnss3 \
    libnspr4 \
    libgbm1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install playwright pypdf boto3
RUN playwright install chromium

COPY . /var/task

CMD ["python3", "-m", "awslambdaric", "lambda_function.lambda_handler"]