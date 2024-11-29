# Use AWS Lambda Python runtime as base image
FROM public.ecr.aws/lambda/python:3.12

# Copy Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright system dependencies manually with dnf
RUN dnf install -y \
    nss \
    atk \
    at-spi2-atk \
    cups-libs \
    dbus-libs \
    libX11 \
    libXcomposite \
    libXdamage \
    libXext \
    libXfixes \
    libXrandr \
    libxcb \
    libxkbcommon \
    mesa-libgbm \
    libdrm \
    alsa-lib \
    liberation-fonts \
    libXScrnSaver \
    xorg-x11-server-Xvfb \
    && dnf clean all

# Install Playwright and its browsers
RUN pip install --no-cache-dir playwright && \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright-browsers playwright install chromium

# Copy AWS Lambda function code
COPY aws/* ${LAMBDA_TASK_ROOT}

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright-browsers

# Define the Lambda handler
CMD ["lambda_function.handler"]
