FROM python:3.11.12-alpine@sha256:a648a482d0124da939ead54c5c6f0f6ce0b4ac925749c7d9ad3c2eba838966f1

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
