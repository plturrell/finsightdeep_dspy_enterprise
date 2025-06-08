"""
API endpoints for DSPy frontend.
"""

from dspy.frontend.api.vector_store_api import router as vector_store_router

__all__ = [
    "vector_store_router",
]