FROM python:3.11.13-alpine@sha256:9ce54d7ed458f71129c977478dd106cf6165a49b73fa38c217cc54de8f3e2bd0

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
