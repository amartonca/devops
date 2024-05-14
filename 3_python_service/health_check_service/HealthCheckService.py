from datetime import datetime

from flask import Flask, jsonify
import logging as log
import os
from kafka import KafkaProducer
import json

# Initialize Flask app
app = Flask(__name__)

log.basicConfig(level=log.INFO)

kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.49.2:32056').split(',')
topic = os.getenv('KAFKA_TOPIC', 'health-checks-topic')

# Kafka Producer Setup
producer = KafkaProducer(
    bootstrap_servers=kafka_servers,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)


@app.route('/health', methods=['GET'])
def health_check():
    # Here you can add checks to external services or databases
    return jsonify({"service": "health-checker-service", "status": "healthy"}), 200


@app.route('/check_health', methods=['GET'])
def check_health():
    message = {"service_name": "health-check-service", "status": "healthy", "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    # Send the message and wait for it to be acknowledged
    future = producer.send(topic, value=message)
    result = future.get(timeout=60)  # Specify an appropriate timeout

    response = f"Message {message} sent to topic {result.topic} at offset {result.offset}"

    log.info(response)
    return response, 200


if __name__ == '__main__':
    app.run(debug=bool(os.getenv('HEALTHCHECK_SERVICE_DEBUG', False)))

    log.info(f"Health check service started on port 5000")
