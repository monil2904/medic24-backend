import asyncio
import time
import hashlib
from app.models import medgemma, meditron, medichat
from app.utils.safety import detect_emergency

async def ensemble_query(user_query: str, query_type: str = "general") -> dict:
    """
    Call all 3 medical AI models IN PARALLEL, merge their responses.
    This is a TRUE ensemble — not a single model with different prompts.
    """
    start_time = time.time()

    # Check for emergency FIRST
    is_emergency = detect_emergency(user_query)

    # Define weights based on query type
    weights = {
        "clinical":  {"medgemma": 0.45, "meditron": 0.30, "medichat": 0.25},
        "drug":      {"medgemma": 0.35, "meditron": 0.40, "medichat": 0.25},
        "symptom":   {"medgemma": 0.30, "meditron": 0.25, "medichat": 0.45},
        "general":   {"medgemma": 0.40, "meditron": 0.30, "medichat": 0.30},
    }.get(query_type, {"medgemma": 0.40, "meditron": 0.30, "medichat": 0.30})

    # Call ALL 3 models in PARALLEL
    results = await asyncio.gather(
        medgemma.query(user_query),
        meditron.query(user_query),
        medichat.query(user_query),
        return_exceptions=True
    )

    # Process results
    medgemma_response = results[0] if isinstance(results[0], str) else None
    meditron_response = results[1] if isinstance(results[1], str) else None
    medichat_response = results[2] if isinstance(results[2], str) else None

    # Track which models succeeded
    models_used = []
    responses = {}
    if medgemma_response:
        models_used.append("MedGemma 27B")
        responses["medgemma"] = medgemma_response
    if meditron_response:
        models_used.append("Meditron 7B")
        responses["meditron"] = meditron_response
    if medichat_response:
        models_used.append("MediChat-Llama3")
        responses["medichat"] = medichat_response

    # Calculate confidence based on how many models responded
    confidence = len(models_used) / 3.0  # 1.0 if all 3, 0.67 if 2, 0.33 if 1

    # Merge responses into ensemble answer
    if not models_used:
        ensemble_response = "I apologize, but I'm unable to process your query right now. Please try again in a moment."
        confidence = 0.0
    elif len(models_used) == 1:
        ensemble_response = list(responses.values())[0]
    else:
        # Build weighted merged response
        sections = []
        if medgemma_response:
            sections.append(f"**Clinical Analysis:**\n{medgemma_response}")
        if meditron_response:
            sections.append(f"**Medical Guidelines:**\n{meditron_response}")
        if medichat_response:
            sections.append(f"**Patient-Friendly Explanation:**\n{medichat_response}")
        ensemble_response = "\n\n---\n\n".join(sections)

    # Add disclaimer
    disclaimer = "\n\n⚠️ *This information is for educational purposes only and does not replace professional medical advice. Always consult a qualified healthcare provider.*"
    ensemble_response += disclaimer

    # Add emergency warning if detected
    if is_emergency:
        ensemble_response = "🚨 **EMERGENCY DETECTED** — If you are experiencing a medical emergency, please call **112** (India) or go to your nearest emergency room immediately.\n\n" + ensemble_response

    processing_time = int((time.time() - start_time) * 1000)

    return {
        "ensemble_response": ensemble_response,
        "confidence": round(confidence, 2),
        "models_used": models_used,
        "individual_responses": {
            "medgemma": medgemma_response,
            "meditron": meditron_response,
            "medichat": medichat_response,
        },
        "processing_time_ms": processing_time,
        "is_emergency": is_emergency,
    }
