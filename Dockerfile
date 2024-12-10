FROM python:3.11.11-alpine@sha256:bc84eb94541f34a0e98535b130ea556ae85f6a431fdb3095762772eeb260ffc3

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
