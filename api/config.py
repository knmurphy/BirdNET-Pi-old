"""Configuration management using Pydantic Settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment and config files."""

    # Database paths
    database_path: Path = Path.home() / "BirdNET-Pi" / "scripts" / "birds.db"
    duckdb_path: Path = Path.home() / "BirdNET-Pi" / "scripts" / "birds.duckdb"

    # Server settings
    api_host: str = "0.0.0.0"
    api_port: int = 8003

    # BirdNET-Pi config file path
    config_ini_path: Path = Path.home() / "BirdNET-Pi" / "birdnet.conf"

    # Audio settings
    audio_base_path: Path = Path.home() / "BirdSongs" / "Extracted" / "By_Date"

    model_config = SettingsConfigDict(env_prefix="FIELD_STATION_")


# Global settings instance
settings = Settings()
