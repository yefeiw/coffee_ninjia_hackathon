from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Coffee Ninja"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    openai_api_key: str | None = None
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    qdrant_path: str = "./qdrant_data"
    qdrant_collection_name: str = "coffee_profiles"
    retrieval_top_k: int = 8
    chat_store_path: str = "./chat_data/conversations.json"
    profile_store_path: str = "./profile_data/profiles.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
