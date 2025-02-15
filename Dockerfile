FROM python:3.12.9-alpine@sha256:203f7ed10d733d22188aa76391690f2142cef83094490cc37384cedacdcd652d

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
