FROM python:3.11.9-alpine@sha256:0b5ed25d3cc27cd35c7b0352bac8ef2ebc8dd3da72a0c03caaf4eb15d9ec827a

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
