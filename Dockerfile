FROM python:3.11.11-alpine@sha256:fbcb089a803d5673f225dc923b8e29ecc7945e9335465037b6961107b9da3d61

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
