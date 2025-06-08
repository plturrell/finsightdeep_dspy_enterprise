# Deploying DSPy to NVIDIA Blueprint

This guide explains how to deploy the DSPy API with SAP HANA Cloud integration to NVIDIA Blueprint, taking advantage of GPU acceleration for improved performance.

## Prerequisites

Before you begin, make sure you have:

1. An NVIDIA GPU Cloud (NGC) account with access to Blueprint
2. A SAP HANA Cloud instance set up and configured
3. Docker and Docker Compose installed locally for testing
4. The NVIDIA Blueprint CLI installed (`pip install nvidia-blueprint`)

## Step 1: Test Your Setup Locally

Before deploying to NVIDIA Blueprint, it's essential to test your setup locally:

```bash
# Start the local Docker environment
docker-compose -f docker-compose.local.yml up -d

# Test all API endpoints
./scripts/test_api_coverage.sh
```

If your local setup tests pass successfully, you're ready to deploy to NVIDIA Blueprint.

## Step 2: Configure Your Deployment

DSPy includes template files for NVIDIA Blueprint deployment. Start by creating your configuration file:

```bash
# Create your blueprint configuration from the template
cp blueprint.yaml.template blueprint.yaml
```

Edit the `blueprint.yaml` file to match your requirements:

```yaml
name: dspy-application
version: 1.0.0
description: DSPy application for language model programming

services:
  dspy-api:
    image: ${NVIDIA_NGC_REGISTRY}/dspy:latest
    resources:
      gpu:
        count: 1  # Adjust based on your workload
        type: A10  # Available GPU types: T4, A10, A100, etc.
    ports:
      - port: 8000
        target: 8000
    environment:
      # LLM Provider Configuration
      - NVIDIA_API_KEY=${NVIDIA_API_KEY}
      - NVIDIA_API_BASE=${NVIDIA_API_BASE}
      - DSPY_LM_PROVIDER=nvidia
      - DSPY_ENABLE_TENSOR_CORES=1
      
      # SAP HANA Cloud Vector Store Configuration
      - SAP_HANA_HOST=${SAP_HANA_HOST}
      - SAP_HANA_PORT=${SAP_HANA_PORT}
      - SAP_HANA_USER=${SAP_HANA_USER}
      - SAP_HANA_PASSWORD=${SAP_HANA_PASSWORD}
      - SAP_HANA_DATABASE=${SAP_HANA_DATABASE}
      - SAP_HANA_SCHEMA=${SAP_HANA_SCHEMA}
      - SAP_HANA_TABLE=${SAP_HANA_TABLE}
      - DSPY_VECTOR_STORE=sap_hana
```

## Step 3: Build and Push the Docker Image

Build your Docker image with GPU support and push it to the NVIDIA NGC registry:

```bash
# Log in to the NGC Registry
docker login nvcr.io

# Build the image with GPU support
docker build -t nvcr.io/YOUR_ORG/dspy:latest -f Dockerfile .

# Push the image to NGC Registry
docker push nvcr.io/YOUR_ORG/dspy:latest
```

Replace `YOUR_ORG` with your NGC organization name.

## Step 4: Deploy to NVIDIA Blueprint

Use the NVIDIA Blueprint CLI to deploy your application:

```bash
# Set required environment variables
export NVIDIA_API_KEY=your-api-key
export NVIDIA_API_BASE=https://api.nvidia.com/v1
export SAP_HANA_HOST=your-hana-host.hanatrial.ondemand.com
export SAP_HANA_PORT=443
export SAP_HANA_USER=your-hana-user
export SAP_HANA_PASSWORD=your-hana-password
export SAP_HANA_DATABASE=your-database
export SAP_HANA_SCHEMA=PUBLIC
export SAP_HANA_TABLE=VECTOR_STORE
export NVIDIA_NGC_REGISTRY=nvcr.io/YOUR_ORG

# Deploy to Blueprint
nvidia-blueprint deploy -f blueprint.yaml
```

The deployment process will output the URL where your DSPy API is accessible.

## Step 5: Verify the Deployment

After deployment completes, verify that your DSPy API is running correctly:

```bash
# Test the API status endpoint
curl https://your-blueprint-url.nvidia.com/api/v1/status

# Test the vector store status endpoint
curl https://your-blueprint-url.nvidia.com/api/v1/vectorstore/status
```

## Advanced Configuration

### Scaling Configuration

For production workloads, you may want to enable auto-scaling:

```yaml
scaling:
  minReplicas: 1
  maxReplicas: 3
  metrics:
    - type: Resource
      resource:
        name: cpu
        targetAverageUtilization: 70
    - type: Resource
      resource:
        name: memory
        targetAverageUtilization: 80
```

### Monitoring and Logging

Configure monitoring and logging for your deployment:

```yaml
observability:
  monitoring:
    enabled: true
  logging:
    level: INFO
    retention: 7d
```

### Security Configuration

Enhance security for your deployment:

```yaml
security:
  network_security:
    ingress_rules:
      - port: 443
        source: ["0.0.0.0/0"]
        protocol: tcp
      - port: 8000
        source: ["0.0.0.0/0"]
        protocol: tcp
  secrets:
    - name: SAP_HANA_PASSWORD
      description: "SAP HANA Cloud password"
      required: true
```

## Troubleshooting

### Connection Issues with SAP HANA Cloud

If you're experiencing connection issues with SAP HANA Cloud:

1. Verify that your SAP HANA Cloud instance is accessible from the internet
2. Check that your credentials are correct and have not expired
3. Ensure that your firewall rules allow connections from NVIDIA Blueprint IP ranges

### Performance Optimization

For optimal performance on NVIDIA GPUs:

1. Set `DSPY_ENABLE_TENSOR_CORES=1` to enable tensor core operations
2. Use the A10 or A100 GPU for best performance
3. Configure the appropriate memory settings based on your workload:
   ```
   PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
   ```

## Next Steps

- Set up CI/CD pipelines for automated deployment
- Implement monitoring and alerting
- Configure auto-scaling based on usage patterns