FROM python:3.14.9-alpine@sha256:d55673c233e28839c1c0c69766428cb6d50174a2ecfdcf915b6f58a0b0991562

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
