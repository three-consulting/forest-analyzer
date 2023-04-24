from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = "OPENAI_API_KEY"
    openai_model_name: str = "gpt-4"

    database_name: str = "DATABASE_NAME"
    database_user: str = "DATABASE_USER"
    database_password: str = "DATABASE_PASSWORD"
    database_port: str = "DATABASE_PORT"
    database_host: str = "DATABASE_HOST"

    class Config:
        env_file = ".env"