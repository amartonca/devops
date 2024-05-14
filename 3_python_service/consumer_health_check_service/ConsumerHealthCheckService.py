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

# Disable Kafka logging
# kafka_logger = log.getLogger('kafka')
# kafka_logger.addHandler(log.NullHandler())
# kafka_logger.propagate = False

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
lock = threading.Lock()


def is_date_newer(date1, date2):
    try:
        return datetime.strptime(date1, '%Y-%m-%d %H:%M:%S') > datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        log.error("Error parsing dates. Ensure both dates are properly formatted.")
        return False


def update_health_checks():
    log.info("Starting health check consumer...")
    while True:
        consumer.poll(timeout_ms=10000)  # Adjust timeout as needed

        for message in consumer:
            data = message.value
            name = data['service_name']
            new_status = data['status']
            new_timestamp = data['timestamp']

            new_service_health_check = {
                'status': new_status,
                'timestamp': new_timestamp
            }

            with lock:
                if name not in latest_health_checks:
                    log.info(f"Adding new health check for service {name} with status {new_status}")
                    latest_health_checks[name] = new_service_health_check
                else:
                    current_health_check = latest_health_checks[name]
                    current_status = current_health_check['status']
                    current_timestamp = current_health_check['timestamp']

                    if new_status != current_status and is_date_newer(new_timestamp, current_timestamp):
                        log.info(f"Status change detected for {name}: {current_status} -> {new_status}")
                        latest_health_checks[name] = new_service_health_check
                    elif is_date_newer(new_timestamp, current_timestamp):
                        # log.debug(f"Timestamp update for {name} with unchanged status {new_status}")
                        latest_health_checks[name] = new_service_health_check


# Start the background thread for Kafka consumer
thread = threading.Thread(target=update_health_checks, daemon=True)
thread.start()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"service": "consumer-health-checker-service", "status": "healthy"}), 200


@app.route('/get_latest_health_check', methods=['GET'])
def check_health():
    with lock:
        if not latest_health_checks:
            return jsonify({"message": "No new health checks available"}), 200
        return jsonify(latest_health_checks), 200


if __name__ == '__main__':
    app.run(debug=bool(os.getenv('CONSUMER_HEALTHCHECK_SERVICE_DEBUG', False)), port=5001)
    log.info(f"Consumer Health check service started on port 5001")
