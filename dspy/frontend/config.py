"""
Configuration module for DSPy frontend.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FrontendConfig:
    """Configuration for the DSPy frontend."""
    
    # Server configuration
    host: str = "127.0.0.1"
    port: int = 8080
    debug: bool = False
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # API configuration
    api_prefix: str = "/api"
    api_version: str = "v1"
    
    # Authentication
    enable_auth: bool = False
    auth_token_expiry: int = 3600  # 1 hour in seconds
    jwt_secret: Optional[str] = None
    
    # Frontend assets
    static_folder: str = "static"
    template_folder: str = "templates"
    
    # Monitoring and tracking
    enable_telemetry: bool = False
    enable_monitoring: bool = True
    
    # Experiment tracking
    experiment_tracking_dir: str = "experiments"
    
    # Model serving
    model_cache_dir: str = "model_cache"
    
    # Additional custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize with environment variables if available."""
        env_prefix = "DSPY_FRONTEND_"
        
        # Override from environment variables
        for key, value in self.__dict__.items():
            env_var = f"{env_prefix}{key.upper()}"
            if env_var in os.environ:
                env_value = os.environ[env_var]
                
                # Type conversion
                if isinstance(value, bool):
                    setattr(self, key, env_value.lower() in ("true", "1", "yes"))
                elif isinstance(value, int):
                    setattr(self, key, int(env_value))
                elif isinstance(value, list):
                    setattr(self, key, env_value.split(","))
                else:
                    setattr(self, key, env_value)
        
        # Special case for JWT secret
        if "DSPY_FRONTEND_JWT_SECRET" in os.environ:
            self.jwt_secret = os.environ["DSPY_FRONTEND_JWT_SECRET"]
        elif self.enable_auth and not self.jwt_secret:
            import secrets
            self.jwt_secret = secrets.token_hex(32)
    
    def get_full_api_prefix(self) -> str:
        """Get the full API prefix including version."""
        return f"{self.api_prefix}/{self.api_version}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary, hiding sensitive fields."""
        config_dict = {k: v for k, v in self.__dict__.items() if k != "jwt_secret"}
        # Add a placeholder for sensitive fields
        if self.jwt_secret:
            config_dict["jwt_secret"] = "***HIDDEN***"
        return config_dict