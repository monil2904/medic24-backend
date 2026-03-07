from google.cloud import storage
from app.config import settings
from datetime import timedelta

def get_storage_client():
    # Attempt to initialize using standard google-cloud-storage credentials path 
    # (requires GOOGLE_APPLICATION_CREDENTIALS env var or service account config)
    return storage.Client()

async def upload_file(file_bytes: bytes, filename: str, content_type: str) -> str:
    client = get_storage_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(filename)
    # google-cloud-storage operates synchronously under the hood for this wrapper unless we use the async extensions, 
    # but this is fine for now
    blob.upload_from_string(file_bytes, content_type=content_type)
    
    # Return the public URL or gs:// link (here we use public URL format for simplicity)
    return f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{filename}"

async def get_signed_url(filename: str) -> str:
    client = get_storage_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(filename)
    
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=1),
        method="GET",
    )
    return url

async def delete_file(filename: str) -> bool:
    client = get_storage_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(filename)
    if blob.exists():
        blob.delete()
        return True
    return False
