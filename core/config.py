from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./stocks.db"
    API_V1_STR: str = "/api/v1"

settings = Settings() 