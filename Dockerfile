FROM python:3.11.10-alpine@sha256:f089154eb2546de825151b9340a60d39e2ba986ab17aaffca14301b0b961a11c

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
