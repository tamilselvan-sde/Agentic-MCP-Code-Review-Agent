#################################
# ConfigManager
#################################
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

print("="*40)
# Config Loading
print("="*40)

load_dotenv()

class Config(BaseSettings):
    """Configuration class for the application settings."""
    github_token: str = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    repo_owner: str = os.getenv("GITHUB_REPO_OWNER", "tamilselvan-sde")
    repo_name: str = os.getenv("GITHUB_REPO_NAME", "MCP-PostgreSQL")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")
    
    @property
    def repo_full_name(self) -> str:
        """Returns the full repository name in owner/repo format."""
        return f"{self.repo_owner}/{self.repo_name}"

config = Config()

print("#===============[ Config loaded ]==========")
