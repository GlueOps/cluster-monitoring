FROM python:3.12.10-alpine@sha256:4bbf5ef9ce4b273299d394de268ad6018e10a9375d7efc7c2ce9501a6eb6b86c

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY monitoring_script.py /app/
COPY serviceconfig.py /app/

CMD [ "python", "-u", "monitoring_script.py" ]
