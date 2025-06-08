#!/usr/bin/env python
"""
Local API testing script for DSPy with SAP HANA Cloud integration.

This script creates a simple FastAPI server that mocks the DSPy API
for testing purposes without requiring the full Docker setup.
"""

import argparse
import json
import logging
import os
import sys
import time
import uuid
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    logger.error("FastAPI or dependencies not installed. Run: pip install fastapi uvicorn pydantic")
    HAS_FASTAPI = False

def create_mock_app():
    """Create a mock DSPy API server for testing."""
    app = FastAPI(title="DSPy Mock API")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Define API models
    class PredictionRequest(BaseModel):
        prompt: str
        model: Optional[str] = None
        options: Dict[str, Any] = {}
    
    class VectorSearchRequest(BaseModel):
        query: str
        k: int = 2
        filter_dict: Optional[Dict[str, Any]] = None
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {"message": "DSPy Mock API is running"}
    
    # Health check endpoint
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    # API status endpoint
    @app.get("/api/v1/status")
    async def status():
        return {
            "status": "ok",
            "version": "2.6.28",
            "auth_enabled": False,
        }
    
    # Prediction endpoint
    @app.post("/api/v1/predict")
    async def predict(request: PredictionRequest):
        provider = request.options.get("provider", "nvidia")
        return {
            "result": {
                "question": request.prompt,
                "answer": f"This is a mock answer using the {provider} provider."
            },
            "model": request.model or "mock-model",
            "latency": 0.5,
        }
    
    # Streaming endpoint
    @app.post("/api/v1/predict/stream")
    async def predict_stream(request: PredictionRequest):
        return JSONResponse({
            "status": "streaming_not_available_in_mock",
            "message": "Streaming is not available in the mock API"
        })
    
    # Models endpoint
    @app.get("/api/v1/models")
    async def models():
        return {
            "models": [
                {"id": "nvidia/model1", "name": "NVIDIA Model 1"},
                {"id": "sap/model1", "name": "SAP Model 1"},
            ]
        }
    
    # Optimizers endpoint
    @app.get("/api/v1/optimizers")
    async def optimizers():
        return {
            "optimizers": [
                {"id": "bootstrap", "name": "Bootstrap Few-Shot"},
                {"id": "simba", "name": "SIMBA"},
            ]
        }
    
    # Modules endpoint
    @app.get("/api/v1/modules")
    async def modules():
        return {
            "modules": [
                {"id": "chain_of_thought", "name": "Chain of Thought"},
                {"id": "react", "name": "ReAct"},
            ]
        }
    
    # Vector store status endpoint
    @app.get("/api/v1/vectorstore/status")
    async def vector_store_status():
        # Simulate SAP HANA connection based on environment variables
        if os.environ.get("SAP_HANA_HOST"):
            return {
                "status": "connected",
                "type": "sap_hana",
                "connection_ok": True,
                "host": os.environ.get("SAP_HANA_HOST", "mock-hana-host"),
                "schema": os.environ.get("SAP_HANA_SCHEMA", "PUBLIC"),
                "table": os.environ.get("SAP_HANA_TABLE", "VECTOR_STORE"),
                "message": "Connected to SAP HANA Cloud (mocked)"
            }
        else:
            return {
                "status": "not_configured",
                "message": "SAP HANA Cloud connection not configured"
            }
    
    # Vector store collections endpoint
    @app.get("/api/v1/vectorstore/collections")
    async def vector_store_collections():
        # For SAP HANA, collections are tables
        return [
            {
                "name": os.environ.get("SAP_HANA_TABLE", "VECTOR_STORE"),
                "document_count": 100,  # Mock document count
                "dimension": 1536  # Default dimension for OpenAI embeddings
            }
        ]
    
    # Vector store search endpoint
    @app.post("/api/v1/vectorstore/search")
    async def vector_store_search(request: VectorSearchRequest):
        time.sleep(0.2)  # Simulate search time
        
        # Generate mock results
        results = []
        for i in range(min(request.k, 5)):  # At most 5 mock results
            results.append({
                "id": f"doc{i+1}",
                "text": f"This is a mock document {i+1} matching query: {request.query}",
                "metadata": {"source": "mock", "index": i},
                "score": 0.9 - (i * 0.1)  # Descending scores
            })
        
        return {
            "results": results,
            "latency": 0.2
        }
    
    # OpenAPI schema
    @app.get("/openapi.json")
    async def openapi_schema():
        return app.openapi()
    
    return app

def parse_args():
    parser = argparse.ArgumentParser(description="Run a mock DSPy API server for testing")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to run the server on (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run API tests after starting the server"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    if not HAS_FASTAPI:
        logger.error("FastAPI is required but not installed.")
        return 1
    
    app = create_mock_app()
    
    if args.test:
        # Start the server in a separate process
        import subprocess
        import time
        
        server_process = subprocess.Popen(
            [sys.executable, __file__, "--host", args.host, "--port", str(args.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        logger.info(f"Started mock API server on http://{args.host}:{args.port}")
        logger.info("Waiting for server to initialize...")
        time.sleep(3)
        
        # Run the test script
        logger.info("Running API endpoint tests...")
        try:
            test_script = os.path.join(os.path.dirname(__file__), "test_api_coverage.sh")
            test_process = subprocess.run([test_script], check=True)
            
            if test_process.returncode == 0:
                logger.info("✅ All API endpoint tests passed!")
            else:
                logger.error("❌ Some API endpoint tests failed.")
                
            # Kill the server process
            server_process.terminate()
            server_process.wait()
            
            return test_process.returncode
        except subprocess.CalledProcessError as e:
            logger.error(f"Test script failed with exit code {e.returncode}")
            server_process.terminate()
            server_process.wait()
            return e.returncode
    else:
        # Run the server directly
        logger.info(f"Starting mock API server on http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
        return 0

if __name__ == "__main__":
    sys.exit(main())