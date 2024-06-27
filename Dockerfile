FROM python:3.11.9-alpine@sha256:5745fa2b8591a756160721b8305adba3972fb26a9132789ed60160f21e55f5dc

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
