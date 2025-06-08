"""
Server module for DSPy frontend.

This module provides FastAPI server implementation for the DSPy frontend,
including API endpoints and web interface.
"""

import importlib.util
import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Union

from dspy.frontend.config import FrontendConfig

logger = logging.getLogger(__name__)

# Check if required packages are available
try:
    import fastapi
    from fastapi import FastAPI, HTTPException, Depends, Request, status
    from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    logger.warning("FastAPI is not installed. Install with 'pip install fastapi uvicorn jinja2'.")

try:
    import pydantic
    from pydantic import BaseModel, Field
    
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    logger.warning("Pydantic is not installed. Install with 'pip install pydantic'.")

# Optional vector store API support
try:
    from dspy.frontend.api import vector_store_router
    HAS_VECTOR_STORE_API = True
except ImportError:
    HAS_VECTOR_STORE_API = False
    logger.warning("Vector store API module not found. Vector store endpoints will not be available.")


def create_app(config: Optional[FrontendConfig] = None) -> Any:
    """
    Create a FastAPI application for the DSPy frontend.
    
    Args:
        config: Frontend configuration
        
    Returns:
        FastAPI application
    """
    if not HAS_FASTAPI or not HAS_PYDANTIC:
        raise ImportError(
            "FastAPI and Pydantic are required. "
            "Install with 'pip install fastapi uvicorn jinja2 pydantic'"
        )
    
    if config is None:
        config = FrontendConfig()
    
    # Create FastAPI app
    app = FastAPI(
        title="DSPy Frontend",
        description="Web frontend and API for DSPy",
        version="1.0.0",
    )
    
    # Setup CORS if enabled
    if config.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    # Include vector store router if available
    if HAS_VECTOR_STORE_API:
        try:
            app.include_router(vector_store_router)
            logger.info("Vector store API endpoints registered")
        except Exception as e:
            logger.error(f"Failed to register vector store API endpoints: {e}")
    
    # Setup static files if folder exists
    static_path = os.path.join(os.path.dirname(__file__), config.static_folder)
    if os.path.exists(static_path) and os.path.isdir(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Setup templates if folder exists
    template_path = os.path.join(os.path.dirname(__file__), config.template_folder)
    templates = None
    if os.path.exists(template_path) and os.path.isdir(template_path):
        templates = Jinja2Templates(directory=template_path)
    
    # Authentication dependency if enabled
    auth_dependency = []
    if config.enable_auth:
        try:
            import jwt
            from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
            
            auth_scheme = HTTPBearer()
            
            async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
                try:
                    payload = jwt.decode(
                        credentials.credentials,
                        config.jwt_secret,
                        algorithms=["HS256"]
                    )
                    return payload
                except jwt.PyJWTError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            
            auth_dependency = [Depends(get_current_user)]
        except ImportError:
            logger.warning("PyJWT is not installed. Install with 'pip install pyjwt'.")
            config.enable_auth = False
    
    # Define API models
    class PredictionRequest(BaseModel):
        prompt: str
        model: Optional[str] = None
        options: Dict[str, Any] = Field(default_factory=dict)
    
    class PredictionResponse(BaseModel):
        result: Any
        model: str
        latency: float
    
    # API endpoints
    api_prefix = config.get_full_api_prefix()
    
    @app.get(f"{api_prefix}/status")
    async def get_status():
        """Check if the API is running."""
        try:
            import dspy
            return {
                "status": "ok",
                "version": getattr(dspy, "__version__", "unknown"),
                "auth_enabled": config.enable_auth,
            }
        except Exception as e:
            logger.error(f"Error in status endpoint: {e}")
            return {"status": "error", "message": str(e)}
    
    @app.post(f"{api_prefix}/predict", response_model=PredictionResponse, dependencies=auth_dependency)
    async def predict(request: PredictionRequest):
        """Run a prediction with a DSPy program."""
        try:
            import dspy
            import time
            
            # Get or create model
            model_name = request.model or "default"
            
            # Run prediction
            start_time = time.time()
            
            # This is a simplified example - in a real implementation, 
            # you would use a registered DSPy program
            program = dspy.ChainOfThought("question -> answer")
            result = program(question=request.prompt)
            
            latency = time.time() - start_time
            
            return {
                "result": result.toDict(),
                "model": model_name,
                "latency": latency,
            }
        except Exception as e:
            logger.error(f"Error in predict endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post(f"{api_prefix}/predict/stream", dependencies=auth_dependency)
    async def predict_stream(request: PredictionRequest):
        """Run a prediction with streaming response."""
        try:
            import dspy
            import ujson
            import asyncio
            
            # This is a simplified example - in a real implementation,
            # you would use a registered DSPy program with streamify
            program = dspy.streamify(dspy.ChainOfThought("question -> answer"))
            
            async def generate():
                try:
                    async for value in program(question=request.prompt):
                        if isinstance(value, dspy.Prediction):
                            data = {"prediction": value.toDict()}
                            yield f"data: {ujson.dumps(data)}\n\n"
                        else:
                            data = {"chunk": str(value)}
                            yield f"data: {ujson.dumps(data)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"Error in stream generation: {e}")
                    error_data = {"error": str(e)}
                    yield f"data: {ujson.dumps(error_data)}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        except Exception as e:
            logger.error(f"Error in predict_stream endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Web interface routes
    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Render the main page."""
        if templates is None:
            return HTMLResponse(content=get_default_index_html())
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Render the dashboard page."""
        if templates is None:
            return HTMLResponse(content="<h1>Dashboard</h1><p>Templates not configured.</p>")
        return templates.TemplateResponse("dashboard.html", {"request": request})
    
    return app


def start_server(app: Any = None, config: Optional[FrontendConfig] = None) -> None:
    """
    Start the FastAPI server.
    
    Args:
        app: FastAPI application (created if None)
        config: Frontend configuration
    """
    if not HAS_FASTAPI:
        raise ImportError("FastAPI is not installed. Install with 'pip install fastapi uvicorn'")
    
    if config is None:
        config = FrontendConfig()
    
    if app is None:
        app = create_app(config)
    
    try:
        import uvicorn
        logger.info(f"Starting DSPy frontend server at http://{config.host}:{config.port}")
        uvicorn.run(app, host=config.host, port=config.port, log_level="info")
    except ImportError:
        logger.error("Uvicorn is not installed. Install with 'pip install uvicorn'")
    except Exception as e:
        logger.error(f"Error starting server: {e}")


def get_default_index_html() -> str:
    """Get default HTML for the index page when templates are not configured."""
    return """<!DOCTYPE html>
<html>
<head>
    <title>DSPy Frontend</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
        }
        .card {
            border: 1px solid #eaeaea;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .button {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            text-decoration: none;
            margin-right: 10px;
        }
        code {
            background-color: #f8f8f8;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: monospace;
        }
        #status {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>DSPy Frontend</h1>
    <div class="card">
        <h2>Status</h2>
        <p>API Status: <span id="status">Checking...</span></p>
        <p>Version: <span id="version">Unknown</span></p>
    </div>
    
    <div class="card">
        <h2>Try It Out</h2>
        <p>Enter a question to test the DSPy chain of thought:</p>
        <textarea id="prompt" rows="3" style="width: 100%; margin-bottom: 10px;" placeholder="What is the capital of France?"></textarea>
        <button class="button" onclick="runPrediction()">Run Prediction</button>
        <button class="button" onclick="runStreamingPrediction()">Run with Streaming</button>
        
        <h3>Result:</h3>
        <pre id="result" style="background-color: #f8f8f8; padding: 10px; border-radius: 5px; white-space: pre-wrap;">Results will appear here</pre>
    </div>
    
    <div class="card">
        <h2>API Documentation</h2>
        <p>Access the API docs at <a href="/docs">/docs</a></p>
        <p>Example API endpoints:</p>
        <ul>
            <li><code>GET /api/v1/status</code> - Check API status</li>
            <li><code>POST /api/v1/predict</code> - Run a prediction</li>
            <li><code>POST /api/v1/predict/stream</code> - Run a streaming prediction</li>
        </ul>
    </div>
    
    <script>
        // Check API status on page load
        fetch('/api/v1/status')
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').textContent = data.status || 'Unknown';
                document.getElementById('version').textContent = data.version || 'Unknown';
            })
            .catch(error => {
                document.getElementById('status').textContent = 'Error';
                console.error('Error checking API status:', error);
            });
            
        // Run prediction
        function runPrediction() {
            const prompt = document.getElementById('prompt').value;
            if (!prompt) {
                alert('Please enter a prompt');
                return;
            }
            
            document.getElementById('result').textContent = 'Loading...';
            
            fetch('/api/v1/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                }),
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => {
                document.getElementById('result').textContent = 'Error: ' + error.message;
                console.error('Error running prediction:', error);
            });
        }
        
        // Run streaming prediction
        function runStreamingPrediction() {
            const prompt = document.getElementById('prompt').value;
            if (!prompt) {
                alert('Please enter a prompt');
                return;
            }
            
            const resultElement = document.getElementById('result');
            resultElement.textContent = 'Streaming...';
            
            const eventSource = new EventSource(`/api/v1/predict/stream?prompt=${encodeURIComponent(prompt)}`);
            let resultText = '';
            
            eventSource.onmessage = function(event) {
                if (event.data === '[DONE]') {
                    eventSource.close();
                    return;
                }
                
                try {
                    const data = JSON.parse(event.data);
                    if (data.prediction) {
                        resultText = JSON.stringify(data.prediction, null, 2);
                    } else if (data.chunk) {
                        resultText += data.chunk;
                    } else if (data.error) {
                        resultText = 'Error: ' + data.error;
                    }
                    resultElement.textContent = resultText;
                } catch (error) {
                    console.error('Error parsing stream data:', error);
                }
            };
            
            eventSource.onerror = function(error) {
                console.error('Error with EventSource:', error);
                eventSource.close();
                resultElement.textContent = 'Error with streaming. See console for details.';
            };
        }
    </script>
</body>
</html>
"""