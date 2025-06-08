#!/usr/bin/env python
"""
Simple script to test DSPy API endpoints structure.
"""

import json
import logging
import sys
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    """Print all expected endpoints for the DSPy API."""
    base_url = "http://localhost:8000"
    
    # Core API endpoints
    core_endpoints = [
        {"method": "GET", "path": "/api/v1/status", "description": "Check API status"},
        {"method": "POST", "path": "/api/v1/predict", "description": "Run prediction"},
        {"method": "POST", "path": "/api/v1/predict/stream", "description": "Run streaming prediction"},
        {"method": "GET", "path": "/api/v1/models", "description": "List available models"},
        {"method": "GET", "path": "/api/v1/optimizers", "description": "List available optimizers"},
        {"method": "GET", "path": "/api/v1/modules", "description": "List available modules"},
    ]
    
    # Web interface endpoints
    web_endpoints = [
        {"method": "GET", "path": "/", "description": "Web interface root"},
        {"method": "GET", "path": "/dashboard", "description": "Dashboard"},
        {"method": "GET", "path": "/docs", "description": "API documentation"},
        {"method": "GET", "path": "/openapi.json", "description": "OpenAPI schema"},
        {"method": "GET", "path": "/health", "description": "Health check"},
    ]
    
    # Vector store API endpoints
    vector_endpoints = [
        {"method": "GET", "path": "/api/v1/vectorstore/status", "description": "Vector store status"},
        {"method": "GET", "path": "/api/v1/vectorstore/collections", "description": "List vector store collections"},
        {"method": "POST", "path": "/api/v1/vectorstore/search", "description": "Search vector store"},
    ]
    
    # Print endpoint information
    print("\nDSPy API Endpoints Structure")
    print("===========================\n")
    
    print("Core API Endpoints:")
    print("-----------------")
    for ep in core_endpoints:
        print(f"{ep['method']:5} {urljoin(base_url, ep['path']):40} {ep['description']}")
    
    print("\nWeb Interface Endpoints:")
    print("----------------------")
    for ep in web_endpoints:
        print(f"{ep['method']:5} {urljoin(base_url, ep['path']):40} {ep['description']}")
    
    print("\nVector Store API Endpoints:")
    print("-------------------------")
    for ep in vector_endpoints:
        print(f"{ep['method']:5} {urljoin(base_url, ep['path']):40} {ep['description']}")
    
    # Print environment variable information
    print("\nRequired Environment Variables for SAP HANA Cloud:")
    print("----------------------------------------------")
    print("SAP_HANA_HOST                 SAP HANA Cloud host URL")
    print("SAP_HANA_PORT                 SAP HANA Cloud port (default: 443)")
    print("SAP_HANA_USER                 SAP HANA Cloud username")
    print("SAP_HANA_PASSWORD             SAP HANA Cloud password")
    print("SAP_HANA_DATABASE             SAP HANA Cloud database name")
    print("SAP_HANA_SCHEMA               SAP HANA Cloud schema (default: PUBLIC)")
    print("SAP_HANA_TABLE                SAP HANA Cloud table (default: VECTOR_STORE)")
    print("DSPY_VECTOR_STORE             Set to 'sap_hana' to enable SAP HANA Cloud")
    
    # Print test commands
    print("\nTesting Commands:")
    print("---------------")
    print("1. Run the local mock API server:")
    print("   python scripts/local_api_test.py")
    print()
    print("2. Test endpoints with curl:")
    print("   curl -s http://localhost:8000/api/v1/status | jq")
    print("   curl -s http://localhost:8000/api/v1/vectorstore/status | jq")
    print()
    print("3. Run Docker-based tests:")
    print("   docker-compose -f docker-compose.local.yml up -d")
    print("   ./scripts/test_api_coverage.sh")
    print()
    print("4. Test SAP HANA Cloud connection:")
    print("   python scripts/test_sap_hana.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())