from flask import Flask, jsonify
import logging as log
import os
import threading
from kafka import KafkaConsumer
import json

# Initialize Flask app
app = Flask(__name__)

log.basicConfig(level=log.INFO)

services = {}

# Kafka Consumer Setup
consumer = KafkaConsumer(
    os.getenv('KAFKA_TOPIC', 'health_checks_topic'),
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'my-cluster-kafka-bootstrap:9094').split(','),
    auto_offset_reset='earliest',
    group_id=os.getenv('KAFKA_GROUP_ID', 'health_checks_service'),  # Consumer group ID
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


def consume_messages():
    """Function to consume messages from Kafka and log them."""
    for message in consumer:
        data = message.value

        log.info(f"Health Check Update - Service: {data['service_name']}, Status: {data['status']}, Time: {data['timestamp']}")

        name = data['service_name']
        if name not in services.keys():
            services[name] = {
                'name': name,
                'status': data['status'],
                'timestamp': data['timestamp']
            }
            log.info(f"New service registered: {name}")
            continue

        if data['status'] != services[name]['status']:
            log.info(f"Service status changed: {name} - {data['status']}")

        services[name] = {
            'name': name,
            'status': data['status'],
            'timestamp': data['timestamp']
        }


# Run the Kafka consumer in a background thread
threading.Thread(target=consume_messages, daemon=True).start()


@app.route('/check_health', methods=['GET'])
def check_health():
    log.info("Manual health check triggered.")
    return jsonify(services)


if __name__ == '__main__':
    debug = os.getenv('HEALTHCHECK_SERVICE_DEBUG', True)
    port = os.getenv('HEALTHCHECK_SERVICE_PORT', 5000)

    app.run(debug=debug, port=port)

    log.info(f"Health check service started on port {port}")
