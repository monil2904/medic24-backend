from fastapi import APIRouter, Depends, HTTPException
from app.schemas import ChatRequest, ChatResponse
from app.middleware.auth import get_current_user
from app.utils.safety import detect_emergency
from app.services.cache import get_cached_response, set_cached_response
from app.models.ensemble import ensemble_query
from app.services.chat_service import save_chat
from app.services.user_service import increment_queries

router = APIRouter()

RATE_LIMITS = {
    "free": 5,
    "basic": 50,
    "pro": 999,
    "medical_pro": 999
}

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["id"])
    plan = current_user.get("subscription_plan", "free")
    
    # Check rate limit
    queries_today = await increment_queries(user_id)
    limit = RATE_LIMITS.get(plan, 5)
    if queries_today > limit:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded for {plan} plan")
        
    is_emergency = detect_emergency(req.message)
    
    disclaimer = "\n---\n*Disclaimer: Med24 AI provides information for educational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult a healthcare provider."
    
    # Check cache
    cache_key = f"{req.message}_{req.query_type}"
    cached = get_cached_response(cache_key)
    if cached:
        # DB save happens in the background via event loop typically, but here we just wait
        await save_chat(
            user_id, req.message, req.query_type, cached["ensemble_response"],
            cached["individual_responses"].get("medgemma"),
            cached["individual_responses"].get("meditron"),
            cached["individual_responses"].get("medichat"),
            cached["confidence"]
        )
        return ChatResponse(
            ensemble_response=cached["ensemble_response"],
            confidence=cached["confidence"],
            models_used=cached["models_used"],
            processing_time_ms=0,
            disclaimer=disclaimer,
            is_emergency=is_emergency,
            individual_responses=cached["individual_responses"] if req.include_individual else None
        )

    # Call ensemble
    result = await ensemble_query(req.message, req.query_type)
    
    # Save cache
    set_cached_response(cache_key, result)
    
    # Save chat history
    ind_res = result["individual_responses"]
    await save_chat(
        user_id, req.message, req.query_type, result["ensemble_response"],
        ind_res.get("medgemma"), ind_res.get("meditron"), ind_res.get("medichat"),
        result["confidence"]
    )
    
    return ChatResponse(
        ensemble_response=result["ensemble_response"],
        confidence=result["confidence"],
        models_used=result["models_used"],
        processing_time_ms=result["processing_time_ms"],
        disclaimer=disclaimer,
        is_emergency=is_emergency,
        individual_responses=ind_res if req.include_individual else None
    )
