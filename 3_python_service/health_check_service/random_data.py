import requests
import random
from datetime import datetime

# Define the endpoint URL
url = 'http://192.168.49.2:32324/check_health'

# Define the list of service names
services = [
    "database-service",
    "user-auth-service",
    "email-service",
    "payment-gateway-service",
    "inventory-service"
]


# Function to send health check data
def send_health_check():
    for i in range(10000):
        for service in services:
            # Randomly choose the status
            status = random.choice(['UP', 'DOWN'])

            # Prepare the message
            message = {
                "service_name": service,
                "status": status,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Send POST request to the endpoint
            try:
                response = requests.post(url, json=message)
                print(f"Response from server for {service}: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to send request for {service}: {e}")


# Run the function to send health checks
send_health_check()
