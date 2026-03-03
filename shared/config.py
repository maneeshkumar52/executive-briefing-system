from pydantic_settings import BaseSettings
from functools import lru_cache
from openai import AsyncAzureOpenAI
import structlog

logger = structlog.get_logger()


class Settings(BaseSettings):
    azure_openai_endpoint: str = "https://placeholder.openai.azure.com/"
    azure_openai_api_key: str = "placeholder"
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-02-01"
    cosmos_endpoint: str = "https://placeholder.documents.azure.com:443/"
    cosmos_key: str = "placeholder"
    cosmos_database: str = "executive-briefings"
    cosmos_container: str = "briefings"
    service_bus_connection_string: str = "placeholder"
    local_mode: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_openai_client() -> AsyncAzureOpenAI:
    s = get_settings()
    return AsyncAzureOpenAI(
        azure_endpoint=s.azure_openai_endpoint,
        api_key=s.azure_openai_api_key,
        api_version=s.azure_openai_api_version,
    )
