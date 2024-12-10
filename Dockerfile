FROM python:3.12.8-alpine@sha256:fd340d298d9d537a33c859f03bcc60e8e2542968e16f998bb0e232e25b4b23bd

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
