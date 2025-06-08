# DSPy Deployment Guide with SAP HANA Cloud Integration

This guide explains how to deploy DSPy with SAP HANA Cloud vector store integration using Docker and NVIDIA Blueprint.

## Prerequisites

- Docker and Docker Compose
- NVIDIA GPU (for GPU-accelerated deployment)
- SAP HANA Cloud account with database credentials
- NVIDIA API key (for NVIDIA Blueprint deployment)

## Local Development Testing

### 1. Configure Environment Variables

Copy the `.env.example` file to `.env` and update it with your SAP HANA Cloud credentials:

```bash
cp .env.example .env
```

Edit the `.env` file:

```bash
# SAP HANA Cloud Vector Store Configuration
SAP_HANA_HOST=d93a8739-44a8-4845-bef3-8ec724dea2ce.hana.prod-us10.hanacloud.ondemand.com
SAP_HANA_PORT=443
SAP_HANA_USER=DBADMIN
SAP_HANA_PASSWORD=Initial@1
SAP_HANA_DATABASE=SYSTEMDB
SAP_HANA_SCHEMA=PUBLIC
SAP_HANA_TABLE=VECTOR_STORE
DSPY_VECTOR_STORE=sap_hana
```

### 2. Test SAP HANA Cloud Connection

Test your connection to SAP HANA Cloud:

```bash
python scripts/test_sap_hana.py
```

### 3. Test API Endpoints Locally

Run the local mock API server:

```bash
python scripts/local_api_test.py
```

In a separate terminal, test the API endpoints:

```bash
# Test status endpoint
curl -s http://localhost:8000/api/v1/status | python -m json.tool

# Test vector store status
curl -s http://localhost:8000/api/v1/vectorstore/status | python -m json.tool

# Test vector store collections
curl -s http://localhost:8000/api/v1/vectorstore/collections | python -m json.tool

# Test vector store search
curl -s -X POST http://localhost:8000/api/v1/vectorstore/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test query","k":2}' | python -m json.tool
```

### 4. Run with Docker Compose

Start the Docker Compose environment:

```bash
docker-compose -f docker-compose.local.yml up -d
```

Test the Docker deployment:

```bash
./scripts/test_api_coverage.sh
```

## NVIDIA Blueprint Deployment

### 1. Using Docker Compose for Blueprint

The easiest way to deploy to NVIDIA Blueprint is using the provided Docker Compose file:

```bash
# Set up environment variables
export NVIDIA_API_KEY=your-nvidia-api-key
export NVIDIA_NGC_REGISTRY=nvcr.io/YOUR_ORG
export SAP_HANA_HOST=d93a8739-44a8-4845-bef3-8ec724dea2ce.hana.prod-us10.hanacloud.ondemand.com
export SAP_HANA_USER=DBADMIN
export SAP_HANA_PASSWORD=Initial@1

# Deploy using Docker Compose
docker-compose -f docker-compose.blueprint.yml up -d
```

### 2. Manual Build and Push (Alternative)

If you prefer to manually build and push the Docker image:

```bash
# Login to NGC Registry
docker login nvcr.io

# Build Docker image for NVIDIA Blueprint
docker build -t nvcr.io/YOUR_ORG/dspy:latest -f Dockerfile.blueprint .

# Push image to NGC
docker push nvcr.io/YOUR_ORG/dspy:latest
```

### 3. Configure NVIDIA Blueprint

```bash
# Export necessary variables
export NVIDIA_API_KEY=your-nvidia-api-key
export NVIDIA_NGC_REGISTRY=nvcr.io/YOUR_ORG

# Deploy to NVIDIA Blueprint
nvidia-blueprint deploy -f nvidia-blueprint-deploy.yaml
```

### 3. Verify Deployment

```bash
# Get the deployment URL from NVIDIA Blueprint console
export DEPLOYMENT_URL=your-deployment-url

# Test the status endpoint
curl -s $DEPLOYMENT_URL/api/v1/status | python -m json.tool

# Test the vector store status
curl -s $DEPLOYMENT_URL/api/v1/vectorstore/status | python -m json.tool
```

## Monitoring and Maintenance

### Check Logs

```bash
# For Docker Compose
docker-compose -f docker-compose.local.yml logs -f dspy-api

# For NVIDIA Blueprint
nvidia-blueprint logs -f dspy-sap-hana
```

### Update SAP HANA Cloud Credentials

If you need to update your SAP HANA Cloud credentials:

1. Update your `.env` file with the new credentials
2. Restart the Docker containers or redeploy to NVIDIA Blueprint

## Troubleshooting

### Connection Issues with SAP HANA Cloud

If you're having trouble connecting to SAP HANA Cloud:

1. Verify your credentials and host information
2. Check that your SAP HANA Cloud instance is running and accessible
3. Verify network connectivity and firewall settings

### GPU Issues

If you're experiencing GPU-related issues:

1. Check if CUDA is available: `docker exec dspy-api python -c "import torch; print(torch.cuda.is_available())"`
2. Verify NVIDIA driver installation: `nvidia-smi`
3. Ensure Docker is configured to use the NVIDIA runtime: `docker info | grep -i runtime`

## Additional Resources

- [DSPy Documentation](https://dspy.ai/)
- [SAP HANA Cloud Documentation](https://help.sap.com/docs/SAP_HANA_CLOUD)
- [NVIDIA Blueprint Documentation](https://docs.nvidia.com/datacenter/cloud-native/blueprint/index.html)