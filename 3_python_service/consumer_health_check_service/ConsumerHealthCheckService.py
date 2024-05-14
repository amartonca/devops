from datetime import datetime
import threading
from flask import Flask, jsonify
import logging as log
import os
from kafka import KafkaConsumer
import json

# Initialize Flask app
app = Flask(__name__)

# Initialize logging
log.basicConfig(level=log.INFO)

# Environment variables or default values
kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.49.2:32056').split(',')
topic = os.getenv('KAFKA_TOPIC', 'health-checks-topic')
group_id = os.getenv('KAFKA_CONSUMER_GROUP_ID', 'health-checks-group')

# Kafka Consumer Setup
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=kafka_servers,
    auto_offset_reset='earliest',
    enable_auto_commit=False,
    group_id=group_id,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Dictionary to store the latest health check per service
latest_health_checks = {}


def update_health_checks():
    log.info("Starting health check consumer...")
    while True:
        consumer.poll(timeout_ms=10000)  # Adjust timeout as needed

        for message in consumer:
            data = message.value

            name = data['service_name']
            status = data['status']

            new_service_health_check = {
                'status': status,
                'timestamp': data['timestamp']
            }

            if name not in latest_health_checks.keys():
                log.info(f"Adding new health check for service {name} with status {status}")

            latest_health_checks[name] = new_service_health_check

            if status != latest_health_checks.get(name)['status']:
                log.info(f"Updating health check for service {name} from {latest_health_checks.get(name)['status']} to {status}")


# Start the background thread for Kafka consumer
thread = threading.Thread(target=update_health_checks, daemon=True)
thread.start()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"service": "consumer-health-checker-service", "status": "healthy"}), 200


@app.route('/get_latest_health_check', methods=['GET'])
def check_health():
    if not latest_health_checks:
        return jsonify({"message": "No new health checks available"}), 200
    return jsonify(latest_health_checks), 200


if __name__ == '__main__':
    app.run(debug=bool(os.getenv('CONSUMER_HEALTHCHECK_SERVICE_DEBUG', False)), port=5001)
    log.info(f"Consumer Health check service started on port 5001")
