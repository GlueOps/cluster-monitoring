FROM python:3.14.0-alpine@sha256:9c32c2f24d00536cac7d4d356d82c5274fb17366c52aa59ed0cc4c06f8b60a35

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
