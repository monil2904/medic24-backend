from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    HF_TOKEN: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 72
    GCS_BUCKET_NAME: str = "med24-uploads"
    GOOGLE_CLIENT_ID: str
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()
