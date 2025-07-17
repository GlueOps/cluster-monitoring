FROM python:3.11.13-alpine@sha256:a25e12e5f7bd9ce4578bc87eadec231cc3aa7d6a03723601d3e6f82639969d3a

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
