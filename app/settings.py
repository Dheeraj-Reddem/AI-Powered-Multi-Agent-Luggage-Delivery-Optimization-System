from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "local"
    DATABASE_URL: str
    REDIS_URL: str

    AIRPORT_BUFFER_MINUTES: int = 180
    BASE_PRICE: float = 15.0
    PRICE_PER_KM: float = 1.2
    PRICE_PER_KG: float = 0.6

    class Config:
        env_file = ".env"

settings = Settings()
