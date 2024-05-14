# Deployment Automation

Create Kubernetes deployment manifests for both the HealthCheckService and ConsumerHealthCheckService.
Implement a rolling deployment strategy for these services.

Use ConfigMaps/Secrets to manage any configuration that needs to be externalized. Ensure that the services can
scale horizontally.

## How

1. For this task, I'll leverage on helm charts for easier management. I created the chart
   with `helm create HealthCheckService` and modified it, so it supports both services.

I configured the helm chart to take the image and port as inputs.

# Documentation

