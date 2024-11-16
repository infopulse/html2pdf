FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libasound2 \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG FUNCTION_DIR="/function"
ENV PYTHONPATH="${PYTHONPATH}:/funcion/playwright"
ENV PLAYWRIGHT_BROWSERS_PATH="/usr/local/share/playwright"
ENV PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox  --disable-dev-shm-usage"

RUN mkdir -p ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}

RUN pip install --no-cache-dir playwright awslambdaric playwright pypdf boto3 reportlab
RUN playwright install chromium
RUN chmod -R 777 /usr/local/share/playwright

COPY aws ${FUNCTION_DIR}

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "lambda_function.handler" ]
