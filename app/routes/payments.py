import httpx
from fastapi import APIRouter, HTTPException, Depends, Request
from app.config import settings
from app.middleware.auth import get_current_user
from app.database import execute
import hmac
import hashlib

router = APIRouter()

def get_razorpay_plan_id(plan_id: str, billing: str) -> str:
    plans = {
        "monthly": {
            "basic": settings.RAZORPAY_PLAN_BASIC_MONTHLY,
            "pro": settings.RAZORPAY_PLAN_PRO_MONTHLY,
            "medical_pro": settings.RAZORPAY_PLAN_MEDICAL_PRO_MONTHLY,
        },
        "yearly": {
            "basic": settings.RAZORPAY_PLAN_BASIC_YEARLY,
            "pro": settings.RAZORPAY_PLAN_PRO_YEARLY,
            "medical_pro": settings.RAZORPAY_PLAN_MEDICAL_PRO_YEARLY,
        }
    }
    return plans.get(billing, {}).get(plan_id)

@router.post("/create-subscription")
async def create_subscription(request: dict, current_user: dict = Depends(get_current_user)):
    plan_id = request.get("plan_id")
    billing = request.get("billing", "monthly")
    
    if not plan_id or plan_id not in ["basic", "pro", "medical_pro"]:
        raise HTTPException(status_code=400, detail="Invalid plan")
        
    if billing not in ["monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid billing cycle")
        
    rzp_plan_id = get_razorpay_plan_id(plan_id, billing)
    if not rzp_plan_id:
        raise HTTPException(status_code=400, detail="Plan mapping not found")

    auth = (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    
    payload = {
        "plan_id": rzp_plan_id,
        "total_count": 120,
        "customer_notify": 1,
        "notes": {
            "user_id": str(current_user["id"]),
            "plan": plan_id
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.razorpay.com/v1/subscriptions",
            json=payload,
            auth=auth
        )
        data = response.json()
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=data.get("error", {}).get("description", "Failed to create subscription"))
            
        return {
            "subscription_id": data["id"]
        }

@router.post("/verify-payment")
async def verify_payment(request: dict, current_user: dict = Depends(get_current_user)):
    razorpay_payment_id = request.get("razorpay_payment_id")
    razorpay_subscription_id = request.get("razorpay_subscription_id")
    razorpay_signature = request.get("razorpay_signature")
    
    if not razorpay_payment_id or not razorpay_subscription_id or not razorpay_signature:
        raise HTTPException(status_code=400, detail="Missing payment verification details")
        
    # Verify signature 
    msg = f"{razorpay_payment_id}|{razorpay_subscription_id}"
    expected_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        msg.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid payment signature")
        
    auth = (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.razorpay.com/v1/subscriptions/{razorpay_subscription_id}",
            auth=auth
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to fetch subscription details")
            
        sub_data = response.json()
        plan = sub_data.get("notes", {}).get("plan")
        
        if not plan:
            plan = request.get("plan_id")
            
        if not plan:
            raise HTTPException(status_code=400, detail="Could not determine plan")
            
        from app.services.user_service import update_user_plan
        await update_user_plan(current_user["id"], plan)

        # If they had a previous active subscription, this creates a new one. Update DB.
        # Ensure we add razorpay_subscription_id as well
        await execute(
            """INSERT INTO subscriptions (user_id, plan, razorpay_payment_id, status, started_at, razorpay_subscription_id)
               VALUES ($1, $2, $3, 'active', NOW(), $4)""",
            current_user["id"], plan, razorpay_payment_id, razorpay_subscription_id
        )
        
        return {"message": "Payment verified and plan updated successfully", "plan": plan}
