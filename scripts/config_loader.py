"""
Universal Configuration Loader

Loads and validates configuration from config.yml with environment variable overrides.
Supports multiple deployment modes and agent connection types.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Agent connection configuration"""
    mode: str = "http"
    enabled: bool = True
    http: Dict[str, Any] = field(default_factory=dict)
    sdk: Dict[str, Any] = field(default_factory=dict)
    mcp: Dict[str, Any] = field(default_factory=dict)
    docker: Dict[str, Any] = field(default_factory=dict)
    local: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Config:
    """Main configuration class"""
    
    # Core settings
    agent_mode: str = "hybrid"
    
    # Agent configurations
    ollama: AgentConfig = field(default_factory=AgentConfig)
    openrouter: AgentConfig = field(default_factory=AgentConfig)
    
    # Other configurations
    research: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)
    docker: Dict[str, Any] = field(default_factory=dict)
    mcp: Dict[str, Any] = field(default_factory=dict)
    sdk: Dict[str, Any] = field(default_factory=dict)
    http: Dict[str, Any] = field(default_factory=dict)
    logging: Dict[str, Any] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)
    github_actions: Dict[str, Any] = field(default_factory=dict)
    features: Dict[str, Any] = field(default_factory=dict)
    experimental: Dict[str, Any] = field(default_factory=dict)
    cost: Dict[str, Any] = field(default_factory=dict)


class ConfigLoader:
    """Load and manage configuration"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent / "config.yml"
        self._config: Optional[Config] = None
    
    def load(self) -> Config:
        """Load configuration from file and environment"""
        if self._config:
            return self._config
        
        # Load from YAML
        if self.config_path.exists():
            with open(self.config_path) as f:
                config_dict = yaml.safe_load(f)
        else:
            config_dict = {}
        
        # Override with environment variables
        config_dict = self._apply_env_overrides(config_dict)
        
        # Create Config object
        self._config = self._dict_to_config(config_dict)
        
        return self._config
    
    def _apply_env_overrides(self, config_dict: Dict) -> Dict:
        """Apply environment variable overrides"""
        
        # Agent mode override
        if env_mode := os.getenv("AGENT_MODE"):
            config_dict["AGENT_MODE"] = env_mode
        
        # Ollama overrides
        if os.getenv("OLLAMA_API_KEY"):
            config_dict.setdefault("OLLAMA", {}).setdefault("http", {})["api_key"] = os.getenv("OLLAMA_API_KEY")
        
        if os.getenv("OLLAMA_MODE"):
            config_dict.setdefault("OLLAMA", {})["mode"] = os.getenv("OLLAMA_MODE")
        
        if os.getenv("OLLAMA_BASE_URL"):
            config_dict.setdefault("OLLAMA", {}).setdefault("http", {})["base_url"] = os.getenv("OLLAMA_BASE_URL")
        
        # OpenRouter overrides
        if os.getenv("OPENROUTER_API_KEY"):
            config_dict.setdefault("OPENROUTER", {}).setdefault("http", {})["api_key"] = os.getenv("OPENROUTER_API_KEY")
        
        if os.getenv("OPENROUTER_MODE"):
            config_dict.setdefault("OPENROUTER", {})["mode"] = os.getenv("OPENROUTER_MODE")
        
        if os.getenv("OPENROUTER_MODEL"):
            config_dict.setdefault("OPENROUTER", {}).setdefault("models", {})["primary"] = os.getenv("OPENROUTER_MODEL")
        
        # GitHub token
        if os.getenv("GITHUB_TOKEN"):
            config_dict.setdefault("RESEARCH", {}).setdefault("github", {})["token"] = os.getenv("GITHUB_TOKEN")
        
        # Force update
        if os.getenv("FORCE_UPDATE", "").lower() in ("true", "1", "yes"):
            config_dict.setdefault("RESEARCH", {})["force_update"] = True
        
        return config_dict
    
    def _dict_to_config(self, config_dict: Dict) -> Config:
        """Convert dictionary to Config object"""
        
        # Extract main sections
        ollama_dict = config_dict.get("OLLAMA", {})
        openrouter_dict = config_dict.get("OPENROUTER", {})
        
        # Create agent configs
        ollama_config = AgentConfig(
            mode=ollama_dict.get("mode", "http"),
            enabled=ollama_dict.get("enabled", True),
            http=ollama_dict.get("http", {}),
            sdk=ollama_dict.get("sdk", {}),
            mcp=ollama_dict.get("mcp", {}),
            docker=ollama_dict.get("docker", {}),
            local=ollama_dict.get("local", {})
        )
        
        openrouter_config = AgentConfig(
            mode=openrouter_dict.get("mode", "http"),
            enabled=openrouter_dict.get("enabled", True),
            http=openrouter_dict.get("http", {}),
            sdk=openrouter_dict.get("sdk", {}),
            mcp=openrouter_dict.get("mcp", {})
        )
        
        return Config(
            agent_mode=config_dict.get("AGENT_MODE", "hybrid"),
            ollama=ollama_config,
            openrouter=openrouter_config,
            research=config_dict.get("RESEARCH", {}),
            validation=config_dict.get("VALIDATION", {}),
            docker=config_dict.get("DOCKER", {}),
            mcp=config_dict.get("MCP", {}),
            sdk=config_dict.get("SDK", {}),
            http=config_dict.get("HTTP", {}),
            logging=config_dict.get("LOGGING", {}),
            monitoring=config_dict.get("MONITORING", {}),
            performance=config_dict.get("PERFORMANCE", {}),
            security=config_dict.get("SECURITY", {}),
            github_actions=config_dict.get("GITHUB_ACTIONS", {}),
            features=config_dict.get("FEATURES", {}),
            experimental=config_dict.get("EXPERIMENTAL", {}),
            cost=config_dict.get("COST", {})
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        if not self._config:
            self.load()
        
        parts = key.split(".")
        value = self._config.__dict__
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, default)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return default
        
        return value


# Global config instance
_config_loader = ConfigLoader()


def get_config() -> Config:
    """Get global configuration instance"""
    return _config_loader.load()


def get(key: str, default: Any = None) -> Any:
    """Get configuration value by key"""
    return _config_loader.get(key, default)


# Convenience functions
def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    return get(f"features.{feature}", False)


def get_agent_mode(agent: str) -> str:
    """Get connection mode for an agent"""
    return get(f"{agent}.mode", "http")


def is_agent_enabled(agent: str) -> bool:
    """Check if an agent is enabled"""
    return get(f"{agent}.enabled", True)
