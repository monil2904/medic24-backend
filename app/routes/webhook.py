import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException
from app.config import settings
from app.database import execute

router = APIRouter()

@router.post("/webhook")
async def razorpay_webhook(request: Request):
    """Verify and process Razorpay payment webhooks."""
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    # Verify webhook signature
    expected = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload = await request.json()
    event = payload.get("event", "")

    if event in ["payment.captured", "subscription.activated"]:
        entity = payload.get("payload", {}).get(event.split(".")[0], {}).get("entity", {})
        payment_id = entity.get("id")
        notes = entity.get("notes", {})
        user_id = notes.get("user_id")
        plan = notes.get("plan")

        if user_id and plan:
            await execute("UPDATE users SET subscription_plan = $1 WHERE id = $2", plan, user_id)
            
            rzp_payment_id = payment_id if event == "payment.captured" else None
            rzp_sub_id = payment_id if event == "subscription.activated" else None
            
            await execute(
                """INSERT INTO subscriptions (user_id, plan, razorpay_payment_id, razorpay_subscription_id, status, started_at)
                   VALUES ($1, $2, $3, $4, 'active', NOW())""",
                user_id, plan, rzp_payment_id, rzp_sub_id
            )

    return {"status": "ok"}
