FROM python:3.15.2-alpine@sha256:2b4b04f31a4a009c1fadf7ce9338471f288488199cf43dcd1af71f244ea550aa

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
