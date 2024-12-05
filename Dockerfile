FROM python:3.12.8-alpine@sha256:bb94273467caf397de28b4e6dd09ca4a2dd1b53fa9b130d5b2c7c82719258356

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
