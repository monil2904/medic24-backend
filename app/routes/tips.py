from fastapi import APIRouter

router = APIRouter()

@router.get("/today")
async def get_todays_tip():
    return {
        "tip": "Stay hydrated! Drinking water helps maintain the balance of body fluids, ensuring your organs function properly.",
        "category": "hydration",
        "source": "Med24 AI Health Tips"
    }

@router.get("/all")
async def get_all_tips():
    return [
         {
            "tip": "Stay hydrated! Drinking water helps maintain the balance of body fluids, ensuring your organs function properly.",
            "category": "hydration",
            "source": "Med24 AI Health Tips"
        },
        {
            "tip": "Getting 7-9 hours of sleep each night is essential for immune function and mental health.",
            "category": "sleep",
            "source": "Med24 AI Health Tips"
        }
    ]
