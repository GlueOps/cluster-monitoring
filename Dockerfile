FROM python:3.12.2-alpine3.19@sha256:25a82f6f8b720a6a257d58e478a0a5517448006e010c85273f4d9c706819478c as final

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
