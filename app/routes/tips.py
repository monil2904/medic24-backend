from fastapi import APIRouter

router = APIRouter()

@router.get("/today")
async def get_todays_tip():
    return {
        "tip": {
            "id": 1,
            "title": "Daily Hydration Goals",
            "tip": "Ensure you drink at least 8 glasses of water today to flush out toxins, improve your skin, and keep your energy levels high throughout the day.",
            "category": "nutrition",
            "icon": "💧"
        }
    }

@router.get("/all")
async def get_all_tips():
    return {
        "tips": [
            {
                "id": 1,
                "title": "Daily Hydration Goals",
                "tip": "Ensure you drink at least 8 glasses of water today to flush out toxins, improve your skin, and keep your energy levels high throughout the day.",
                "category": "nutrition",
                "icon": "💧"
            },
            {
                "id": 2,
                "title": "The Power of Sleep",
                "tip": "Getting 7-8 hours of uninterrupted sleep significantly boosts your immune system and helps consolidate memory.",
                "category": "lifestyle",
                "icon": "😴"
            },
            {
                "id": 3,
                "title": "Morning Stretching",
                "tip": "A simple 5-minute stretch every morning can increase blood flow to your muscles and prepare your body for the day.",
                "category": "exercise",
                "icon": "🧘"
            },
            {
                "id": 4,
                "title": "Digital Detox",
                "tip": "Take a 10-minute break away from all screens every 2 hours to prevent eye strain and mental fatigue.",
                "category": "mental",
                "icon": "📱"
            }
        ]
    }

@router.get("/categories")
async def get_categories():
    return {
        "categories": [
            "nutrition", 
            "exercise", 
            "checkup", 
            "lifestyle", 
            "mental", 
            "seasonal", 
            "safety", 
            "hygiene", 
            "emergency"
        ]
    }
