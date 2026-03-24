from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.schemas import MedicineLookupRequest
from app.models import medgemma

router = APIRouter()

@router.get("/common")
async def get_common_medicines():
    return [
        {"name": "Paracetamol", "uses": ["Fever", "Mild pain"], "category": "Pain Reliever"},
        {"name": "Ibuprofen", "uses": ["Inflammation", "Pain", "Fever"], "category": "NSAID"},
        {"name": "Cetirizine", "uses": ["Allergies", "Hay fever"], "category": "Antihistamine"}
    ]

@router.post("/lookup")
async def lookup_medicine(req: MedicineLookupRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["id"])
    
    prompt = f"Provide comprehensive clinical information about the medicine: {req.medicine_name}. Focus your response appropriately for a {req.query_type} query type."
    
    # Use single_model_query with model
    response = await medgemma.query(prompt)
    
    if not response:
        raise HTTPException(status_code=500, detail="Failed to fetch medicine information")
        
    return {
        "medicine_name": req.medicine_name,
        "query_type": req.query_type,
        "analysis": response,
        "model_used": "Medgemma 27B"
    }
