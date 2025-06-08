"""
Vector store API endpoints for DSPy frontend.

This module provides FastAPI endpoints for interacting with vector stores,
specifically SAP HANA Cloud vector database integration.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional, Union

try:
    import fastapi
    from fastapi import APIRouter, Depends, HTTPException, Request, status
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError(
        "FastAPI and Pydantic are required. "
        "Install with 'pip install fastapi uvicorn pydantic'"
    )

# Import DSPy utilities
import dspy
from dspy.utils.logging_utils import enable_logging

logger = logging.getLogger(__name__)

# API Models
class VectorSearchRequest(BaseModel):
    """Vector search request model."""
    query: str
    k: int = Field(default=5, description="Number of results to return")
    filter_dict: Optional[Dict[str, Any]] = Field(default=None, description="Optional filter conditions")

class VectorStoreDocument(BaseModel):
    """Vector store document model."""
    id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None
    score: Optional[float] = None

class VectorSearchResponse(BaseModel):
    """Vector search response model."""
    results: List[VectorStoreDocument]
    latency: float

class VectorCollectionInfo(BaseModel):
    """Vector collection information model."""
    name: str
    document_count: int
    dimension: int

# Create API router
router = APIRouter(prefix="/api/v1/vectorstore", tags=["Vector Store"])

def get_vector_store():
    """Get the configured vector store."""
    try:
        # First check if we have a vector store in settings
        if hasattr(dspy.settings, 'vector_store'):
            return dspy.settings.vector_store
        
        # If not, check if we have SAPHanaRM configured
        vector_store_type = os.environ.get('DSPY_VECTOR_STORE', '').lower()
        
        if vector_store_type == 'sap_hana':
            try:
                from dspy.retrieve.sap_hana_rm import HanaVectorStore
                
                # Get connection parameters from environment
                host = os.environ.get('SAP_HANA_HOST')
                port = int(os.environ.get('SAP_HANA_PORT', 443))
                user = os.environ.get('SAP_HANA_USER')
                password = os.environ.get('SAP_HANA_PASSWORD')
                schema = os.environ.get('SAP_HANA_SCHEMA', 'PUBLIC')
                table = os.environ.get('SAP_HANA_TABLE', 'VECTOR_STORE')
                
                # Create connection to SAP HANA
                from hdbcli import dbapi
                connection = dbapi.connect(
                    address=host,
                    port=port,
                    user=user,
                    password=password,
                    sslValidateCertificate=False
                )
                
                # Create vector store
                vector_store = HanaVectorStore(
                    connection=connection,
                    schema=schema,
                    table=table
                )
                
                # Cache in settings for future use
                dspy.settings.vector_store = vector_store
                return vector_store
                
            except ImportError:
                logger.warning("hdbcli package not installed. Install with 'pip install hdbcli'")
                return None
            except Exception as e:
                logger.error(f"Error initializing SAP HANA Cloud vector store: {e}")
                return None
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting vector store: {e}")
        return None

@router.get("/status")
async def vector_store_status():
    """Get the status of the vector store."""
    try:
        vector_store = get_vector_store()
        
        if vector_store is None:
            return {
                "status": "not_configured",
                "message": "Vector store is not configured"
            }
        
        # Check connection by executing a simple query
        if hasattr(vector_store, 'connection'):
            try:
                cursor = vector_store.connection.cursor()
                cursor.execute("SELECT 1 FROM DUMMY")
                cursor.close()
                connection_ok = True
            except Exception as e:
                logger.error(f"Error checking SAP HANA connection: {e}")
                connection_ok = False
                
            return {
                "status": "connected" if connection_ok else "error",
                "type": "sap_hana",
                "connection_ok": connection_ok,
                "host": getattr(vector_store, 'host', 'unknown'),
                "schema": getattr(vector_store, 'schema', 'unknown'),
                "table": getattr(vector_store, 'table', 'unknown'),
                "message": "Connected to SAP HANA Cloud" if connection_ok else f"Error connecting to SAP HANA Cloud"
            }
        
        return {
            "status": "unknown",
            "message": "Vector store connection status could not be determined"
        }
        
    except Exception as e:
        logger.error(f"Error checking vector store status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/collections", response_model=List[VectorCollectionInfo])
async def vector_store_collections():
    """Get the list of collections in the vector store."""
    try:
        vector_store = get_vector_store()
        
        if vector_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vector store is not configured"
            )
        
        # For SAP HANA, we don't have collections like other vector DBs
        # Instead, we have a single table with vectors
        # We'll return information about the table
        
        if hasattr(vector_store, 'connection') and hasattr(vector_store, 'table_fqn'):
            try:
                cursor = vector_store.connection.cursor()
                
                # Get document count
                cursor.execute(f"SELECT COUNT(*) FROM {vector_store.table_fqn}")
                document_count = cursor.fetchone()[0]
                
                # We don't need to query for dimension since we already have it
                dimension = getattr(vector_store, 'dimension', 1536)
                
                cursor.close()
                
                # Return a single collection representing the table
                return [
                    {
                        "name": vector_store.table,
                        "document_count": document_count,
                        "dimension": dimension
                    }
                ]
                
            except Exception as e:
                logger.error(f"Error getting vector store collections: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error getting vector store collections: {e}"
                )
        
        # If we can't determine collections, return empty list
        return []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vector store collections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/search", response_model=VectorSearchResponse)
async def vector_store_search(request: VectorSearchRequest):
    """Search for documents in the vector store."""
    try:
        vector_store = get_vector_store()
        
        if vector_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vector store is not configured"
            )
        
        # Check if we have a working embedder
        try:
            embedder = dspy.settings.embedder
            if embedder is None:
                raise ValueError("No embedder configured in DSPy settings")
        except Exception as e:
            logger.error(f"Error getting embedder: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Embedder not configured or not working: {e}"
            )
        
        # Get embedding for query
        try:
            query_embedding = embedder.encode([request.query])[0].tolist()
        except Exception as e:
            logger.error(f"Error generating embedding for query: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating embedding: {e}"
            )
        
        # Perform search
        start_time = time.time()
        
        try:
            search_results = vector_store.similarity_search(
                query_vector=query_embedding,
                k=request.k,
                filter_dict=request.filter_dict
            )
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error performing similarity search: {e}"
            )
        
        latency = time.time() - start_time
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "id": result.get("id", ""),
                "text": result.get("text", ""),
                "metadata": result.get("metadata", {}),
                "score": result.get("score", 0.0)
            })
        
        return {
            "results": results,
            "latency": latency
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching vector store: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )