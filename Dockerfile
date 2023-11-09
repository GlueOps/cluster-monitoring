# --- Stage 1: Testing ---
# Use the same base image for consistency
FROM python:3.11.6-alpine3.18 as tester

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install pytest

# Copy your application code and test files
COPY monitoring_script.py /app/
COPY test_monitoring_script.py /app/

# Run tests
RUN python -u -m pytest -v test_monitoring_script.py

# --- Stage 2: Final Image ---
FROM python:3.11.6-alpine3.18 as final

WORKDIR /app
COPY --from=tester /app/requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy only the necessary files from the tester stage
COPY --from=tester /app/monitoring_script.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
