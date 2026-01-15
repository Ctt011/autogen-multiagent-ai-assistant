"""
Configuration management for the Multi-Agent AI Assistant.

This module provides centralized configuration using environment variables
for better security and deployment flexibility.
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Config:
    """Configuration class for the Multi-Agent AI Assistant."""

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "1.0"))

    # Tavily Search API
    TAVILY_SEARCH_KEY: str = os.getenv("TAVILY_SEARCH_KEY", "")
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

    # Slack Configuration (Optional)
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET", "")

    # Google API Configuration
    GOOGLE_CREDENTIALS_FILE: str = os.getenv(
        "GOOGLE_CREDENTIALS_FILE",
        str(PROJECT_ROOT / "credentials.json")
    )
    GOOGLE_TOKEN_FILE: str = os.getenv(
        "GOOGLE_TOKEN_FILE",
        str(PROJECT_ROOT / "token.json")
    )
    GOOGLE_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/calendar",
        "https://mail.google.com/",
    ]

    # Timezone Configuration
    DEFAULT_TIMEZONE: str = os.getenv("DEFAULT_TIMEZONE", "America/Los_Angeles")

    # Weather API Configuration (Open-Meteo is free, no API key needed)
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org/search"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", str(PROJECT_ROOT / "logs" / "assistant.log"))

    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration values.

        Raises:
            ValueError: If required configuration is missing.
        """
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")

        if not cls.TAVILY_SEARCH_KEY:
            errors.append("TAVILY_SEARCH_KEY is required")

        if errors:
            raise ValueError(
                f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            )

    @classmethod
    def is_slack_enabled(cls) -> bool:
        """Check if Slack integration is configured."""
        return bool(cls.SLACK_BOT_TOKEN and cls.SLACK_SIGNING_SECRET)

    @classmethod
    def is_google_enabled(cls) -> bool:
        """Check if Google APIs (Gmail/Calendar) are configured."""
        creds_file = Path(cls.GOOGLE_CREDENTIALS_FILE)
        return creds_file.exists()


# Create singleton instance
config = Config()
