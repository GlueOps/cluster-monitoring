FROM python:3.14.2-alpine@sha256:2a77c2640cc80f5506babd027c883abc55f04d44173fd52eeacea9d3b978e811

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
