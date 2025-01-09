FROM python:3.11.11-alpine@sha256:9af3561825050da182afc74b106388af570b99c500a69c8216263aa245a2001b

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
