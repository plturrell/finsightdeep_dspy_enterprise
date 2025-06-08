#!/usr/bin/env python
"""
Test script for verifying the local Docker setup for DSPy.

This script tests the basic functionality of the DSPy backend running in Docker.
It checks API connectivity and basic prediction functionality.
"""

import argparse
import json
import logging
import os
import requests
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "http://localhost:8000/api/v1"
MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds


def parse_args():
    parser = argparse.ArgumentParser(description="Test DSPy Docker local setup")
    parser.add_argument(
        "--url", 
        default=API_BASE_URL, 
        help=f"Base URL of the DSPy API (default: {API_BASE_URL})"
    )
    return parser.parse_args()


def test_api_status(base_url):
    """Test the API status endpoint."""
    url = f"{base_url}/api/v1/status"
    logger.info(f"Testing API status at {url}...")
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                logger.info("✅ API status check passed!")
                logger.info(f"   DSPy version: {data.get('version', 'unknown')}")
                return True
            else:
                logger.warning(f"API returned unexpected status: {data}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"API status check failed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            
        if attempt < MAX_RETRIES - 1:
            logger.info(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    
    logger.error("❌ API status check failed after all retries.")
    return False


def test_all_endpoints(base_url):
    """Test all key API endpoints."""
    endpoints = [
        # Core API endpoints
        {"url": f"{base_url}/api/v1/status", "method": "GET", "name": "Status API"},
        {"url": f"{base_url}/", "method": "GET", "name": "Web Interface"},
        {"url": f"{base_url}/dashboard", "method": "GET", "name": "Dashboard"},
        {"url": f"{base_url}/docs", "method": "GET", "name": "API Documentation"},
        {"url": f"{base_url}/openapi.json", "method": "GET", "name": "OpenAPI Schema"},
        
        # API endpoints with payload
        {"url": f"{base_url}/api/v1/predict", "method": "POST", "name": "Prediction API", 
         "payload": {"prompt": "What is DSPy?", "model": None, "options": {"provider": os.environ.get("DSPY_LM_PROVIDER", "nvidia")}}},
        {"url": f"{base_url}/api/v1/predict/stream", "method": "POST", "name": "Streaming API",
         "payload": {"prompt": "Hello", "model": None, "options": {"provider": os.environ.get("DSPY_LM_PROVIDER", "nvidia")}}},
         
        # Health check endpoints
        {"url": f"{base_url}/health", "method": "GET", "name": "Health Check"},
        
        # Advanced API endpoints
        {"url": f"{base_url}/api/v1/models", "method": "GET", "name": "Available Models"},
        {"url": f"{base_url}/api/v1/optimizers", "method": "GET", "name": "Available Optimizers"},
        {"url": f"{base_url}/api/v1/modules", "method": "GET", "name": "Available Modules"},
        
        # SAP HANA Vector Store endpoints
        {"url": f"{base_url}/api/v1/vectorstore/status", "method": "GET", "name": "Vector Store Status"},
        {"url": f"{base_url}/api/v1/vectorstore/collections", "method": "GET", "name": "Vector Store Collections"},
        {"url": f"{base_url}/api/v1/vectorstore/search", "method": "POST", "name": "Vector Store Search",
         "payload": {"query": "test query", "k": 2}}
    ]
    
    results = []
    
    for endpoint in endpoints:
        logger.info(f"Testing {endpoint['name']} at {endpoint['url']}...")
        
        for attempt in range(MAX_RETRIES):
            try:
                if endpoint["method"] == "GET":
                    response = requests.get(endpoint["url"], timeout=10)
                elif endpoint["method"] == "POST":
                    # Use payload if provided, otherwise empty JSON object
                    payload = endpoint.get("payload", {})
                    response = requests.post(endpoint["url"], json=payload, timeout=20)
                    
                    # For streaming endpoints, we need to handle the response differently
                    if "stream" in endpoint["url"] and response.status_code == 200:
                        # Just check headers for streaming response
                        if response.headers.get("content-type") == "text/event-stream":
                            logger.info(f"✅ {endpoint['name']} streaming response confirmed")
                            # Close the connection
                            response.close()
                
                if response.status_code < 400:  # Any 2xx or 3xx status is OK
                    logger.info(f"✅ {endpoint['name']} check passed with status code {response.status_code}")
                    
                    # Log response content for debugging (limited to first 500 chars)
                    content_preview = ""
                    try:
                        if response.headers.get("content-type") == "application/json":
                            content_preview = json.dumps(response.json(), indent=2)[:500]
                            if len(content_preview) >= 500:
                                content_preview += "... (truncated)"
                        elif response.headers.get("content-type") == "text/html":
                            content_preview = "HTML content received"
                        else:
                            content_preview = str(response.content)[:500]
                            if len(content_preview) >= 500:
                                content_preview += "... (truncated)"
                    except:
                        content_preview = "Failed to parse response content"
                        
                    logger.info(f"   Response preview: {content_preview}")
                    results.append(True)
                    break
                else:
                    logger.warning(f"{endpoint['name']} check failed with status code {response.status_code}")
                    if attempt == MAX_RETRIES - 1:
                        logger.error(f"❌ {endpoint['name']} check failed after all retries")
                        try:
                            logger.error(f"   Response: {response.text[:500]}")
                        except:
                            pass
                        results.append(False)
                        
            except requests.exceptions.RequestException as e:
                logger.warning(f"{endpoint['name']} check failed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"❌ {endpoint['name']} check failed after all retries")
                    results.append(False)
            
            if attempt < MAX_RETRIES - 1:
                logger.info(f"Retrying {endpoint['name']} in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
    
    if all(results):
        logger.info("✅ All API endpoints are healthy!")
        return True
    else:
        logger.error("❌ Some API endpoints failed health checks.")
        return False


def test_prediction(base_url):
    """Test a basic prediction."""
    url = f"{base_url}/predict"
    logger.info(f"Testing basic prediction at {url}...")
    
    try:
        data = {
            "prompt": "What is the capital of France?",
            "model": None,  # Use default model
            "options": {
                "provider": os.environ.get("DSPY_LM_PROVIDER", "nvidia")
            }
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        logger.info("✅ Basic prediction test passed!")
        logger.info(f"   Result: {json.dumps(result, indent=2)}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Basic prediction test failed: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"   Response: {e.response.text}")
        return False


def main():
    args = parse_args()
    
    logger.info("Starting DSPy Docker local setup tests...")
    logger.info(f"Using LM provider: {os.environ.get('DSPY_LM_PROVIDER', 'nvidia')}")
    
    # Run tests
    logger.info("=== Phase 1: Basic API Status Check ===")
    status_ok = test_api_status(args.url)
    
    if status_ok:
        logger.info("\n=== Phase 2: Testing All API Endpoints ===")
        endpoints_ok = test_all_endpoints(args.url)
        
        logger.info("\n=== Phase 3: Testing Prediction Functionality ===")
        prediction_ok = test_prediction(args.url)
    else:
        logger.error("Skipping endpoint and prediction tests as basic API status check failed.")
        endpoints_ok = False
        prediction_ok = False
    
    # Report overall result
    logger.info("\n=== Test Results Summary ===")
    logger.info(f"API Status Check: {'✅ PASSED' if status_ok else '❌ FAILED'}")
    logger.info(f"API Endpoints Check: {'✅ PASSED' if endpoints_ok else '❌ FAILED'}")
    logger.info(f"Prediction Functionality: {'✅ PASSED' if prediction_ok else '❌ FAILED'}")
    
    if status_ok and endpoints_ok and prediction_ok:
        logger.info(f"\n✅ All tests passed! The DSPy Docker local setup is working correctly.")
        logger.info(f"   Provider: {os.environ.get('DSPY_LM_PROVIDER', 'nvidia')}")
        logger.info(f"   API URL: {args.url}")
        return 0
    else:
        logger.error("\n❌ Some tests failed. Please check the logs for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())