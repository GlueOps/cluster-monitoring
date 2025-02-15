FROM python:3.11.11-alpine@sha256:1820d692a9da5adc7ff19fd4b4b2348ed1de83b47385785e05f6088d230345d8

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
