# emergency keyword detection

EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "stroke", "heart attack", "suicide", "overdose", "seizure",
    "kill myself", "bleeding out", "unconscious", "trouble breathing", "choking"
]

def detect_emergency(query: str) -> bool:
    text_lower = query.lower()
    return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)
