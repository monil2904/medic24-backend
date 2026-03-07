import asyncio
import time
from typing import Dict, Any

from app.models.medgemma import query as gemma_query
from app.models.meditron import query as meditron_query
from app.models.medichat import query as medichat_query

# Weights based on query type
WEIGHTS = {
    "clinical": {"medgemma": 0.45, "meditron": 0.30, "medichat": 0.25},
    "drug":     {"medgemma": 0.35, "meditron": 0.40, "medichat": 0.25},
    "symptom":  {"medgemma": 0.30, "meditron": 0.25, "medichat": 0.45},
    "general":  {"medgemma": 0.40, "meditron": 0.30, "medichat": 0.30}
}

async def ensemble_query(user_query: str, query_type: str = "general") -> Dict[str, Any]:
    start_time = time.time()
    
    # Run all 3 models in parallel to minimize latency
    results = await asyncio.gather(
        gemma_query(user_query),
        meditron_query(user_query),
        medichat_query(user_query),
        return_exceptions=True
    )

    gemma_res, meditron_res, medichat_res = results

    # Clean results: catch exceptions and nulls passed from the wrappers
    gemma_clean = gemma_res if isinstance(gemma_res, str) else None
    meditron_clean = meditron_res if isinstance(meditron_res, str) else None
    medichat_clean = medichat_res if isinstance(medichat_res, str) else None

    # Count successful responses to figure out our confidence & missing models
    successful_responses = []
    individual_responses = {}
    
    if gemma_clean:
        successful_responses.append("medgemma")
        individual_responses["medgemma"] = gemma_clean
    if meditron_clean:
        successful_responses.append("meditron")
        individual_responses["meditron"] = meditron_clean
    if medichat_clean:
        successful_responses.append("medichat")
        individual_responses["medichat"] = medichat_clean

    if len(successful_responses) == 3:
        confidence = 1.0
    elif len(successful_responses) == 2:
        confidence = 0.7
    elif len(successful_responses) == 1:
        confidence = 0.4
    else:
        confidence = 0.0

    # Build the merged response
    # Real-world blending might use another LLM call or advanced RAG routing.
    # Here, we format an ensemble-backed markdown representation based on what loaded perfectly.
    
    merged = ""
    if confidence == 0:
        merged = "I'm sorry, I'm currently unable to process your medical query. Please try again later or consult a professional."
    else:
        # We start with the primary output dictated by the 'best model' for that query type
        weights_for_type = WEIGHTS.get(query_type, WEIGHTS["general"])
        
        best_model = None
        best_weight = -1
        
        for model_name in successful_responses:
            if weights_for_type[model_name] > best_weight:
                best_weight = weights_for_type[model_name]
                best_model = model_name
                
        merged += f"### Primary AI Assessment\n{individual_responses[best_model]}\n\n"
        
        # Add supplementary insights from other models
        other_models = [m for m in successful_responses if m != best_model]
        if other_models:
            merged += "### Additional Perspectives given by Ensemble\n"
            for m in other_models:
                merged += f"**{m.capitalize()} Engine:**\n{individual_responses[m]}\n\n"
                
        merged += "\n---\n*Disclaimer: Med24 AI provides information for educational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult a healthcare provider."
        
    end_time = time.time()
    
    return {
        "ensemble_response": merged,
        "confidence": confidence,
        "models_used": successful_responses,
        "individual_responses": individual_responses,
        "processing_time_ms": int((end_time - start_time) * 1000)
    }
