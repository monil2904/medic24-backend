from fastapi import APIRouter

router = APIRouter()

@router.get("/today")
async def get_todays_tip():
    return {
        "tip": "Stay hydrated! Drinking water helps maintain the balance of body fluids, ensuring your organs function properly.",
        "category": "hydration",
        "source": "Med24 AI Health Tips"
    }
