FROM python:3.13.3-alpine@sha256:a94caf6aab428e086bc398beaf64a6b7a0fad4589573462f52362fd760e64cc9

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
