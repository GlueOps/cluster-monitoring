FROM python:3.11.13-alpine@sha256:8068890a42d68ece5b62455ef327253249b5f094dcdee57f492635a40217f6a3

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
