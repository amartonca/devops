# Deployment Automation

Create Kubernetes deployment manifests for both the HealthCheckService and ConsumerHealthCheckService.
Implement a rolling deployment strategy for these services.

Use ConfigMaps/Secrets to manage any configuration that needs to be externalized. Ensure that the services can
scale horizontally.

## How

1. For this task, I'll leverage on helm charts for easier management. I created the chart
   with `helm create HealthCheckService` and modified it, so it supports both services.

I configured the helm chart to take the image and port as inputs.

2. Next I had to set up the environment variables for the containers in the configmap since i didn't have any secrets
   yet.

To test that the chart is valid, i used helm template:

```bash
helm template \
    -f values.yaml \
    -f values-producer.yaml \
    --set image.name=producer \
    --set service.port=5000 \
    --set configmap.data.KAFKA_BOOTSTRAP_SERVERS=some-server \
    --set configmap.data.KAFKA_TOPIC=some-topic \
    .
```

![img.png](img.png)

# Documentation

