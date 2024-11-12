# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM mcr.microsoft.com/playwright:latest

RUN apt-get update && apt-get install -y python3-pip

ARG FUNCTION_DIR
ENV PYTHONPATH="${PYTHONPATH}:/funcion/playwright"
ENV PLAYWRIGHT_BROWSERS_PATH="/usr/local/share/playwright"

WORKDIR ${FUNCTION_DIR}

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY aws ${FUNCTION_DIR}

# Install the function's dependencies
RUN pip3 install awslambdaric playwright pypdf boto3 reportlab
RUN python3 -m playwright install chromium

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "lambda_function.handler" ]
