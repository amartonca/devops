FROM python:3.9-slim

RUN apt-get update && apt-get install -y curl

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY HealthCheckService.py app.py

ENV KAFKA_BOOTSTRAP_SERVERS = kafka-bootstrap-server:9094;
ENV KAFKA_TOPIC = health-checks-topic;
ENV HEALTHCHECK_SERVICE_DEBUG false;

ENV FLASK_APP=app.py

EXPOSE 5000

HEALTHCHECK \
    --interval=5s \
    --timeout=3s \
    --start-period=5s \
    --retries=3 \
    CMD curl --fail http://127.0.0.1:5000/health || exit 1

CMD [ "python3", "-m" , "flask", "run","--host=0.0.0.0", "--port=5000"]