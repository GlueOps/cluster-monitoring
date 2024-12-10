FROM python:3.11.11-alpine@sha256:9ae1ab261b73eeaf88957c42744b8ec237faa8fa0d5be22a3ed697f52673b58a

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
