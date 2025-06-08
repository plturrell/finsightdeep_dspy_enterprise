"""
Command-line interface for DSPy frontend.
"""

import argparse
import logging
import os
import sys
from typing import List, Optional

from dspy.frontend.config import FrontendConfig
from dspy.frontend.server import start_server

logger = logging.getLogger(__name__)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="DSPy Frontend Server")
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the server on (default: 127.0.0.1)",
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the server on (default: 8080)",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    
    parser.add_argument(
        "--enable-auth",
        action="store_true",
        help="Enable authentication",
    )
    
    parser.add_argument(
        "--disable-cors",
        action="store_true",
        help="Disable CORS (Cross-Origin Resource Sharing)",
    )
    
    parser.add_argument(
        "--cors-origins",
        type=str,
        default="*",
        help="CORS origins (comma-separated) (default: *)",
    )
    
    parser.add_argument(
        "--static-folder",
        type=str,
        help="Path to static files folder",
    )
    
    parser.add_argument(
        "--template-folder",
        type=str,
        help="Path to template files folder",
    )
    
    parser.add_argument(
        "--experiment-tracking-dir",
        type=str,
        help="Path to experiment tracking directory",
    )
    
    return parser.parse_args(args)


def configure_logging(debug: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        debug: Whether to enable debug logging
    """
    log_level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )


def main(args: Optional[List[str]] = None) -> None:
    """
    Main entry point for the DSPy frontend CLI.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
    """
    parsed_args = parse_args(args)
    configure_logging(parsed_args.debug)
    
    # Create configuration from arguments
    config = FrontendConfig(
        host=parsed_args.host,
        port=parsed_args.port,
        debug=parsed_args.debug,
        enable_cors=not parsed_args.disable_cors,
        cors_origins=parsed_args.cors_origins.split(","),
        enable_auth=parsed_args.enable_auth,
    )
    
    # Override with provided arguments if specified
    if parsed_args.static_folder:
        config.static_folder = parsed_args.static_folder
    
    if parsed_args.template_folder:
        config.template_folder = parsed_args.template_folder
    
    if parsed_args.experiment_tracking_dir:
        config.experiment_tracking_dir = parsed_args.experiment_tracking_dir
    
    try:
        # Start the server
        start_server(config=config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()