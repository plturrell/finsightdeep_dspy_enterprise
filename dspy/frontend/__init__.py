"""
DSPy frontend module.

This module provides frontend interfaces for DSPy, including web dashboards,
visualization tools, and API endpoints.
"""

from dspy.frontend.config import FrontendConfig
from dspy.frontend.server import create_app, start_server

__all__ = [
    "FrontendConfig",
    "create_app",
    "start_server",
]