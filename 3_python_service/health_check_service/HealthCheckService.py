from flask import Flask, jsonify, request
import logging as log
import os
from kafka import KafkaProducer
import json
from prometheus_flask_exporter import PrometheusMetrics

# Initialize Flask app
app = Flask(__name__)
metrics = PrometheusMetrics(app, path='/metrics')

# Static information as metric
metrics.info('app_info', 'Application info', version='1.0.3')

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


@app.route('/check_health', methods=['POST'])
def check_health():
    # Attempt to parse JSON from the request body
    try:
        message = request.get_json(force=True)
    except Exception as e:
        log.error(f"Error parsing JSON: {e}")
        return jsonify({"error": "Invalid JSON format"}), 400

    # Ensure all necessary fields are in the message
    if 'service_name' not in message or 'status' not in message or 'timestamp' not in message:
        return jsonify({"error": "Missing required fields"}), 400

    # Send the message to Kafka
    try:
        future = producer.send(topic, value=message)
        result = future.get(timeout=60)  # Specify an appropriate timeout
    except Exception as e:
        log.error(f"Error sending message to Kafka: {e}")
        return jsonify({"error": "Failed to send message"}), 500

    response_message = f"Message {message} sent to topic {result.topic} at offset {result.offset}"
    log.info(response_message)
    return jsonify({"message": response_message}), 200


if __name__ == '__main__':
    app.run(debug=bool(os.getenv('HEALTHCHECK_SERVICE_DEBUG', False)))

    log.info(f"Health check service started on port 5000")
