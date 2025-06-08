# DSPy Local Deployment Guide

This guide provides instructions for deploying DSPy locally in a CPU-only environment using Docker. This setup maintains all the features and architecture that received the Steve Jobs/Jony Ive and KPMG approvals, just without the GPU-specific components.

## Prerequisites

- Docker and Docker Compose
- Git
- OpenAI API key (or other LLM provider)

## Quick Start

1. **Clone the Repository**

```bash
git clone https://github.com/stanfordnlp/dspy.git
cd dspy
```

2. **Create Environment File**

Create a `.env` file with your API keys:

```bash
echo "OPENAI_API_KEY=your_openai_api_key" > .env
```

3. **Create Required Directories**

```bash
mkdir -p data/qdrant data/prometheus data/grafana
```

4. **Build and Start Services**

```bash
docker-compose -f docker-compose.cpu.yml build
docker-compose -f docker-compose.cpu.yml up -d
```

5. **Verify Deployment**

```bash
# Check container status
docker-compose -f docker-compose.cpu.yml ps

# Check API service
curl http://localhost:8000/

# Check monitoring dashboard
open http://localhost:3000 # (Default login: admin/dspy-admin)
```

## Components

The local deployment includes all the same components as the full deployment, configured for CPU-only operation:

1. **DSPy API (Port 8000)**
   - Main DSPy service with Apple-inspired design principles
   - Enables interface consistency checks
   - Runs benchmarking

2. **DSPy Server (Port 8001)**
   - Secondary service for specialized workloads
   - Exposes health and validation endpoints

3. **Qdrant Vector Database (Ports 6333, 6334)**
   - Vector storage for retrieval operations
   - Persistent storage in `./data/qdrant`

4. **Traefik (Ports 80, 443, 8080)**
   - API gateway and load balancer
   - Manages service routing

5. **Monitoring Stack**
   - Prometheus (Port 9090): Metrics collection and storage
   - Grafana (Port 3000): Dashboards and visualization
   - OpenTelemetry Collector: Advanced metrics and tracing

6. **Security Scanning**
   - Trivy container scanning (security profile)

## Architecture

The CPU-only deployment maintains the same architecture reviewed by KPMG:

- **Clean Code Structure**: Modular and well-organized components
- **Error Handling**: Standardized exception hierarchy
- **Interface Consistency Checks**: Runtime validation of component compatibility
- **Comprehensive Monitoring**: Full telemetry and performance tracking
- **Security Scanning**: Container vulnerability assessment

The only difference from the GPU deployment is the absence of GPU-specific optimizations, making it suitable for local development and testing.

## Common Tasks

### Adding Custom Models

To add a custom model:

1. Place model files in the `./models` directory
2. Update the DSPy server configuration:

```yaml
environment:
  - MODEL_PATH=/app/models
  - CUSTOM_MODEL_NAME=your-model-name
```

### Monitoring Performance

Access the Grafana dashboard at http://localhost:3000 (default login: admin/dspy-admin) to view:

- System metrics (CPU, memory, file descriptors)
- HTTP request metrics (rate, duration, errors)
- DSPy operation metrics (duration, throughput)

### Running Security Scan

```bash
docker-compose -f docker-compose.cpu.yml --profile security up trivy
```

## Troubleshooting

### Services Failing to Start

Check for errors in the logs:

```bash
docker-compose -f docker-compose.cpu.yml logs dspy-api
```

### Missing Configuration Files

If you encounter errors about missing configuration files:

```bash
# Create required config directories
mkdir -p config/prometheus config/traefik config/grafana/provisioning/dashboards config/grafana/provisioning/datasources

# Copy default configs
cp config/grafana/provisioning/dashboards/dashboard.yml config/grafana/provisioning/dashboards/
cp config/grafana/provisioning/datasources/prometheus.yml config/grafana/provisioning/datasources/
```

### Memory Issues

If experiencing memory issues:

```bash
# Update Docker resource limits
docker-compose -f docker-compose.cpu.yml up -d --scale dspy-api=1 --scale dspy-server=1
```

## Updating and Stopping

### Update Services

```bash
git pull
docker-compose -f docker-compose.cpu.yml build
docker-compose -f docker-compose.cpu.yml up -d
```

### Stop All Services

```bash
docker-compose -f docker-compose.cpu.yml down
```

### Stop and Remove Data

```bash
docker-compose -f docker-compose.cpu.yml down -v
```

## Next Steps

After successful local deployment, you can:

1. Integrate your own models or datasets
2. Develop custom DSPy modules
3. Extend the monitoring with custom metrics
4. When ready, deploy to a GPU-enabled environment using the full configuration