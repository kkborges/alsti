"""
Configuration module for Gemini Code Generator.
Loads environment variables and provides access to application settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class LanguagePaths(BaseModel):
    """Paths to language compilers and interpreters."""

    python: Optional[str] = Field(default=None)
    pip: Optional[str] = Field(default=None)
    node: Optional[str] = Field(default=None)
    npm: Optional[str] = Field(default=None)
    npx: Optional[str] = Field(default=None)
    java: Optional[str] = Field(default=None)
    javac: Optional[str] = Field(default=None)
    maven: Optional[str] = Field(default=None)
    gradle: Optional[str] = Field(default=None)
    dotnet: Optional[str] = Field(default=None)
    php: Optional[str] = Field(default=None)
    composer: Optional[str] = Field(default=None)
    go: Optional[str] = Field(default=None)
    cargo: Optional[str] = Field(default=None)
    rustc: Optional[str] = Field(default=None)
    ruby: Optional[str] = Field(default=None)
    gem: Optional[str] = Field(default=None)
    bundle: Optional[str] = Field(default=None)


class Config(BaseModel):
    """Application configuration."""

    # Gemini API
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-pro"

    # Language paths
    language_paths: LanguagePaths

    # Output configuration
    generated_code_dir: Path = Field(default=Path("./generated"))
    max_retry_attempts: int = 5
    validation_timeout: int = 30

    # Logging
    log_level: str = "INFO"
    log_file: Path = Field(default=Path("./gemini-code-generator.log"))

    class Config:
        arbitrary_types_allowed = True


def load_config() -> Config:
    """
    Load configuration from environment variables.

    Returns:
        Config: Application configuration

    Raises:
        ValueError: If required configuration is missing
    """
    # Load .env file
    load_dotenv()

    # Check for required variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please copy .env.example to .env and set your API key."
        )

    # Load language paths
    language_paths = LanguagePaths(
        python=os.getenv("PYTHON_PATH"),
        pip=os.getenv("PIP_PATH"),
        node=os.getenv("NODE_PATH"),
        npm=os.getenv("NPM_PATH"),
        npx=os.getenv("NPX_PATH"),
        java=os.getenv("JAVA_PATH"),
        javac=os.getenv("JAVAC_PATH"),
        maven=os.getenv("MAVEN_PATH"),
        gradle=os.getenv("GRADLE_PATH"),
        dotnet=os.getenv("DOTNET_PATH"),
        php=os.getenv("PHP_PATH"),
        composer=os.getenv("COMPOSER_PATH"),
        go=os.getenv("GO_PATH"),
        cargo=os.getenv("CARGO_PATH"),
        rustc=os.getenv("RUSTC_PATH"),
        ruby=os.getenv("RUBY_PATH"),
        gem=os.getenv("GEM_PATH"),
        bundle=os.getenv("BUNDLE_PATH"),
    )

    # Create config
    config = Config(
        gemini_api_key=api_key,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
        language_paths=language_paths,
        generated_code_dir=Path(os.getenv("GENERATED_CODE_DIR", "./generated")),
        max_retry_attempts=int(os.getenv("MAX_RETRY_ATTEMPTS", "5")),
        validation_timeout=int(os.getenv("VALIDATION_TIMEOUT", "30")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=Path(os.getenv("LOG_FILE", "./gemini-code-generator.log")),
    )

    # Create generated code directory if it doesn't exist
    config.generated_code_dir.mkdir(parents=True, exist_ok=True)

    return config


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config: Application configuration
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config
