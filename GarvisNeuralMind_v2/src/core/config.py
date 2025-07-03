"""
Configuration management for GarvisNeuralMind
Handles loading settings from YAML files and environment variables
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration"""
    
    # App configuration
    app_name: str = "GarvisNeuralMind"
    app_version: str = "2.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # AI Model API Keys
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    google_ai_api_key: Optional[str] = Field(None, env="GOOGLE_AI_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Database settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = 0
    
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "garvis_neural_mind"
    postgres_user: Optional[str] = Field(None, env="POSTGRES_USER")
    postgres_password: Optional[str] = Field(None, env="POSTGRES_PASSWORD")
    
    # Pinecone settings
    pinecone_api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    pinecone_environment: str = "us-west1-gcp-free"
    pinecone_index_name: str = "garvis-memory"
    
    # Feature flags
    voice_interaction: bool = True
    browser_control: bool = True
    code_assistance: bool = True
    memory_persistence: bool = True
    fine_tuning: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/garvis.log"
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize settings with optional YAML config file"""
        super().__init__()
        
        # Load from YAML file if provided
        if config_path:
            self.load_from_yaml(config_path)
        else:
            # Try to load default config
            default_config = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
            if default_config.exists():
                self.load_from_yaml(str(default_config))
    
    def load_from_yaml(self, config_path: str):
        """Load settings from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Update settings from YAML
            if config_data:
                self._update_from_dict(config_data)
                
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update settings from dictionary"""
        
        # App settings
        if "app" in config_data:
            app_config = config_data["app"]
            self.app_name = app_config.get("name", self.app_name)
            self.app_version = app_config.get("version", self.app_version)
            self.debug = app_config.get("debug", self.debug)
            self.host = app_config.get("host", self.host)
            self.port = app_config.get("port", self.port)
        
        # AI models
        if "ai_models" in config_data:
            models = config_data["ai_models"]
            if "openrouter" in models:
                self.openrouter_api_key = self._expand_env_vars(
                    models["openrouter"].get("api_key", self.openrouter_api_key)
                )
            if "google_ai" in models:
                self.google_ai_api_key = self._expand_env_vars(
                    models["google_ai"].get("api_key", self.google_ai_api_key)
                )
            if "openai" in models:
                self.openai_api_key = self._expand_env_vars(
                    models["openai"].get("api_key", self.openai_api_key)
                )
        
        # Storage settings
        if "storage" in config_data:
            storage = config_data["storage"]
            
            if "redis" in storage:
                redis_config = storage["redis"]
                self.redis_host = redis_config.get("host", self.redis_host)
                self.redis_port = redis_config.get("port", self.redis_port)
                self.redis_password = self._expand_env_vars(
                    redis_config.get("password", self.redis_password)
                )
                self.redis_db = redis_config.get("db", self.redis_db)
            
            if "postgresql" in storage:
                pg_config = storage["postgresql"]
                self.postgres_host = pg_config.get("host", self.postgres_host)
                self.postgres_port = pg_config.get("port", self.postgres_port)
                self.postgres_db = pg_config.get("database", self.postgres_db)
                self.postgres_user = self._expand_env_vars(
                    pg_config.get("username", self.postgres_user)
                )
                self.postgres_password = self._expand_env_vars(
                    pg_config.get("password", self.postgres_password)
                )
            
            if "pinecone" in storage:
                pinecone_config = storage["pinecone"]
                self.pinecone_api_key = self._expand_env_vars(
                    pinecone_config.get("api_key", self.pinecone_api_key)
                )
                self.pinecone_environment = pinecone_config.get("environment", self.pinecone_environment)
                self.pinecone_index_name = pinecone_config.get("index_name", self.pinecone_index_name)
        
        # Features
        if "features" in config_data:
            features = config_data["features"]
            self.voice_interaction = features.get("voice_interaction", self.voice_interaction)
            self.browser_control = features.get("browser_control", self.browser_control)
            self.code_assistance = features.get("code_assistance", self.code_assistance)
            self.memory_persistence = features.get("memory_persistence", self.memory_persistence)
            self.fine_tuning = features.get("fine_tuning", self.fine_tuning)
        
        # Logging
        if "logging" in config_data:
            logging_config = config_data["logging"]
            self.log_level = logging_config.get("level", self.log_level)
            self.log_file = logging_config.get("file", self.log_file)
    
    def _expand_env_vars(self, value: Optional[str]) -> Optional[str]:
        """Expand environment variables in string values"""
        if not value or not isinstance(value, str):
            return value
        
        # Handle ${VAR_NAME} format
        if value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var)
        
        return value
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"