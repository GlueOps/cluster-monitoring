FROM python:3.14.0-alpine@sha256:e1a567200b6d518567cc48994d3ab4f51ca54ff7f6ab0f3dc74ac5c762db0800

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
