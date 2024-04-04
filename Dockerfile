FROM python:3.11.8-alpine@sha256:b6bd7d58b4e0f38cd151de9b96fffc9edf647bc6ba490ffe772d5d5eab11acda

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
