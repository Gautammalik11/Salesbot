"""
Configuration settings for Sales Chatbot application.
Loads environment variables and provides application configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration."""

    # API Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database/sales.db")

    # Application Settings
    APP_TITLE: str = os.getenv("APP_TITLE", "Sales Data Chatbot")
    CURRENCY_SYMBOL: str = os.getenv("CURRENCY_SYMBOL", "$")
    DATE_FORMAT: str = os.getenv("DATE_FORMAT", "%Y-%m-%d")

    # Claude Model Configuration
    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"
    CLAUDE_TEMPERATURE: float = 0.0  # Lower temperature for more consistent SQL generation

    # CSV Processing Settings
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list = ['.csv', '.xlsx', '.xls']

    # Supported ERP Systems
    ERP_SYSTEMS: list = ['Odoo', 'Focus']

    # Analytics Settings
    DEFAULT_TOP_N: int = 10
    INACTIVE_CUSTOMER_DAYS: int = 90

    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are configured.

        Returns:
            True if valid, raises ValueError otherwise
        """
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Please set it in your .env file or environment variables."
            )

        if not cls.ANTHROPIC_API_KEY.startswith("sk-ant-"):
            raise ValueError(
                "Invalid ANTHROPIC_API_KEY format. "
                "API key should start with 'sk-ant-'"
            )

        return True

    @classmethod
    def get_database_url(cls) -> str:
        """Get SQLite database URL for SQLAlchemy.

        Returns:
            Database URL string
        """
        return f"sqlite:///{cls.DATABASE_PATH}"


# Create singleton instance
settings = Settings()
