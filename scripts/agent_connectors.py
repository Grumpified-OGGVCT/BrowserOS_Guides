"""
Universal Agent Connectors

Supports multiple connection types: SDK, MCP, HTTP, Local, Docker
Automatically selects best available method based on configuration
"""

import os
import requests
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

try:
    from config_loader import get_config, get_agent_mode, is_agent_enabled
except ImportError:
    # Fallback for standalone execution
    def get_config(): return None
    def get_agent_mode(agent): return "http"
    def is_agent_enabled(agent): return True


class AgentConnector(ABC):
    """Base class for agent connectors"""
    
    @abstractmethod
    def query(self, prompt: str, **kwargs) -> str:
        """Send query to agent and get response"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if agent is available"""
        pass


class HTTPAgentConnector(AgentConnector):
    """HTTP/REST API connector"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def query(self, prompt: str, **kwargs) -> str:
        """Send HTTP request"""
        model = kwargs.get("model", "default")
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2000)
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        except Exception as e:
            print(f"❌ HTTP request failed: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check HTTP endpoint availability"""
        try:
            response = self.session.get(
                f"{self.base_url}/models",
                timeout=5
            )
            return response.status_code < 500
        except:
            return False


class SDKAgentConnector(AgentConnector):
    """SDK-based connector (Python client libraries)"""
    
    def __init__(self, sdk_type: str, **kwargs):
        self.sdk_type = sdk_type
        self.client = None
        self._initialize_client(**kwargs)
    
    def _initialize_client(self, **kwargs):
        """Initialize SDK client"""
        if self.sdk_type == "ollama":
            try:
                import ollama
                host = kwargs.get("host", "localhost:11434")
                self.client = ollama.Client(host=host)
            except ImportError:
                print("⚠️ Ollama SDK not installed: pip install ollama")
        
        elif self.sdk_type == "openai":
            try:
                from openai import OpenAI
                api_base = kwargs.get("api_base", "https://api.openai.com/v1")
                api_key = kwargs.get("api_key", os.getenv("OPENAI_API_KEY"))
                self.client = OpenAI(base_url=api_base, api_key=api_key)
            except ImportError:
                print("⚠️ OpenAI SDK not installed: pip install openai")
    
    def query(self, prompt: str, **kwargs) -> str:
        """Send query via SDK"""
        if not self.client:
            return ""
        
        model = kwargs.get("model", "llama2")
        temperature = kwargs.get("temperature", 0.7)
        
        try:
            if self.sdk_type == "ollama":
                response = self.client.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": temperature}
                )
                return response.get("message", {}).get("content", "")
            
            elif self.sdk_type == "openai":
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                return response.choices[0].message.content
        
        except Exception as e:
            print(f"❌ SDK query failed: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check SDK availability"""
        return self.client is not None


class MCPAgentConnector(AgentConnector):
    """Model Context Protocol connector"""
    
    def __init__(self, server_url: str, protocol_version: str = "2024-11-05"):
        self.server_url = server_url
        self.protocol_version = protocol_version
        self.transport = self._detect_transport()
    
    def _detect_transport(self) -> str:
        """Detect MCP transport type from URL"""
        if self.server_url.startswith("mcp://"):
            return "stdio"
        elif self.server_url.startswith("http"):
            return "http"
        elif self.server_url.startswith("ws"):
            return "websocket"
        return "stdio"
    
    def query(self, prompt: str, **kwargs) -> str:
        """Send query via MCP"""
        # MCP implementation would go here
        # For now, this is a placeholder
        print("⚠️ MCP connector not fully implemented yet")
        return ""
    
    def is_available(self) -> bool:
        """Check MCP server availability"""
        # Check if MCP server is running
        return False  # Placeholder


class DockerAgentConnector(AgentConnector):
    """Docker container connector"""
    
    def __init__(self, container_name: str, port: int = 11434):
        self.container_name = container_name
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.http_connector = HTTPAgentConnector(
            self.base_url,
            api_key="",  # Local container doesn't need auth
            timeout=60
        )
    
    def query(self, prompt: str, **kwargs) -> str:
        """Send query to Docker container"""
        return self.http_connector.query(prompt, **kwargs)
    
    def is_available(self) -> bool:
        """Check if Docker container is running"""
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return self.container_name in result.stdout
        except:
            return False


class LocalAgentConnector(AgentConnector):
    """Local binary connector (e.g., local Ollama installation)"""
    
    def __init__(self, binary_path: str, serve_address: str = "127.0.0.1:11434"):
        self.binary_path = binary_path
        self.serve_address = serve_address
        self.base_url = f"http://{serve_address}"
        self.http_connector = HTTPAgentConnector(
            self.base_url,
            api_key="",
            timeout=60
        )
    
    def query(self, prompt: str, **kwargs) -> str:
        """Send query to local binary"""
        return self.http_connector.query(prompt, **kwargs)
    
    def is_available(self) -> bool:
        """Check if local binary is available"""
        import subprocess
        try:
            result = subprocess.run(
                [self.binary_path, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


class UniversalAgentConnector:
    """Universal connector that auto-selects best available method"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.connectors: List[AgentConnector] = []
        self._initialize_connectors()
    
    def _initialize_connectors(self):
        """Initialize all possible connectors based on configuration"""
        config = get_config()
        if not config:
            # Fallback to environment-based configuration
            self._initialize_from_env()
            return
        
        agent_config = getattr(config, self.agent_name.lower(), None)
        if not agent_config or not agent_config.enabled:
            return
        
        mode = agent_config.mode
        
        # Initialize connectors based on mode
        if mode == "http" or mode == "hybrid":
            self._add_http_connector(agent_config.http)
        
        if mode == "sdk" or mode == "hybrid":
            self._add_sdk_connector(agent_config.sdk)
        
        if mode == "mcp" or mode == "hybrid":
            self._add_mcp_connector(agent_config.mcp)
        
        if mode == "docker" or mode == "hybrid":
            self._add_docker_connector(agent_config.docker)
        
        if mode == "local" or mode == "hybrid":
            self._add_local_connector(agent_config.local)
    
    def _initialize_from_env(self):
        """Fallback initialization from environment variables"""
        if self.agent_name.lower() == "ollama":
            api_key = os.getenv("OLLAMA_API_KEY")
            if api_key:
                self.connectors.append(
                    HTTPAgentConnector("https://api.ollama.ai/v1", api_key)
                )
        
        elif self.agent_name.lower() == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                self.connectors.append(
                    HTTPAgentConnector("https://openrouter.ai/api/v1", api_key)
                )
    
    def _add_http_connector(self, http_config: Dict):
        """Add HTTP connector"""
        base_url = http_config.get("base_url")
        api_key_env = http_config.get("api_key_env")
        api_key = http_config.get("api_key") or os.getenv(api_key_env, "")
        
        if base_url and api_key:
            self.connectors.append(
                HTTPAgentConnector(
                    base_url,
                    api_key,
                    http_config.get("timeout", 60)
                )
            )
    
    def _add_sdk_connector(self, sdk_config: Dict):
        """Add SDK connector"""
        sdk_type = self.agent_name.lower()
        if sdk_type == "openrouter":
            sdk_type = "openai"  # OpenRouter uses OpenAI SDK
        
        self.connectors.append(SDKAgentConnector(sdk_type, **sdk_config))
    
    def _add_mcp_connector(self, mcp_config: Dict):
        """Add MCP connector"""
        server_url = mcp_config.get("server_url")
        if server_url:
            self.connectors.append(
                MCPAgentConnector(
                    server_url,
                    mcp_config.get("protocol_version", "2024-11-05")
                )
            )
    
    def _add_docker_connector(self, docker_config: Dict):
        """Add Docker connector"""
        container_name = docker_config.get("container_name")
        if container_name:
            port = docker_config.get("ports", ["11434:11434"])[0].split(":")[0]
            self.connectors.append(
                DockerAgentConnector(container_name, int(port))
            )
    
    def _add_local_connector(self, local_config: Dict):
        """Add local binary connector"""
        binary_path = local_config.get("binary_path")
        if binary_path:
            self.connectors.append(
                LocalAgentConnector(
                    binary_path,
                    local_config.get("serve_address", "127.0.0.1:11434")
                )
            )
    
    def query(self, prompt: str, **kwargs) -> str:
        """Send query using first available connector"""
        for connector in self.connectors:
            if connector.is_available():
                print(f"✓ Using {connector.__class__.__name__} for {self.agent_name}")
                result = connector.query(prompt, **kwargs)
                if result:
                    return result
        
        print(f"⚠️ No available connector for {self.agent_name}")
        return ""
    
    def is_available(self) -> bool:
        """Check if any connector is available"""
        return any(c.is_available() for c in self.connectors)


# Factory function
def create_agent_connector(agent_name: str) -> UniversalAgentConnector:
    """Create universal agent connector for given agent"""
    return UniversalAgentConnector(agent_name)
