from fastapi import APIRouter

router = APIRouter()

@router.get("/common")
async def get_common_medicines():
    return [
        {"name": "Paracetamol", "uses": ["Fever", "Mild pain"], "category": "Pain Reliever"},
        {"name": "Ibuprofen", "uses": ["Inflammation", "Pain", "Fever"], "category": "NSAID"},
        {"name": "Cetirizine", "uses": ["Allergies", "Hay fever"], "category": "Antihistamine"}
    ]
