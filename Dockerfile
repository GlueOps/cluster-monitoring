FROM python:3.12.8-alpine@sha256:b0fc5cb1a4ae39af99c0ddf4b56cb06e8f867dce47fa9a8553f8601e527596b4

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
