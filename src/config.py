"""
Configuration management for Code Guardian application.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for managing application settings."""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    
    # GitLab Configuration
    GITLAB_TOKEN: Optional[str] = os.getenv("GITLAB_TOKEN")
    GITLAB_URL: str = os.getenv("GITLAB_URL", "https://gitlab.com")
    
    # Application Settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    SUPPORTED_LANGUAGES: list = [
        "python", "java", "javascript", "typescript", "c#", "cpp", "c",
        "go", "rust", "php", "ruby", "swift", "kotlin", "scala"
    ]
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_required_settings(cls) -> None:
        """Validate that all required configuration settings are present."""
        required_settings = [
            ("AZURE_OPENAI_API_KEY", cls.AZURE_OPENAI_API_KEY),
            ("AZURE_OPENAI_ENDPOINT", cls.AZURE_OPENAI_ENDPOINT),
        ]
        
        missing_settings = []
        for setting_name, setting_value in required_settings:
            if not setting_value:
                missing_settings.append(setting_name)
        
        if missing_settings:
            raise ValueError(
                f"Missing required configuration settings: {', '.join(missing_settings)}"
            )


# Global configuration instance
config = Config()
