import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings and environment variables.
    Pydantic will automatically read these from a .env file or system environment variables.
    """

    GROQ_API_KEY: str 
    GROQ_MODEL_NAME: str = "llama-3.3-70b-versatile"

    APP_NAME: str = "AI Data Analyst"
    APP_VERSION: str = "1.0.0"
    DEBUG_MODE: bool = True

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "sample_data")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)