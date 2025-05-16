FROM python:3.11.11-alpine@sha256:d5e2fc72296647869f5eeb09e7741088a1841195059de842b05b94cb9d3771bb

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
