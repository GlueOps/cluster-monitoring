FROM python:3.12.11-alpine@sha256:9b8808206f4a956130546a32cbdd8633bc973b19db2923b7298e6f90cc26db08

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
