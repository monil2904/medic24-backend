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
    RAZORPAY_WEBHOOK_SECRET: str = ""
    RAZORPAY_PLAN_BASIC_MONTHLY: str = "plan_SVwfKLy699DjYo"
    RAZORPAY_PLAN_PRO_MONTHLY: str = "plan_SVwg6oqHcbABR8"
    RAZORPAY_PLAN_MEDICAL_PRO_MONTHLY: str = "plan_SVwhDrp1iFpWQI"
    RAZORPAY_PLAN_BASIC_YEARLY: str = "plan_SVwkSuyrPc7cOq"
    RAZORPAY_PLAN_PRO_YEARLY: str = "plan_SVwtowGjrUM1nT"
    RAZORPAY_PLAN_MEDICAL_PRO_YEARLY: str = "plan_SVwuiQuhoZ00Tp"
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
