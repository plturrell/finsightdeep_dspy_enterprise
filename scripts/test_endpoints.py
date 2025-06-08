#!/usr/bin/env python
"""
Script to test API endpoints in the DSPy Docker setup.
This script can be run without actually starting the Docker containers.
"""

import argparse
import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Test DSPy API endpoints configuration")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000", 
        help="Base URL of the DSPy API (default: http://localhost:8000)"
    )
    return parser.parse_args()

def list_all_endpoints(base_url):
    """List all expected endpoints in the DSPy API."""
    endpoints = [
        # Core API endpoints
        {"url": f"{base_url}/api/v1/status", "method": "GET", "name": "Status API", "description": "Check API status and version"},
        {"url": f"{base_url}/api/v1/predict", "method": "POST", "name": "Prediction API", "description": "Run a prediction with a DSPy program"},
        {"url": f"{base_url}/api/v1/predict/stream", "method": "POST", "name": "Streaming Prediction API", "description": "Run a prediction with streaming response"},
        
        # Web interface endpoints
        {"url": f"{base_url}/", "method": "GET", "name": "Web Interface", "description": "Main web interface"},
        {"url": f"{base_url}/dashboard", "method": "GET", "name": "Dashboard", "description": "DSPy dashboard"},
        {"url": f"{base_url}/docs", "method": "GET", "name": "API Documentation", "description": "Interactive API documentation"},
        {"url": f"{base_url}/openapi.json", "method": "GET", "name": "OpenAPI Schema", "description": "OpenAPI schema for the API"},
        {"url": f"{base_url}/health", "method": "GET", "name": "Health Check", "description": "Health check endpoint"},
        
        # Advanced API endpoints
        {"url": f"{base_url}/api/v1/models", "method": "GET", "name": "Available Models", "description": "List available language models"},
        {"url": f"{base_url}/api/v1/optimizers", "method": "GET", "name": "Available Optimizers", "description": "List available DSPy optimizers"},
        {"url": f"{base_url}/api/v1/modules", "method": "GET", "name": "Available Modules", "description": "List available DSPy modules"},
        
        # SAP HANA Vector Store endpoints
        {"url": f"{base_url}/api/v1/vectorstore/status", "method": "GET", "name": "Vector Store Status", "description": "Check SAP HANA Cloud connection status"},
        {"url": f"{base_url}/api/v1/vectorstore/collections", "method": "GET", "name": "Vector Store Collections", "description": "List vector collections in SAP HANA Cloud"},
        {"url": f"{base_url}/api/v1/vectorstore/search", "method": "POST", "name": "Vector Store Search", "description": "Search for similar vectors in SAP HANA Cloud"}
    ]
    
    # Print endpoint table
    print("\nAvailable API Endpoints:\n")
    print(f"{'Endpoint':<40} {'Method':<8} {'Description':<50}")
    print(f"{'-'*40} {'-'*8} {'-'*50}")
    
    for endpoint in endpoints:
        print(f"{endpoint['url']:<40} {endpoint['method']:<8} {endpoint['description']:<50}")
    
    return endpoints

def main():
    args = parse_args()
    
    logger.info("DSPy API Endpoints Configuration")
    logger.info(f"Base URL: {args.url}")
    
    endpoints = list_all_endpoints(args.url)
    
    logger.info("\nEndpoint validation instructions:")
    logger.info("1. Start the Docker environment:")
    logger.info("   docker-compose -f docker-compose.local.yml up -d")
    logger.info("2. Run the test script to validate all endpoints:")
    logger.info("   python scripts/test_docker_local.py")
    logger.info("3. For manual testing, you can access these endpoints directly")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())