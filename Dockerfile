FROM python:3.12.10-alpine@sha256:9c51ecce261773a684c8345b2d4673700055c513b4d54bc0719337d3e4ee552e

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
