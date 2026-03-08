from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.middleware.auth import get_current_user
from app.services.storage_service import upload_file
from app.models.medgemma import query_with_image
from app.models.meditron import query as meditron_query
from app.models.medichat import query as medichat_query
from app.services.user_service import increment_image_queries
import base64
import uuid
import asyncio

router = APIRouter()

IMAGE_RATE_LIMITS = {
    "free": 0,
    "basic": 5,
    "pro": 999,
    "medical_pro": 999
}

@router.post("/")
async def analyze_image(
    file: UploadFile = File(...),
    query: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["id"])
    plan = current_user.get("subscription_plan", "free")

    # Increment monthly image query counter
    await increment_image_queries(user_id)

    if IMAGE_RATE_LIMITS.get(plan, 0) == 0:
        raise HTTPException(status_code=403, detail="Image analysis requires basic plan or higher")
        
    # Check size (max 10MB)
    MAX_SIZE = 10 * 1024 * 1024
    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image exceeds 10MB limit")
        
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are supported")

    # Upload to GCS
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"images/{user_id}_{uuid.uuid4()}.{ext}"
    gcs_url = await upload_file(file_bytes, filename, file.content_type)
    
    # Convert to base64 for LLM
    img_b64 = base64.b64encode(file_bytes).decode('utf-8')
    
    # Get Multimodal MedGemma description
    gemma_desc = await query_with_image(img_b64, query)
    if not gemma_desc:
        raise HTTPException(status_code=500, detail="Failed to analyze image with MedGemma")
        
    # Send description to Meditron & Medichat
    enhanced_query = f"Image description: {gemma_desc}\nUser query: {query}"
    
    results = await asyncio.gather(
        meditron_query(enhanced_query),
        medichat_query(enhanced_query),
        return_exceptions=True
    )
    
    meditron_res, medichat_res = results
    meditron_clean = meditron_res if isinstance(meditron_res, str) else None
    medichat_clean = medichat_res if isinstance(medichat_res, str) else None
    
    # Create final response
    ensemble_response = f"### Visual Analysis (MedGemma)\n{gemma_desc}\n\n"
    if meditron_clean:
        ensemble_response += f"### Guidelines & Recommendations (Meditron)\n{meditron_clean}\n\n"
    if medichat_clean:
        ensemble_response += f"### Simple Explanation (MediChat)\n{medichat_clean}\n\n"
        
    return {
        "ensemble_response": ensemble_response,
        "image_url": gcs_url,
        "models_used": ["medgemma", "meditron", "medichat"]
    }
