from flask import Flask, jsonify
import logging as log
import os

# Initialize Flask app
app = Flask(__name__)

log.basicConfig(level=log.INFO)


@app.route('/check_health', methods=['GET'])
def check_health():
    log.info("Manual health check triggered.")
    return jsonify({"message": "Manual health check log triggered"}), 200


if __name__ == '__main__':
    debug = os.getenv('HEALTHCHECK_SERVICE_DEBUG', True)
    port = os.getenv('HEALTHCHECK_SERVICE_PORT', 5000)

    app.run(debug=debug, port=port)

    log.info(f"Health check service started on port {port}")
