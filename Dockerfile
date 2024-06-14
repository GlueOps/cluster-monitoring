FROM python:3.11.9-alpine@sha256:e8effbb94ea2e5439c6b69c97c6455ff11fce94b7feaaed84bb0f2300d798cb7

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
